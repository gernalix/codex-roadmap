#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import queue
import sqlite3
import subprocess
import tempfile
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_DB = Path.home() / ".local" / "share" / "c2-codex-human" / "viewer.sqlite3"
DEFAULT_MODEL = "gpt-5.6-terra"
DEFAULT_REASONING = "medium"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def message_hash(session_id: str, timestamp: str, text: str) -> str:
    return hashlib.sha256(f"{session_id}\0{timestamp}\0{text}".encode()).hexdigest()


def bundle_hash(mode: str, message_ids: Iterable[str]) -> str:
    payload = mode + "\0" + "\0".join(message_ids)
    return hashlib.sha256(payload.encode()).hexdigest()


class ViewerDB:
    def __init__(self, path: Path = DEFAULT_DB):
        self.path = path.expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.Lock()
        self._install()

    def _install(self) -> None:
        with self.lock, self.conn:
            self.conn.executescript("""
            PRAGMA journal_mode=WAL;
            PRAGMA foreign_keys=ON;
            CREATE TABLE IF NOT EXISTS sessions(
              session_id TEXT PRIMARY KEY,
              source_path TEXT NOT NULL,
              first_seen_at TEXT NOT NULL,
              last_seen_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages(
              message_id TEXT PRIMARY KEY,
              session_id TEXT NOT NULL REFERENCES sessions(session_id),
              timestamp TEXT NOT NULL,
              text TEXT NOT NULL,
              ingested_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_messages_session_time
              ON messages(session_id,timestamp);
            CREATE TABLE IF NOT EXISTS ai_runs(
              ai_run_id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id TEXT NOT NULL REFERENCES sessions(session_id),
              mode TEXT NOT NULL,
              bundle_hash TEXT NOT NULL,
              selected_message_ids_json TEXT NOT NULL,
              request_text TEXT NOT NULL,
              response_text TEXT,
              model TEXT NOT NULL,
              reasoning TEXT NOT NULL,
              status TEXT NOT NULL,
              created_at TEXT NOT NULL,
              completed_at TEXT,
              error TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_ai_runs_bundle
              ON ai_runs(session_id,bundle_hash,status);
            CREATE TABLE IF NOT EXISTS companion_state(
              session_id TEXT PRIMARY KEY REFERENCES sessions(session_id),
              summary TEXT NOT NULL DEFAULT '',
              last_message_id TEXT,
              enabled INTEGER NOT NULL DEFAULT 0,
              updated_at TEXT NOT NULL
            );
            """)

    def ensure_session(self, session_id: str, source_path: str) -> None:
        now = utc_now()
        with self.lock, self.conn:
            self.conn.execute("""
              INSERT INTO sessions(session_id,source_path,first_seen_at,last_seen_at)
              VALUES(?,?,?,?)
              ON CONFLICT(session_id) DO UPDATE SET
                source_path=excluded.source_path,last_seen_at=excluded.last_seen_at
            """, (session_id, source_path, now, now))

    def save_message(self, session_id: str, timestamp: str, text: str) -> str:
        mid = message_hash(session_id, timestamp, text)
        with self.lock, self.conn:
            self.conn.execute("""
              INSERT OR IGNORE INTO messages(message_id,session_id,timestamp,text,ingested_at)
              VALUES(?,?,?,?,?)
            """, (mid, session_id, timestamp, text, utc_now()))
            self.conn.execute("UPDATE sessions SET last_seen_at=? WHERE session_id=?", (utc_now(), session_id))
        return mid

    def messages(self, session_id: str) -> list[sqlite3.Row]:
        with self.lock:
            return list(self.conn.execute(
                "SELECT * FROM messages WHERE session_id=? ORDER BY timestamp,message_id",
                (session_id,),
            ))

    def cached_response(self, session_id: str, bhash: str) -> str | None:
        with self.lock:
            row = self.conn.execute("""
              SELECT response_text FROM ai_runs
              WHERE session_id=? AND bundle_hash=? AND status='done'
              ORDER BY ai_run_id DESC LIMIT 1
            """, (session_id, bhash)).fetchone()
        return str(row[0]) if row and row[0] else None

    def start_ai_run(self, session_id: str, mode: str, bhash: str, ids: list[str],
                     request_text: str, model: str, reasoning: str) -> int:
        with self.lock, self.conn:
            cur = self.conn.execute("""
              INSERT INTO ai_runs(
                session_id,mode,bundle_hash,selected_message_ids_json,request_text,
                model,reasoning,status,created_at
              ) VALUES(?,?,?,?,?,?,?,'running',?)
            """, (session_id, mode, bhash, json.dumps(ids), request_text, model, reasoning, utc_now()))
            return int(cur.lastrowid)

    def finish_ai_run(self, run_id: int, response: str) -> None:
        with self.lock, self.conn:
            self.conn.execute("""
              UPDATE ai_runs SET response_text=?,status='done',completed_at=? WHERE ai_run_id=?
            """, (response, utc_now(), run_id))

    def fail_ai_run(self, run_id: int, error: str) -> None:
        with self.lock, self.conn:
            self.conn.execute("""
              UPDATE ai_runs SET status='failed',error=?,completed_at=? WHERE ai_run_id=?
            """, (error, utc_now(), run_id))

    def get_companion(self, session_id: str) -> tuple[bool, str, str | None]:
        with self.lock:
            row = self.conn.execute(
                "SELECT enabled,summary,last_message_id FROM companion_state WHERE session_id=?",
                (session_id,),
            ).fetchone()
        if not row:
            return False, "", None
        return bool(row["enabled"]), str(row["summary"] or ""), row["last_message_id"]

    def set_companion(self, session_id: str, *, enabled: bool | None = None,
                      summary: str | None = None, last_message_id: str | None = None) -> None:
        current_enabled, current_summary, current_last = self.get_companion(session_id)
        with self.lock, self.conn:
            self.conn.execute("""
              INSERT INTO companion_state(session_id,summary,last_message_id,enabled,updated_at)
              VALUES(?,?,?,?,?)
              ON CONFLICT(session_id) DO UPDATE SET
                summary=excluded.summary,last_message_id=excluded.last_message_id,
                enabled=excluded.enabled,updated_at=excluded.updated_at
            """, (
                session_id,
                current_summary if summary is None else summary,
                current_last if last_message_id is None else last_message_id,
                int(current_enabled if enabled is None else enabled),
                utc_now(),
            ))


def build_explain_prompt(mode: str, selected: list[dict], nearby: list[dict]) -> str:
    selected_text = "\n\n".join(
        f"[SELECTED {i+1} | {m['timestamp']}]\n{m['text']}" for i, m in enumerate(selected)
    )
    nearby_text = "\n\n".join(
        f"[CONTEXT | {m['timestamp']}]\n{m['text']}" for m in nearby
    )
    scope = {
        "single": "Spiega il singolo aggiornamento selezionato.",
        "multi": "Spiega insieme gli aggiornamenti selezionati, evidenziando il filo comune.",
        "all": "Fornisci una lettura organica dell'intera transcript filtrata della sessione.",
    }.get(mode, "Spiega gli aggiornamenti selezionati.")
    return f"""Sei un companion interpretativo per una sessione Codex.
Usa ESCLUSIVAMENTE il testo incluso qui sotto. Non usare tool, filesystem, web, memoria esterna o supposizioni non supportate.
Rispondi in italiano, in modo concreto e comprensibile a una persona che conosce il progetto ma non i dettagli implementativi.
{scope}

Copri, quando applicabile:
- cosa sta succedendo;
- perché sta succedendo;
- background necessario per capire i termini;
- relazione tra i vari messaggi;
- conseguenze pratiche;
- stato attuale e prossimo passo atteso;
- eventuali punti che non possono essere verificati dai soli messaggi.

MESSAGGI SELEZIONATI
{selected_text}

CONTESTO VICINO
{nearby_text}
"""


def build_companion_prompt(previous_summary: str, new_messages: list[dict]) -> str:
    incoming = "\n\n".join(
        f"[{m['timestamp']}]\n{m['text']}" for m in new_messages
    )
    return f"""Sei un companion live che interpreta una transcript filtrata di Codex.
Usa SOLO il contenuto fornito qui. Non usare tool, filesystem, web o altre fonti.
Aggiorna una spiegazione compatta e cumulativa della sessione in italiano.
Non limitarti a parafrasare: chiarisci nessi causali, cosa sta facendo Codex, perché, cosa è risolto, cosa resta e il prossimo passo.
Se una conclusione non è verificabile dai messaggi, dichiaralo brevemente.

STATO INTERPRETATIVO PRECEDENTE
{previous_summary or "(nessuno: inizializza dallo storico ricevuto)"}

NUOVI MESSAGGI
{incoming}

Restituisci solo il nuovo stato interpretativo, con queste sezioni:
Obiettivo
Cosa sta succedendo
Perché
Decisioni / problemi emersi
Stato attuale
Prossimo passo atteso
"""


def run_codex(prompt: str, *, model: str = DEFAULT_MODEL, reasoning: str = DEFAULT_REASONING,
              timeout: int = 240) -> str:
    with tempfile.TemporaryDirectory(prefix="c2-codex-human-ai-") as tmp:
        out = Path(tmp) / "answer.txt"
        cmd = [
            str(Path.home() / ".local" / "bin" / "codex"),
            "exec",
            "--ephemeral",
            "--skip-git-repo-check",
            "--ignore-rules",
            "-C", tmp,
            "-s", "read-only",
            "-m", model,
            "-c", f'model_reasoning_effort="{reasoning}"',
            "-o", str(out),
            "-",
        ]
        proc = subprocess.run(
            cmd, input=prompt, text=True, stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE, timeout=timeout,
        )
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or f"codex exit {proc.returncode}")[-1200:])
        if not out.exists():
            raise RuntimeError("codex did not produce an answer")
        answer = out.read_text(encoding="utf-8").strip()
        if not answer:
            raise RuntimeError("empty AI response")
        return answer


@dataclass
class AIResult:
    request_id: str
    mode: str
    response: str | None
    error: str | None
    from_cache: bool = False
    selected_ids: list[str] | None = None


class AIWorker:
    def __init__(self, db: ViewerDB, session_id: str, *,
                 model: str = DEFAULT_MODEL, reasoning: str = DEFAULT_REASONING):
        self.db = db
        self.session_id = session_id
        self.model = model
        self.reasoning = reasoning
        self.requests: queue.Queue[dict] = queue.Queue()
        self.results: queue.Queue[AIResult] = queue.Queue()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def submit_explain(self, *, request_id: str, mode: str, selected: list[dict],
                       nearby: list[dict]) -> None:
        ids = [str(m["message_id"]) for m in selected]
        bhash = bundle_hash(mode, ids)
        cached = self.db.cached_response(self.session_id, bhash)
        if cached is not None:
            self.results.put(AIResult(request_id, mode, cached, None, True, ids))
            return
        prompt = build_explain_prompt(mode, selected, nearby)
        self.requests.put({
            "request_id": request_id, "mode": mode, "ids": ids,
            "bhash": bhash, "prompt": prompt,
        })

    def submit_companion(self, *, request_id: str, previous_summary: str,
                         new_messages: list[dict]) -> None:
        ids = [str(m["message_id"]) for m in new_messages]
        prompt = build_companion_prompt(previous_summary, new_messages)
        self.requests.put({
            "request_id": request_id, "mode": "companion", "ids": ids,
            "bhash": bundle_hash("companion", ids + [hashlib.sha256(previous_summary.encode()).hexdigest()]),
            "prompt": prompt,
        })

    def _loop(self) -> None:
        while True:
            req = self.requests.get()
            run_id = self.db.start_ai_run(
                self.session_id, req["mode"], req["bhash"], req["ids"],
                req["prompt"], self.model, self.reasoning,
            )
            try:
                response = run_codex(req["prompt"], model=self.model, reasoning=self.reasoning)
                self.db.finish_ai_run(run_id, response)
                self.results.put(AIResult(
                    req["request_id"], req["mode"], response, None, False, req["ids"]
                ))
            except Exception as exc:
                self.db.fail_ai_run(run_id, str(exc))
                self.results.put(AIResult(
                    req["request_id"], req["mode"], None, str(exc), False, req["ids"]
                ))
            finally:
                self.requests.task_done()
