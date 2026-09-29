# C2 Master deterministic watchdog

The Master watchdog is deliberately non-semantic. It does not call Codex, Luna, Sol, or any other model on a timer.

## Responsibilities

- Read objective local control-plane facts from the C2 runtime DB and systemd.
- Detect whether the Master Goal service/worker is active.
- Compute a stable fingerprint from Inbox size bands, lifecycle counts, runnable IDs, active runs, lease state, supervisor ownership and the latest Inbox triage timestamp.
- Start the Master Goal once when that fingerprint materially changes and autonomous work remains.
- Avoid re-starting the Goal for an unchanged fingerprint after a successful check.
- Retry a genuine systemd start failure a bounded number of times.
- Send Telegram + Fedora notifications only after automatic recovery is exhausted and human action is required.
- Send a recovery notification when an active human-attention incident clears and the Goal is running again.

## Non-responsibilities

- Semantic interpretation of roadmap content.
- Reconciliation decisions, task classification or prioritization.
- Model-driven polling or repeated "still blocked" turns.
- Creating C2 discoveries/issues from speculative interpretation.

Semantic diagnosis belongs to ChatGPT using RDC when a human-attention alert is raised or when the user explicitly asks for inspection.
