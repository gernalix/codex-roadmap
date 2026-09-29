# Goal
Diagnostica cosa non va nella C2 live e risolvi il guasto con il minimo cambiamento necessario.

# Scope
- Autorita canonica: `/home/daniele/projects/codex-roadmap/roadmap.sqlite`, receipt C2, stato Git/runtime/systemd live.
- Segui `/home/daniele/projects/codex-roadmap/README.md` e `C2_EXECUTOR_CONTRACT.md`.
- Preserva worker, run e worktree gia attivi; non duplicare executor e non bypassare il single writer.
- Prima verifica mirata dello stato reale, poi correggi solo il failure domain dimostrato.
- Se emerge incidentalmente un problema distinto, catturalo nella C2 Inbox senza indagarlo.

# Acceptance
- causa concreta identificata con evidenza live;
- fix minimo applicato nel worktree/checkout assegnato e integrato tramite il percorso canonico;
- verifica mirata PASS sul comportamento guasto;
- servizi/runtime C2 necessari risultano operativi;
- receipt terminale C2 applicato.

# Stop
Termina subito dopo i gate PASS. Nessun audit, refactor o cleanup extra.
