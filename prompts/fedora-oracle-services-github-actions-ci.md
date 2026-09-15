[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=539590 | project_id=51 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Aggiungere CI sicura ai repository di infrastruttura/servizi:
- `gernalix/vm_oracle`
- `gernalix/oracle-backup-service`
- `gernalix/fedora-system-monitor`
- `gernalix/fedora-t7-backup`
- `gernalix/app_lifecycle_monitor`
- `gernalix/codex-session-logger`

GitHub deve validare tutto ciò che è ripetibile in sandbox; Codex locale/SSH deve fare soltanto uno smoke runtime mirato quando il cloud non può riprodurre systemd, dischi o Oracle VM.

# Scope / discovery limitata
Per ogni repo risolvi `project_id` e stato da MegaVault. Leggi soltanto:
- `.github/workflows`;
- file Python/Shell entrypoint toccati dai test;
- unit file systemd;
- Docker/Compose/nginx/yaml direttamente presenti;
- test esistenti.

Non leggere report storici/incident registry salvo un blocker concreto.

# CI hosted
Aggiungi solo check pertinenti al contenuto reale:
- Python: test runner esistente + syntax/import compile;
- shell: `bash -n`; `shellcheck` solo se già compatibile o installabile senza cambiare il codice per warning estranei;
- systemd: verifica sintattica/unit-file in ambiente temporaneo quando tecnicamente possibile;
- YAML/Compose: parse/config validation;
- nginx: config test solo con fixture/path temporanei, mai endpoint reali;
- backup: test backup -> restore esclusivamente in directory temporanee, mai T7/Seagate reali;
- nessun SSH, token Oracle, Telegram o secret di produzione nei job PR.

Trigger PR + push default branch, concurrency, report solo su failure. Niente scheduled job che tocchi infrastruttura reale.

# Smoke locale dopo hosted PASS
Solo per repo modificati e soltanto se necessario:
- Fedora services: verifica una volta unit/config nel runtime locale senza riavviare servizi non pertinenti;
- `vm_oracle`/`oracle-backup-service`: un solo smoke read-only o su directory temporanea via SSH Oracle, usando helper già esistenti;
- nessun upgrade sistema, nessun reboot, nessuna cancellazione backup;
- non creare self-hosted runner general-purpose per questi repo.

Se lo smoke richiede un secret già gestito da MegaVault, usa il riferimento/runtime esistente; non stampare il valore.

# Sicurezza
Questa fase è `STRICT` perché riguarda backup/infrastruttura:
- mai `rm -rf` su path reali di backup;
- mai test restore sopra dati esistenti;
- mai `docker compose down -v`;
- mai modificare firewall, SSH o Cloudflare per far passare CI;
- se un test richiede side effect reale non isolabile, sostituiscilo con fixture/mock e lascia lo smoke locale manual-dispatch/Codex.

# Ciclo autonomo
Local gate economico -> push -> `gh run watch` -> log fallito soltanto -> fix minimo -> un retry. PASS chiude il repo.

# Acceptance
Ogni repo attivo ha CI hosted verde per la parte sandboxabile; le dipendenze dal runtime reale sono esplicitamente separate e, se toccate, hanno uno smoke non distruttivo PASS.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 539590 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 539590`

Output massimo 8 righe: RESULT + stato per repo/gruppo + smoke locali eseguiti + blocker.
