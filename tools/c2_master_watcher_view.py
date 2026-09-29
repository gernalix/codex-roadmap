#!/usr/bin/env python3
"""Human-readable live view of the deterministic C2 watchdog."""
import json
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path.home() / ".local/share/c2-master-watcher"
STATE = ROOT / "state.json"
HEARTBEAT = ROOT / "heartbeat.json"
ALERT = ROOT / "attention-alert.json"
DB = Path.home() / ".local/state/c2-supervisor/roadmap.sqlite3"
ENTER = "\033[?1049h\033[3J\033[2J\033[H"
EXIT = "\033[?1049l"


def load(path, default):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def service(name):
    try:
        result = subprocess.run(
            ["systemctl", "--user", "is-active", name],
            text=True, capture_output=True, timeout=2,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def inbox_count():
    try:
        conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        value = conn.execute(
            "select count(*) from v_issue_inbox_pending_ordered"
        ).fetchone()[0]
        conn.close()
        return int(value)
    except Exception:
        return None


def fmt_progress(seconds):
    if seconds is None:
        return "recente"
    seconds = max(0, float(seconds))
    if seconds < 60:
        return "meno di un minuto fa"
    if seconds < 3600:
        return f"{int(seconds // 60)} min fa"
    return f"{int(seconds // 3600)} h fa"


def render():
    state = load(STATE, {})
    heartbeat = load(HEARTBEAT, {})
    alert = load(ALERT, {})
    status = state.get("status")
    phase = state.get("phase")
    worker_alive = bool(heartbeat.get("delegated_worker_alive"))
    progressing = bool(heartbeat.get("delegated_worker_progressing"))
    progress_age = heartbeat.get("delegated_progress_age_s")
    inbox = inbox_count()
    master = service("c2-master-goal.service")
    timer = service("c2-master-watcher.timer")

    if status == "working" and phase == "delegated" and worker_alive and progressing:
        headline = "✅ C2 È SANO"
        what = (
            "Il worker delegato sta elaborando l'Inbox C2"
            + (f" ({inbox} elementi pendenti)." if inbox is not None else ".")
            + f" Ultimo avanzamento: {fmt_progress(progress_age)}."
        )
        goal = "Il Master Goal è in pausa intenzionalmente: non serve mentre il worker avanza."
        automatic = [
            "Lascio il Goal fermo finché il worker continua ad avanzare.",
            "Se il worker muore o non avanza per 60 minuti, riattivo il Goal per il recovery.",
            "Se il recovery fallisce ripetutamente, ti avviso su Fedora e Telegram.",
        ]
        intervention = "Nessuno."
    elif status == "recovering":
        headline = "🟡 RECOVERY AUTOMATICO IN CORSO"
        what = state.get("current") or "Il watchdog ha rilevato un cambiamento che richiede recovery."
        goal = "Il Master Goal viene riattivato solo per gestire questo cambiamento reale."
        automatic = ["Attendo l'esito del recovery e torno in osservazione se riesce."]
        intervention = "Nessuno, per ora."
    elif status == "needs_user":
        headline = "🔴 SERVE IL TUO INTERVENTO"
        what = state.get("current") or "Il recovery automatico non è riuscito."
        goal = "Il watchdog non può risolvere automaticamente questo stato."
        automatic = ["Le notifiche restano attive finché il problema non viene risolto."]
        intervention = state.get("intervention") or "Chiedimi di diagnosticare C2."
    elif status == "globally_quiescent":
        headline = "✅ C2 È A RIPOSO"
        what = "Non risulta lavoro C2 autonomo da eseguire."
        goal = "Il Master Goal resta fermo finché non compare nuovo lavoro."
        automatic = ["Il watchdog continua a controllare senza chiamare modelli AI."]
        intervention = "Nessuno."
    elif status == "waiting_external":
        headline = "🔵 C2 È IN ATTESA"
        what = state.get("current") or "C2 aspetta un cambiamento esterno verificabile."
        goal = "Il Master Goal resta fermo finché quel cambiamento non avviene."
        automatic = ["Il watchdog riprenderà automaticamente quando lo stato cambia."]
        intervention = "Nessuno."
    else:
        headline = "🟠 STATO C2 DA VERIFICARE"
        what = state.get("current") or "Il watchdog non ha ancora classificato chiaramente lo stato."
        goal = (
            "Master Goal attivo." if master == "active"
            else "Master Goal inattivo."
        )
        automatic = ["Il watchdog continua i controlli deterministici."]
        intervention = state.get("intervention") or "Nessuno."

    lines = [
        "C2 WATCHDOG",
        "=" * 72,
        headline,
        "",
        "COSA STA SUCCEDENDO",
        what,
        "",
        "MASTER GOAL",
        goal,
        "",
        "COSA FARÀ DA SOLO",
    ]
    lines.extend("• " + item for item in automatic)
    lines += [
        "",
        "DEVI FARE QUALCOSA?",
        intervention,
        "",
        "DIAGNOSTICA ESSENZIALE",
        f"Watchdog: {timer} · Master Goal: {master} · "
        f"worker delegato: {'attivo' if worker_alive else 'non attivo'} · "
        f"progresso: {'sì' if progressing else 'no'}",
    ]
    if alert.get("active"):
        lines.append("Allarme umano: ATTIVO")
    return "\n".join(lines)


def main():
    sys.stdout.write(ENTER)
    sys.stdout.flush()
    previous = None
    try:
        while True:
            current = render()
            if current != previous:
                sys.stdout.write("\033[2J\033[H" + current + "\n")
                sys.stdout.flush()
                previous = current
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(EXIT)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
