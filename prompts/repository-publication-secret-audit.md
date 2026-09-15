[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=940316 | project_id=23 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Audit **read-only** di sicurezza dei repository `gernalix` già pubblici o candidati alla pubblicazione, includendo storia Git completa, tree corrente e rischi GitHub Actions. Aggiorna le sole fonti private:
- `/home/daniele/projects/MegaVault/ai/repository-public-private-matrix.md`
- `/home/daniele/projects/MegaVault/ai/repository-publication-audit.md`

NON cambiare visibility né modificare i repo auditati.

# Scope autoritativo
- Leggi la matrice una sola volta: è l'inventory iniziale.
- Le righe `RETIRE` sono sempre escluse, indipendentemente dal fatto che i repo siano già stati cancellati.
- Scansione completa SOLO per repo attualmente pubblici o baseline `PUBLIC_AFTER_AUDIT`; `PRIVATE` viene scansionato solo se risulta già pubblico.
- Una sola inventory GitHub: `gh repo list gernalix --limit 200 --json name,visibility,isArchived,url,defaultBranchRef`.
- Repo nuovo non classificato: aggiungi `PRIVATE`, `audit_status=UNKNOWN`; non esplorare la codebase.
- Risolvi path tramite MegaVault/remote Git; niente `find ~/`.

# Secret scan — una sola tecnologia
Preferisci `gitleaks` già installato; altrimenti usa un container ufficiale effimero se Podman/Docker è già disponibile. Non installare/confrontare scanner alternativi.

Per tutti i target usa un unico loop/script temporaneo:
1. `git fetch --all --prune --tags` una volta per repo;
2. gitleaks sull'intera history/all refs con output machine-readable e massima redaction;
3. report raw soltanto in `/tmp`;
4. mai stampare secret value, token, password, key, cookie, webhook o payload personali.

Per un finding conserva solo: repo, regola/categoria, path, commit abbreviato, `current|history`, fingerprint redatto se sicuro. Apri il contenuto solo per distinguere placeholder/falso positivo, mostrando esclusivamente contesto redatto.

# Artefatti sensibili — stesso loop
Usa `git ls-files` sul tree corrente e **una sola** enumerazione path della history per cercare:
- `.env*`, credential/secret/key/private certificate;
- DB/dump/backup/export reali;
- cookie/browser profile/session/Login Data;
- file auth/token/webhook non chiaramente codice/test;
- contatti, location, history o dataset personali non sintetici;
- config con host/IP/URL operativi, home path o account identifier non necessari.

Non considerare automaticamente sensibili: Room schema JSON, fixture esplicitamente sintetiche, `.env.example` placeholder, `${{ secrets.NAME }}`.

Esegui grep/regex solo sui tracked text file e solo per categorie ad alto rischio. Nessun dump completo dei match.

# GitHub Actions risk check
Solo dove `.github/workflows` esiste, segnala senza correggere:
- `pull_request_target` che esegue/check-out codice non fidato;
- `permissions: write-all` o write non necessario;
- secrets raggiungibili da contributori esterni;
- self-hosted runner esposto a trigger PR pubblici;
- action terze parti non pin/debolmente pin solo quando il rischio è concreto.

Niente audit supply-chain generale.

# Matrice finale
Per ogni repo compila:
- `audit_status`: `PASS|PASS_WITH_REMEDIATION|PRIVATE_BY_POLICY|RETIRED|BLOCKED`;
- `secret_findings`: soli conteggi per severità;
- `sensitive_artifacts`: categorie/path redatti;
- `history_clean`: `yes|no|unknown`;
- `required_remediation`;
- `final_recommendation`: `PUBLIC|PRIVATE|RETIRE`;
- `publication_ready`: `yes|no`;
- `confidence`: `high|medium|low`.

`publication_ready=yes` SOLO se: `audit_status=PASS`, history/tree puliti, nessuna remediation obbligatoria e confidence high.
Un repo pubblico con secret reale/dato sensibile/artefatto operativo non necessario => `PASS_WITH_REMEDIATION`, `PRIVATE`, `publication_ready=no`, P0.
Credential potenzialmente attivo => remediation `rotate/revoke + history cleanup before republication`, mai valore.
`PRIVATE` non viene promosso senza evidenza forte; `RETIRE` resta escluso.

# Report privato
Aggiorna `repository-publication-audit.md` con tool/versione, audited/skipped/retired, finding redatti, P0 remediation e conteggi PUBLIC/PRIVATE/RETIRE. Nessun valore sensibile.

# Verifica / token discipline
- modifiche ammesse solo ai due file MegaVault + bookkeeping roadmap;
- `git diff --check` sui due file; niente suite MegaVault globale;
- un solo commit+push MegaVault finale;
- niente README/source audit generale, dependency audit, doppio scanner o retry identici;
- batcha fetch+scan+path checks; apri solo path prodotti da evidenza concreta;
- finding reali NON bloccano: completa come `AUDIT_COMPLETE_WITH_FINDINGS`;
- `BLOCKED` solo se inventory/history scan affidabile è impossibile.

# Acceptance
Tutti i repo pubblici/candidati non-RETIRE sono classificati; history+tree sono coperti; ogni riga ha recommendation e `publication_ready`; report è redatto; nessuna visibility/codebase è stata modificata.

# Stop
Dopo `AUDIT_COMPLETE` o `AUDIT_COMPLETE_WITH_FINDINGS`:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 940316 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 940316`

`push_verified=git_push_exit_0` è terminale. Output massimo 7 righe: RESULT, scanner+versione, audited/skipped, PUBLIC/PRIVATE/RETIRE counts, P0 repo names only, MegaVault commit, blocker eventuale.