[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=940316 | project_id=23 | model=GPT-5.5 | reasoning=medium | MegaVault=STRICT`

# Goal
Eseguire una sola campagna fail-closed che: (1) renda subito PRIVATE i repo pubblici classificati `PRIVATE`; (2) auditi history/tree/Actions dei soli repo pubblici o `PUBLIC_AFTER_AUDIT`; (3) applichi la visibility finale; (4) produca un handoff compatto per il successivo lavoro CI, che sarà eseguito direttamente via GitHub/ChatGPT e NON resterà nella roadmap Codex.

Sorgenti/output privati autoritativi:
- `/home/daniele/projects/MegaVault/ai/repository-public-private-matrix.md`
- `/home/daniele/projects/MegaVault/ai/repository-publication-audit.json`
- `/home/daniele/projects/MegaVault/ai/repository-ci-handoff.json`

Repo/workdir operativo per il report: `/home/daniele/projects/MegaVault`. Usa JSON per report/handoff; niente nuovi Markdown di report.

# Scope deterministico
1. Leggi la matrice UNA volta e fai UNA inventory: `gh repo list gernalix --limit 200 --json name,visibility,isArchived,url,defaultBranchRef`.
2. `RETIRE`: esclusi. Repo nuovo non classificato: aggiungi `PRIVATE`, `audit_status=UNKNOWN`, nessuna codebase discovery.
3. Scan completa SOLO per repo attualmente pubblici o baseline `PUBLIC_AFTER_AUDIT`. Un `PRIVATE` viene scansionato solo se era pubblico.
4. Prima dello scan, ogni repo `attualmente pubblico + baseline PRIVATE` va portato PRIVATE. Fallimento => P0 e continua; nessun audit è richiesto per rendere la visibility più restrittiva.

# Scanner — batch, non un dialogo per repo
- Preferisci `gitleaks` già installato; altrimenti container ufficiale effimero solo se Docker/Podman è già disponibile. Non installare altri scanner e non eseguire scanner duplicati.
- Costruisci un unico loop/script temporaneo per tutti i target. Per ciascuno: usa clone locale esistente se valido; altrimenti clone/mirror temporaneo; `git fetch --all --prune --tags` una volta; scan history/all refs con redaction; `git ls-files` + una sola enumerazione path history per artefatti sensibili.
- Raw report esclusivamente `/tmp`. **Non stampare/cat mai il raw report nel transcript.** Parsealo programmaticamente in un riepilogo compatto con solo repo, rule/category, path, commit abbreviato, `current|history` e fingerprint redatto quando sicuro.
- Se il finding è chiaramente classificabile dal rule/path, non fermarti a ragionare tra un repo e l'altro. Intervento modello solo per finding ambiguo che cambia la decisione PUBLIC/PRIVATE.
- Cerca `.env*`, key/cert/credential, DB/dump/export reali, browser/session/cookie, auth/token/webhook, dataset personali e config operativa non necessaria. Fixture sintetiche, Room schema, `.env.example` placeholder e `${{ secrets.NAME }}` non sono finding automatici.

# Workflow Actions
Solo dove `.github/workflows` esiste, controlla in un unico pass rischi concreti: `pull_request_target` con codice non fidato, write permissions eccessive, secret esposti a contributori, self-hosted su PR pubbliche, action terze parti debolmente pin quando rilevante. Niente supply-chain audit generale.

# Decisione + visibility
Per ogni repo: `audit_status`, finding counts, artefatti/path redatti, `history_clean`, remediation, `final_recommendation`, `publication_ready`, confidence, `current_visibility`, `visibility_apply_status`, `default_branch`.

`publication_ready=yes` SOLO con `PASS`, history/tree puliti, nessuna remediation obbligatoria, confidence high.
- `final_recommendation=PUBLIC` + `publication_ready=yes` → PUBLIC.
- Qualsiasi altro stato → PRIVATE / resta PRIVATE.
- `RETIRE` → nessun cambio.
- Repo archived → non riattivare.

Applica visibility in batch via `gh`/API con flag esplicito per le conseguenze. PUBLIC fallito => resta private; PRIVATE fallito => P0. Poi UNA inventory finale globale, niente `gh repo view` per repo.

Credential potenzialmente attivo => `rotate/revoke + history cleanup before republication`, mai valore. Nessun history rewrite/remediation distruttiva qui.

# Output
`repository-publication-audit.json`: `schema_version=1`, `generated_by_prompt_id=940316`, `generated_at_utc`, conteggi finali e una entry ordinata per repo con soli finding redatti/classificazione/remediation/visibility.

`repository-ci-handoff.json`: `schema_version=1`, `generated_by_prompt_id=940316`, `generated_at_utc`, `next_executor="chatgpt_github"`, e una entry per ogni repo esistente non RETIRE con soli `name`, `visibility`, `default_branch`, `audit_status`, `publication_ready`. Questo handoff è sufficiente per il follow-up remoto: NON aggiungere un task Codex CI.

Aggiorna matrice + due JSON; `git diff --check`, parse JSON, un solo commit+push MegaVault. Niente README/source audit generale, retry identici o audit post-applicazione.

# Acceptance
Tutti i repo in scope classificati; history+tree coperti; nessun repo non pronto reso pubblico; baseline PRIVATE pubblici portati private oppure P0 esplicito; visibility finale verificata una volta; matrice/report/handoff redatti e pushati.

# Stop
Dopo `AUDIT_APPLY_COMPLETE` o `AUDIT_APPLY_COMPLETE_WITH_BLOCKERS`, prova `roadmap_guard complete --prompt-id 940316 --dry-run`; se ready esegui complete. Solo su `prompt_identity_mismatch` dovuto a task indipendente precedente usa `reconcile --prompt-id 940316 --result PASS` dry-run + `--confirm-executed`. Altri errori guard => BLOCKED.

Output massimo 7 righe: RESULT, scanner/versione, audited/skipped, PUBLIC/PRIVATE/RETIRE counts, visibility applied/blocked, P0 repo names only, MegaVault commit.
