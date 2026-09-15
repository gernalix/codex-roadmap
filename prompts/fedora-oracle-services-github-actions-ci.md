[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=539590 | project_id=51 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
CI sandboxabile e sicura per:
- `gernalix/vm_oracle`
- `gernalix/oracle-backup-service`
- `gernalix/fedora-system-monitor`
- `gernalix/fedora-t7-backup`
- `gernalix/app_lifecycle_monitor`
- `gernalix/codex-session-logger`

GitHub testa solo ciò che è ripetibile senza infrastruttura reale; Codex locale/SSH esegue al massimo smoke mirati quando indispensabili.

# Routing minimo
Per repo risolvi una volta project_id/stato e leggi soltanto: riga matrice pubblico/privato, `.github/workflows`, entrypoint Python/Shell coinvolti, unit systemd/config Docker/nginx/yaml realmente presenti e test esistenti. Niente report storici/incident registry salvo blocker concreto.

# CI sandbox
Aggiungi solo check pertinenti:
- Python: runner esistente + syntax/import compile;
- shell: `bash -n`; shellcheck solo se già compatibile senza cleanup estraneo;
- systemd: verifica sintattica/unit-file temporanea quando possibile;
- YAML/Compose: parse/config validation;
- nginx: test con fixture/path temporanei;
- backup: backup->restore esclusivamente in directory temporanee.

Mai SSH, Oracle token, Telegram, Cloudflare, dischi T7/Seagate o production secrets nei job PR.

# Visibility/costo
- PUBLIC: hosted standard PR + push default branch.
- PRIVATE: hosted solo gate leggero/sandboxabile, senza schedule o job pesanti ricorrenti; runtime/integrazione pesante resta locale. Non creare self-hosted runner general-purpose per questi repo.

Sempre: path filters per evitare docs-only, concurrency cancel-in-progress, artifact solo failure con retention <=3 giorni.

# Smoke reale — solo dopo CI PASS e solo se necessario
Esegui smoke esclusivamente per un repo/modifica che abbia un requisito non simulabile:
- Fedora: una sola verifica unit/config, senza restart non necessario;
- Oracle/backup: un solo smoke read-only o su temp dir via helper SSH esistente;
- secret solo tramite riferimento/runtime esistente, mai valore stampato.

Se la CI non modifica comportamento runtime, NON fare smoke reale "per sicurezza".

# Guardrail STRICT
Mai `rm -rf` su backup reali, restore sopra dati esistenti, `docker compose down -v`, upgrade/reboot, firewall/SSH/Cloudflare change. Side effect non isolabile => fixture/mock e nota, non workaround.

# Ciclo efficiente
Niente full gate locale duplicato: preflight minimo -> push -> singolo run GitHub canonico. Failure -> solo job/log fallito -> fix minimo -> nuovo run; retry identico vietato. PASS chiude il repo.

# Acceptance
Ogni repo attivo ha CI verde per la parte sandboxabile; PRIVATE non ha job pesanti/scheduled; eventuali smoke reali sono pochi, non distruttivi e motivati da un requisito concreto.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 539590 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 539590`

Output massimo 7 righe: RESULT, public/private strategy, CI repo counts, smoke eseguiti, commit/push, blocker, note safety eventuale.