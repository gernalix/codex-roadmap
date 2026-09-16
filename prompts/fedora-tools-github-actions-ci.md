[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=539590 | project_id=23 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
CI sandboxabile solo per i tool Fedora candidati alla pubblicazione:
- `gernalix/fedora-system-monitor`
- `gernalix/fedora-t7-backup`
- `gernalix/app_lifecycle_monitor`
- `gernalix/codex-session-logger`

`vm_oracle` e `oracle-backup-service` restano PRIVATE e sono fuori da questa campagna: niente CI generica o smoke infrastrutturali senza un requisito concreto.

# Routing minimo
Per repo leggi una volta: riga matrice visibility, `.github/workflows`, entrypoint Python/Shell, unit/config direttamente coinvolte e test esistenti. Niente incident history o inventory host.

# CI
Aggiungi solo check pertinenti e isolabili: Python unittest/compile/import; `bash -n`; shellcheck solo se già compatibile; systemd/config/YAML parse con fixture/temp dir; backup->restore solo in temp dir. Mai dischi reali, Telegram, Kuma, SSH o production secrets.

PUBLIC: hosted standard PR+push default branch. PRIVATE dopo audit: solo gate leggero automatico, niente schedule/job pesanti. Sempre path filter docs-only, concurrency, permissions minime e artifact failure-only <=3 giorni.

# Ciclo
Preflight minimo -> push -> singolo run GitHub. Failure: solo job/log fallito, fix minimo, leaf gate e nuovo run. Nessun runtime smoke reale se la CI non modifica comportamento runtime.

# Non-goal
Refactor/cleanup, modifiche systemd host, backup/restore reali, restart servizi, mount dischi, VM/Oracle, nuovi self-hosted runner, retry identici.

# Acceptance
Ogni repo attivo in scope ha CI verde per la parte sandboxabile; nessun accesso a infrastruttura/dati reali; PRIVATE non ha job pesanti ricorrenti.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 539590 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 539590`

Output massimo 6 righe: RESULT + una riga per repo + blocker.