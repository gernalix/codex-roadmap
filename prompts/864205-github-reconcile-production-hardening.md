PROMPT_ID=864205

# Goal
Rendere github-reconcile di /home/daniele/projects/github-autosync production-grade: recovery Git sicuro e bounded, elaborazione indipendente di tutti i repository, test integration con bare remotes temporanei, CLI umana concisa con --json, servizio systemd ogni minuto con lock, Push monitor Uptime Kuma reale.

# Vincoli
Preservare commit, staged/unstaged/untracked; vietati reset --hard, clean distruttivi, force push, scelta automatica di conflitti semantici. codex-roadmap usa sempre roadmap_pull.py e single writer. Scope github-autosync, test/systemd e configurazione minima Kuma. MegaVault STANDARD. PROMPT_ID fisso.

# Verifica
Test mirati, suite completa una volta, py_compile, installazione systemd e verifica timer/service/lock/semantica reboot, Kuma DB con monitor unico attivo e heartbeat UP, dry-run e run reale controllato, secondo run idempotente, CI PASS.

# Output
Report massimo 12 righe con PROMPT_ID=864205, risultato, Git hardening, test, CLI, systemd, Kuma, whatsapp-watcher class, idempotency, CI e commit.
