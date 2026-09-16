[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=940316 | project_id=23 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Eseguire una sola campagna fail-closed che: (1) protegga subito i repo già pubblici ma classificati `PRIVATE`; (2) auditi history/tree/Actions dei repo pubblici o `PUBLIC_AFTER_AUDIT`; (3) applichi la visibility finale senza un secondo task; (4) produca un handoff compatto per la CI successiva.

Sorgenti/output privati autoritativi:
- `/home/daniele/projects/MegaVault/ai/repository-public-private-matrix.md`
- `/home/daniele/projects/MegaVault/ai/repository-publication-audit.json`
- `/home/daniele/projects/MegaVault/ai/repository-ci-handoff.json`

Usa JSON per report/handoff: non creare nuovi Markdown di report in MegaVault.

# Scope
- Leggi la matrice una volta e fai una sola inventory: `gh repo list gernalix --limit 200 --json name,visibility,isArchived,url,defaultBranchRef`.
- `RETIRE`: esclusi. Repo nuovo non classificato: aggiungi `PRIVATE`, `audit_status=UNKNOWN`, niente codebase discovery.
- Scansione completa solo per repo attualmente pubblici o baseline `PUBLIC_AFTER_AUDIT`; `PRIVATE` viene scansionato solo se era pubblico.
- Prima dello scan, ogni repo **attualmente pubblico + baseline PRIVATE** va portato PRIVATE con `gh` (nessun audit è necessario per rendere più restrittiva la visibility). Se il cambio fallisce, registra P0 e continua.

# Audit — una sola tecnologia
Preferisci `gitleaks` già installato; altrimenti container ufficiale effimero se Docker/Podman è già disponibile. Un solo loop per target: `git fetch --all --prune --tags` una volta, scan completa history/all refs con redaction, `git ls-files` + una sola enumerazione path history per artefatti sensibili. Report raw solo `/tmp`; mai stampare valori di secret/cookie/token/webhook/dati personali.

Conserva soltanto repo, categoria/regola, path, commit abbreviato, `current|history` e fingerprint redatto se sicuro. Cerca `.env*`, key/cert/credential, DB/dump/export reali, browser/session/cookie, auth/token/webhook, dataset personali e config operativa non necessaria. Non trattare automaticamente come finding fixture sintetiche, Room schema, `.env.example` placeholder o `${{ secrets.NAME }}`.

Solo dove esistono workflow, controlla rischi concreti: `pull_request_target` con codice non fidato, write permissions eccessive, secret esposti a contributori, self-hosted su PR pubbliche, action terze parti debolmente pin quando rilevante. Niente supply-chain audit generale.

# Classificazione + visibility nella stessa sessione
Per ogni repo compila: `audit_status`, finding counts, artefatti/path redatti, `history_clean`, remediation, `final_recommendation`, `publication_ready`, confidence, `current_visibility`, `visibility_apply_status`, `default_branch`.

`publication_ready=yes` solo con `PASS`, history/tree puliti, nessuna remediation obbligatoria, confidence high.
- `final_recommendation=PUBLIC` + `publication_ready=yes` -> PUBLIC.
- Qualsiasi altro stato (`PRIVATE`, `PASS_WITH_REMEDIATION`, `BLOCKED`, `UNKNOWN`, confidence < high) -> PRIVATE / resta PRIVATE.
- `RETIRE` -> nessun cambio.
- Repo archived -> non riattivare.

Applica i cambi via `gh`/API con flag esplicito per le conseguenze della visibility. Nessuna decisione ad hoc per “far passare” la CI. Un cambio PUBLIC fallito lascia il repo private; un cambio PRIVATE fallito è P0. Dopo tutti i cambi fai **una sola** inventory finale, senza `gh repo view` per repo.

Credential potenzialmente attivo => `rotate/revoke + history cleanup before republication`, mai valore. Non eseguire remediation distruttive o history rewrite in questo task.

# Report audit JSON
Scrivi `repository-publication-audit.json` con `schema_version: 1`, `generated_by_prompt_id: 940316`, `generated_at_utc`, conteggi finali e una entry per repo in scope con i soli campi necessari a preservare finding redatti, classificazione, remediation e applicazione visibility. Ordina per `name`. Nessun secret o contenuto raw.

# Handoff CI — nessuna seconda inventory nel task successivo
Crea `repository-ci-handoff.json` con:
- `schema_version: 1`;
- `generated_by_prompt_id: 940316`;
- `generated_at_utc`;
- `repositories`: una entry per ogni repo **esistente e non RETIRE** con soli campi `name`, `visibility`, `default_branch`, `audit_status`, `publication_ready`.

L'handoff deve derivare esclusivamente dall'inventory finale e dalla classificazione appena completata; niente nuova discovery. Ordina per `name`. Non includere finding, path sensibili o dettagli che il task CI non usa.

# Output privato / verifica
Aggiorna matrice + i due JSON. `git diff --check` sulla matrice e parse JSON dei due output; un solo commit+push MegaVault. Niente README/source audit generale, scanner duplicati, retry identici o audit post-applicazione.

# Acceptance
Tutti i repo in scope classificati; history+tree coperti; nessun repo non pronto reso pubblico; baseline PRIVATE pubblici portati private oppure P0 esplicito; visibility finale verificata una volta; matrice/report JSON redatti e pushati; handoff CI completo per tutti i repo esistenti non RETIRE.

# Stop
Dopo `AUDIT_APPLY_COMPLETE` o `AUDIT_APPLY_COMPLETE_WITH_BLOCKERS`:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 940316 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 940316`

`push_verified=git_push_exit_0` è terminale. Output massimo 7 righe: RESULT, scanner/versione, audited/skipped, PUBLIC/PRIVATE/RETIRE counts, visibility applied/blocked, P0 repo names only, MegaVault commit.