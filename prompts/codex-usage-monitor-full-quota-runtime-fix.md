[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=184639 | project_id=8 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST | type=Prompt`

# Goal
Chiudi SOLO la regressione residua di `gernalix/codex-usage-monitor`: finché `weekly_remaining` resta 100, `Codex weekly quota changed` deve essere sempre NO-OP qualunque metadata (`weekly_reset`, `usage_limit_resets_available`) cambi; la prima discesa reale sotto 100 deve notificare. Verifica poi che il runtime Fedora locale usi il fix.

# Starting point autoritativo
Remote `main` contiene il fix Codex `fe41a614` e il regression test `tests/test_quota_notification_policy.py` (commit `d4fb4aeb`), dove `test_full_quota_ignores_metadata_churn` è marcato `expectedFailure` perché l'implementazione attuale ignora solo `weekly_reset`. Il progetto è stdlib-only: NON provare `pytest`; runner canonico per questo task = `python -m unittest`.

# Esegui
1. Nel checkout `/home/daniele/projects/codex-usage-monitor`: `git status --short --branch`; se pulito, un solo `git pull --ff-only origin main`; se modifiche locali incompatibili => BLOCKED, niente stash/reset/force. Non leggere MegaVault/README salvo blocker concreto.
2. Modifica SOLO `quota_change_is_noop`: dopo il parsing numerico, restituisci `True` se e solo se precedente e corrente hanno entrambi `weekly_remaining == 100.0`; altrimenti `False`. Elimina il confronto dei metadata. Nessun refactor.
3. Rimuovi SOLO `@unittest.expectedFailure` dal regression test preparato. Non duplicare i test A-E già presenti.
4. Esegui una sola volta: `python -m unittest tests.test_quota_notification_policy tests.test_parsing`. PASS richiesto; i `ResourceWarning` SQLite già noti e non fatal non vanno investigati in questo task.
5. Commit/push solo questi cambi. Poi verifica il runtime Fedora locale: unit/timer `codex-usage-monitor` devono puntare al checkout/runtime atteso e risultare sani. Esegui al massimo un'acquisizione con notifiche in dry-run se serve a verificare il percorso; NON inviare Telegram reali e non aspettare polling futuri. Se il timer esegue lo script dal checkout aggiornato, non fare restart inutile.

# Stop
PASS = helper generalizzato + expectedFailure rimosso + unit test mirati PASS + commit pushato + runtime/timer Fedora confermato sul codice aggiornato. Nessun audit generale, pytest/installazioni, cleanup, refactor, test suite completa, VM Oracle o Telegram reale.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 184639 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 184639`
Poi STOP.

Output ≤6 righe: RESULT, SHA, test, runtime/timer, Telegram=dry-run/not-sent, blocker.
