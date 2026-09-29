#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import Any

ROOT = Path.home() / ".local/share/c2-master-watcher"
STATE = ROOT / "state.json"
META = ROOT / "deterministic-meta.json"
HEARTBEAT = ROOT / "heartbeat.json"
ALERT_STATE = ROOT / "attention-alert.json"
ERROR_LOG = ROOT / "notification-error.log"
RUNTIME_DB = Path.home() / ".local/state/c2-supervisor/roadmap.sqlite3"
MASTER_PID = Path.home() / ".local/state/c2-master-goal/rpc-worker.pid"
NOTIFY = Path.home() / ".local/bin/c2-notify"
MASTER_SERVICE = "c2-master-goal.service"
MAX_START_FAILURES = 3
RETRY_DELAY_S = 60


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError, OSError):
        return False


def master_worker_alive() -> bool:
    try:
        return _pid_alive(int(MASTER_PID.read_text(encoding="utf-8").strip()))
    except Exception:
        return False


def systemd_state(name: str) -> dict[str, str]:
    env = os.environ.copy()
    uid = os.getuid()
    env.setdefault("XDG_RUNTIME_DIR", f"/run/user/{uid}")
    env.setdefault("DBUS_SESSION_BUS_ADDRESS", f"unix:path=/run/user/{uid}/bus")
    proc = subprocess.run(
        ["systemctl", "--user", "show", name, "--no-pager",
         "-p", "ActiveState", "-p", "SubState", "-p", "Result",
         "-p", "ExecMainStatus", "-p", "ExecMainCode"],
        text=True, capture_output=True, env=env, timeout=5,
    )
    if proc.returncode:
        return {"active": "unknown", "result": "unknown", "error": proc.stderr.strip()}
    values = {}
    for line in proc.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return {
        "active": values.get("ActiveState", "unknown"),
        "sub": values.get("SubState", "unknown"),
        "result": values.get("Result", "unknown"),
        "exec_status": values.get("ExecMainStatus", ""),
        "exec_code": values.get("ExecMainCode", ""),
    }


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE name=? LIMIT 1", (name,)
    ).fetchone() is not None


def db_snapshot(now: float | None = None) -> dict[str, Any]:
    now = time.time() if now is None else now
    if not RUNTIME_DB.exists():
        return {"available": False, "error": "runtime_db_missing"}
    try:
        conn = sqlite3.connect(f"file:{RUNTIME_DB}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        counts = {r["status"]: r["n"] for r in conn.execute(
            "SELECT status,COUNT(*) n FROM work_items GROUP BY status"
        )}
        inbox = conn.execute(
            "SELECT COUNT(*) FROM v_issue_inbox_pending_ordered"
        ).fetchone()[0] if _table_exists(conn, "issue_inbox") else 0
        runnable = [r[0] for r in conn.execute(
            "SELECT work_item_id FROM v_work_item_runnable ORDER BY work_item_id LIMIT 200"
        )]
        runs = []
        for row in conn.execute("""
            SELECT run_id,work_item_id,executor,state,worker_ref,lease_until
            FROM work_item_runs
            WHERE state IN ('claimed','running','recovering')
            ORDER BY created_at DESC LIMIT 100
        """):
            item = dict(row)
            item["lease_expired"] = float(item.get("lease_until") or 0) <= now
            runs.append(item)
        authority = None
        if _table_exists(conn, "c2_supervisor_authority"):
            row = conn.execute(
                "SELECT supervisor_id,lease_expires_at FROM c2_supervisor_authority WHERE singleton=1"
            ).fetchone()
            if row:
                expires = float(row[1] or 0)
                authority = {
                    "supervisor_id": row[0],
                    "lease_expires_at": expires,
                    "lease_valid": expires > now,
                    "lease_stale": now > expires + 120,
                }
        triage_run = None
        if _table_exists(conn, "work_item_tags"):
            row = conn.execute("""
                SELECT r.run_id,r.work_item_id,r.state,r.worker_ref,r.lease_until
                FROM work_items w
                JOIN work_item_tags t USING(work_item_id)
                JOIN work_item_runs r USING(work_item_id)
                WHERE t.tag='c2:issue-triage'
                  AND w.status NOT IN ('completed','failed','cancelled','superseded','waived')
                  AND r.state IN ('claimed','running','recovering')
                ORDER BY r.created_at DESC LIMIT 1
            """).fetchone()
            if row:
                triage_run = dict(row)
                triage_run["lease_expired"] = float(triage_run.get("lease_until") or 0) <= now
        triaged = None
        if _table_exists(conn, "issue_inbox"):
            row = conn.execute(
                "SELECT MAX(triaged_at_ms) FROM issue_inbox WHERE triaged_at_ms IS NOT NULL"
            ).fetchone()
            triaged = row[0] if row else None
        conn.close()
        return {
            "available": True, "counts": counts, "inbox_pending": int(inbox),
            "runnable_ids": runnable, "active_runs": runs,
            "authority": authority, "triage_run": triage_run,
            "last_triaged_at_ms": triaged,
        }
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}:{exc}"}


def _bucket(value: int, size: int) -> int:
    if value <= 0:
        return 0
    return 1 + (value - 1) // size


def state_fingerprint(db: dict[str, Any]) -> str:
    counts = db.get("counts") or {}
    runs = db.get("active_runs") or []
    authority = db.get("authority") or {}
    triage = db.get("triage_run") or {}
    if int(db.get("inbox_pending") or 0) > 0 and triage:
        core = {
            "mode": "triage_gate",
            "inbox_nonempty": True,
            "triage_run": (
                triage.get("run_id"), triage.get("state"),
                bool(triage.get("worker_ref")), bool(triage.get("lease_expired")),
            ),
            "authority": (
                authority.get("supervisor_id"), bool(authority.get("lease_stale")),
            ),
        }
    else:
        core = {
            "mode": "general",
            "inbox_nonempty": bool(int(db.get("inbox_pending") or 0)),
            "pending_bucket": _bucket(int(counts.get("pending") or 0), 10),
            "waiting_bucket": _bucket(int(counts.get("waiting") or 0), 5),
            "blocked_bucket": _bucket(int(counts.get("blocked") or 0), 5),
            "runnable_ids": list(db.get("runnable_ids") or []),
            "runs": [
                (r.get("run_id"), r.get("state"), bool(r.get("worker_ref")), bool(r.get("lease_expired")))
                for r in runs
            ],
            "authority": (authority.get("supervisor_id"), bool(authority.get("lease_stale"))),
        }
    raw = json.dumps(core, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def delegated_worker_state(db: dict[str, Any], now: float | None = None) -> dict[str, Any]:
    now = time.time() if now is None else now
    triage = db.get("triage_run") or {}
    run_id = str(triage.get("run_id") or "")
    worker_ref = str(triage.get("worker_ref") or "")
    out = {
        "run_id": run_id or None,
        "worker_ref": worker_ref or None,
        "alive": False,
        "progressing": False,
        "progress_age_s": None,
        "unit": None,
        "unit_state": "inactive",
    }
    if not run_id or worker_ref != "c2-run:" + run_id:
        return out
    unit = "c2-run-" + run_id + ".service"
    state = systemd_state(unit)
    out["unit"] = unit
    out["unit_state"] = state.get("active", "unknown")
    out["alive"] = state.get("active") == "active"
    last = db.get("last_triaged_at_ms")
    if last:
        try:
            out["progress_age_s"] = max(0.0, now - float(last) / 1000.0)
        except Exception:
            pass
    out["progressing"] = bool(out["alive"] and (
        out["progress_age_s"] is None or out["progress_age_s"] <= 3600
    ))
    return out


def work_remains(db: dict[str, Any]) -> bool:
    counts = db.get("counts") or {}
    live = sum(int(counts.get(s) or 0) for s in (
        "pending", "waiting", "blocked", "claimed", "running", "recovering", "unknown"
    ))
    return bool(int(db.get("inbox_pending") or 0) or live or db.get("runnable_ids") or db.get("active_runs"))


def decide(snapshot: dict[str, Any], meta: dict[str, Any], now: float | None = None) -> dict[str, Any]:
    now = time.time() if now is None else now
    db = snapshot.get("db") or {}
    service = snapshot.get("service") or {}
    if not db.get("available"):
        return {
            "status": "needs_user", "phase": "unknown",
            "headline": "C2 non riesce a leggere lo stato runtime",
            "current": f"Database runtime non disponibile: {db.get('error', 'errore sconosciuto')}.",
            "next": "Apri ChatGPT per diagnosticare il runtime C2.",
            "intervention": "Chiedimi di diagnosticare il runtime C2.",
            "attention_key": "c2_runtime_db_unavailable", "should_start_goal": False,
            "why": ["Il watchdog non può verificare il control plane senza il database runtime."],
        }
    fp = state_fingerprint(db)
    if not work_remains(db):
        return {
            "status": "globally_quiescent", "phase": "external_wait",
            "headline": "C2 è in quiescenza globale",
            "current": "Non risultano attività C2 non terminali, run attivi o Inbox pendente.",
            "next": "Il watchdog attenderà un cambiamento reale di stato.",
            "intervention": "", "attention_key": "", "should_start_goal": False,
            "why": ["Nessun lavoro autonomo risulta dal control plane locale."], "state_key": fp,
        }
    delegated = snapshot.get("delegated_worker") or {}
    if delegated.get("alive"):
        progress = delegated.get("progress_age_s")
        progress_text = (
            " avanzamento Inbox recente" if progress is not None and progress <= 3600
            else " worker systemd vivo"
        )
        return {
            "status": "working", "phase": "delegated",
            "headline": "Lavoro delegato C2 in corso",
            "current": ("Il Master Goal può restare PAUSED per design: il worker canonico "
                        f"{delegated.get('run_id')} è vivo;{progress_text}."),
            "next": "Il runtime continuerà i batch e farà recovery solo se il worker termina o il run resta senza esecutore vivo.",
            "intervention": "", "attention_key": "", "should_start_goal": False,
            "why": ["Il worker delegato systemd è attivo; una lease scaduta da sola non equivale a stallo."],
            "state_key": fp,
        }
    if service.get("active") == "active" or snapshot.get("master_worker_alive"):
        return {
            "status": "working", "phase": "executing",
            "headline": "Il Master Goal è attivo",
            "current": "Il coordinatore C2 è in esecuzione; il watchdog osserva soltanto fatti locali.",
            "next": "Attendere il prossimo cambiamento reale del control plane.",
            "intervention": "", "attention_key": "", "should_start_goal": False,
            "why": ["Il servizio Master Goal o il suo worker risultano attivi."], "state_key": fp,
        }
    failures = int(meta.get("start_failures") or 0)
    last_fp = str(meta.get("last_wake_fingerprint") or "")
    last_wake = float(meta.get("last_wake_at") or 0)
    failed_service = service.get("result") not in ("success", "", "unknown")
    changed = fp != last_fp
    retry_due = failed_service and failures < MAX_START_FAILURES and now - last_wake >= RETRY_DELAY_S
    if changed or retry_due:
        reason = "Lo stato C2 è cambiato" if changed else "Il precedente avvio del Goal è fallito"
        return {
            "status": "recovering", "phase": "inbox",
            "headline": "Il watchdog sta riattivando il Master Goal",
            "current": f"{reason}; è consentito un nuovo avvio deterministico.",
            "next": "Avviare una sola volta il Goal e poi attendere un nuovo cambiamento di stato.",
            "intervention": "", "attention_key": "", "should_start_goal": True,
            "why": [reason, "Lo stesso fingerprint non viene rilanciato in loop."], "state_key": fp,
        }
    if failed_service and failures >= MAX_START_FAILURES:
        return {
            "status": "needs_user", "phase": "unknown",
            "headline": "Il Master Goal non riparte dopo i tentativi automatici",
            "current": f"Il servizio ha fallito {failures} tentativi sullo stesso stato C2.",
            "next": "Serve una diagnosi interattiva tramite ChatGPT/RDC.",
            "intervention": "Chiedimi di diagnosticare il Master Goal C2.",
            "attention_key": "master_goal_recovery_failed", "should_start_goal": False,
            "why": ["I tentativi automatici sono esauriti senza un avvio riuscito."], "state_key": fp,
        }
    return {
        "status": "waiting_external", "phase": "external_wait",
        "headline": "C2 attende un cambiamento reale prima di riattivare il Goal",
        "current": "Il Goal ha già controllato questo identico stato; non verrà richiamato per fare polling semantico.",
        "next": "Un cambiamento di Inbox, run, lease, runnable o ownership riattiverà automaticamente il Goal.",
        "intervention": "", "attention_key": "", "should_start_goal": False,
        "why": ["Il fingerprint del control plane è invariato dall'ultimo avvio riuscito."], "state_key": fp,
    }


def start_goal() -> tuple[bool, str]:
    env = os.environ.copy()
    uid = os.getuid()
    env.setdefault("XDG_RUNTIME_DIR", f"/run/user/{uid}")
    env.setdefault("DBUS_SESSION_BUS_ADDRESS", f"unix:path=/run/user/{uid}/bus")
    proc = subprocess.run(
        ["systemctl", "--user", "start", MASTER_SERVICE],
        text=True, capture_output=True, env=env, timeout=15,
    )
    detail = (proc.stderr or proc.stdout or "").strip()
    return proc.returncode == 0, detail[-600:]


def _log_notify_error(channel: str, exc: Exception) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    with ERROR_LOG.open("a", encoding="utf-8") as handle:
        handle.write(f"{time.time()} {channel}: {type(exc).__name__}: {exc}\n")


def _send(title: str, message: str, urgency: str = "normal") -> None:
    title = " ".join(title.split())[:180]
    message = " ".join(message.split())[:1200]
    try:
        subprocess.run([str(NOTIFY), title, message], text=True, capture_output=True,
                       timeout=30, check=True)
    except Exception as exc:
        _log_notify_error("telegram", exc)
    try:
        subprocess.run(["notify-send", "--app-name", "C2 Master Watchdog",
                        "--urgency", urgency, title, message], text=True,
                       capture_output=True, timeout=10, check=True)
    except Exception as exc:
        _log_notify_error("fedora", exc)


def attention_transition(result: dict[str, Any], alert: dict[str, Any], goal_alive: bool) -> tuple[str | None, dict[str, Any]]:
    active = bool(alert.get("active"))
    key = str(result.get("attention_key") or "")
    if result.get("status") == "needs_user" and key:
        if not active or alert.get("attention_key") != key:
            return "attention", {
                "active": True, "attention_key": key,
                "headline": result.get("headline") or "C2 richiede attenzione",
                "intervention": result.get("intervention") or "Apri ChatGPT per i dettagli.",
                "notified_at": time.time(),
            }
        return None, alert
    if active and goal_alive and result.get("status") in ("working", "recovering"):
        return "resolved", {
            "active": False, "attention_key": "", "resolved_at": time.time(),
            "previous": alert, "current_headline": result.get("headline") or "Master Goal ripartito",
        }
    return None, alert


def apply_notification(result: dict[str, Any], goal_alive: bool) -> None:
    alert = read_json(ALERT_STATE, {})
    event, updated = attention_transition(result, alert, goal_alive)
    if event == "attention":
        _send("C2 Goal - intervento richiesto",
              f"{updated['headline']} Azione richiesta: {updated['intervention']}", "critical")
    elif event == "resolved":
        old = (alert.get("headline") or "Problema precedente").strip()
        current = (updated.get("current_headline") or "Il Goal ha ripreso il lavoro").strip()
        _send("C2 Goal - problema risolto, lavoro ripartito", f"Risolto: {old}. Ora: {current}")
    if event:
        ALERT_STATE.write_text(json.dumps(updated, indent=2, ensure_ascii=False), encoding="utf-8")


def snapshot(now: float | None = None) -> dict[str, Any]:
    now = time.time() if now is None else now
    db = db_snapshot(now)
    return {
        "observed_at": now,
        "db": db,
        "service": systemd_state(MASTER_SERVICE),
        "master_worker_alive": master_worker_alive(),
        "delegated_worker": delegated_worker_state(db, now),
    }


def write_state(result: dict[str, Any], fingerprint: str, wake_result: str | None = None) -> None:
    payload = dict(result)
    payload.update({
        "confidence": "high",
        "should_wake_goal": bool(result.get("should_start_goal")),
        "escalate_to_sol": False,
        "discoveries": [],
        "wake_result": wake_result or "not_needed",
        "analyzed_at": time.time(),
        "state_key": fingerprint,
        "decision_source": "deterministic",
    })
    payload.pop("should_start_goal", None)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(STATE)


def run_once(now: float | None = None) -> int:
    now = time.time() if now is None else now
    ROOT.mkdir(parents=True, exist_ok=True)
    snap = snapshot(now)
    meta = read_json(META, {})
    result = decide(snap, meta, now)
    fp = result.get("state_key") or state_fingerprint(snap.get("db") or {}) if (snap.get("db") or {}).get("available") else "db-unavailable"
    wake_result = None
    if result.get("should_start_goal"):
        ok, detail = start_goal()
        wake_result = "started" if ok else "start_failed"
        meta["last_wake_fingerprint"] = fp
        meta["last_wake_at"] = now
        if ok:
            meta["start_failures"] = 0
        else:
            meta["start_failures"] = int(meta.get("start_failures") or 0) + 1
            if meta["start_failures"] >= MAX_START_FAILURES:
                result = {
                    **result,
                    "status": "needs_user", "phase": "unknown",
                    "headline": "Il Master Goal non può essere riavviato automaticamente",
                    "current": f"systemd ha rifiutato l'avvio per {meta['start_failures']} tentativi. {detail}",
                    "next": "Serve una diagnosi interattiva tramite ChatGPT/RDC.",
                    "intervention": "Chiedimi di diagnosticare il Master Goal C2.",
                    "attention_key": "master_goal_start_failed",
                    "should_start_goal": False,
                    "why": ["Il comando systemd di recovery continua a fallire."],
                }
        META.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    post_delegated = delegated_worker_state(snap.get("db") or {}, time.time())
    goal_alive = master_worker_alive() or systemd_state(MASTER_SERVICE).get("active") == "active"
    apply_notification(result, goal_alive or bool(post_delegated.get("alive")))
    write_state(result, fp, wake_result)
    HEARTBEAT.write_text(json.dumps({
        "checked_at": time.time(), "analyzed": False,
        "state_key": fp, "master_worker_alive": goal_alive,
        "delegated_worker_alive": bool(post_delegated.get("alive")),
        "delegated_worker_progressing": bool(post_delegated.get("progressing")),
        "delegated_run_id": post_delegated.get("run_id"),
        "delegated_progress_age_s": post_delegated.get("progress_age_s"),
        "decision_source": "deterministic",
    }, indent=2), encoding="utf-8")
    return 0


def main() -> int:
    try:
        return run_once()
    except Exception as exc:
        ROOT.mkdir(parents=True, exist_ok=True)
        (ROOT / "last-error.txt").write_text(
            f"{time.time()} {type(exc).__name__}: {exc}\n", encoding="utf-8"
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
