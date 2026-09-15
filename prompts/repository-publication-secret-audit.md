[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=940316 | project_id=23 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Eseguire un audit **read-only** di sicurezza per la futura pubblicazione dei repository `gernalix`: cercare segreti/credenziali, dati personali o operativi, artefatti sensibili e rischi GitHub Actions nella **storia Git completa** dei repository già pubblici o candidati alla pubblicazione. Aggiornare poi la matrice privata autoritativa:

`/home/daniele/projects/MegaVault/ai/repository-public-private-matrix.md`

Non cambiare la visibilità di alcun repository in questo task.

# Starting point autoritativo — non rifare discovery generale
- La matrice sopra esiste già ed è la baseline da validare; non crearne una seconda.
- Il task precedente della roadmap ritira i repository standalone obsoleti. Le righe `RETIRE` vanno escluse dall'audit di pubblicazione anche se un precedente blocker ne avesse impedito la cancellazione.
- Target costosi da scandire: **solo** repository attualmente pubblici oppure con baseline `PUBLIC_AFTER_AUDIT`. I repository `PRIVATE` non vanno sottoposti a scansione completa salvo che risultino attualmente pubblici.
- La roadmap pubblica NON deve contenere nomi/valori di segreti, risultati sensibili o dump della matrice privata.
- Nessun Chrome/browser: usa Git, `gh`, scanner locale e filesystem.

# Inventario minimo
1. Leggi una sola volta la matrice privata.
2. Esegui una sola inventory GitHub, preferibilmente:
   `gh repo list gernalix --limit 200 --json name,visibility,isArchived,url,defaultBranchRef`
3. Confronta inventory e matrice. Se esiste un repo nuovo non classificato, aggiungilo alla matrice come `PRIVATE` + `audit_status=UNKNOWN` senza avviare discovery della sua codebase.
4. Risolvi i path locali tramite MegaVault/remote Git; non usare `find ~/` né scansioni generiche del filesystem.

# Scanner segreti — una sola tecnologia
Usa **un solo scanner** per l'intera campagna:
- preferisci `gitleaks` se già installato;
- se assente ma Podman/Docker è già disponibile, usa un container effimero ufficiale gitleaks montando il repo read-only;
- non installare/comparare più scanner e non eseguire gitleaks + trufflehog sullo stesso repo;
- se serve capire la sintassi della versione disponibile, una sola chiamata `--help` è ammessa.

Per ogni target, raggruppa in un unico loop/script temporaneo le operazioni ripetitive:
1. `git fetch --all --prune --tags` una sola volta;
2. scansione gitleaks della storia Git completa/all refs con report machine-readable e **redaction massima**;
3. report temporanei solo sotto `/tmp`; non committare report raw degli scanner;
4. non stampare mai secret value, token, password, private key, cookie, webhook o stringhe equivalenti in terminale/finale.

Se lo scanner trova un possibile segreto, conserva solo: repo, categoria/regola, path, commit abbreviato, stato `current/history`, fingerprint/redacted id se già sicuro. Non aprire il blob completo salvo che serva a distinguere un placeholder da un segreto reale; in quel caso mostra al massimo contesto redatto.

# Audit artefatti sensibili
Per gli stessi target, con comandi batch e senza leggere file inutili:

## Current tracked tree
Usa `git ls-files` + filtri mirati per individuare almeno:
- `.env*`, credential/secret files, key/certificate private material;
- SQLite/DB/dump/backup/export reali;
- cookie/browser profile/session storage/Login Data;
- file con token/webhook/session/auth nel nome che non siano chiaramente codice/test;
- dataset/export personali, contact/location/history fixtures non sintetiche;
- configurazioni contenenti host/IP/URL operativi, home path personali o identificatori account non necessari al codice.

Non trattare automaticamente come finding i normali Android Room schema JSON, fixture esplicitamente sintetiche, `.env.example` con placeholder o riferimenti `${{ secrets.NAME }}`.

## Git history
Usa una sola enumerazione dei path storici (`git log --all --name-only --pretty=format:` o equivalente) e applica gli stessi pattern. Ispeziona contenuto storico solo quando il path è concretamente sospetto.

## Text exposure
Esegui grep/regex mirati solo sui file tracked testuali per categorie ad alto rischio: credenziali hard-coded, private key headers, webhook/bot tokens, cookie/session data, coordinate/contatti/dati personali reali e dettagli infrastrutturali che la matrice considera motivo per restare privati. Minimizza falsi positivi e non fare dump di match completi.

# Audit GitHub Actions per repo pubblico
Solo se esiste `.github/workflows`:
- segnala `pull_request_target` con checkout/esecuzione di codice non fidato;
- `permissions: write-all` o permessi write non necessari;
- uso di secrets in workflow eseguibili da contributori esterni;
- action di terze parti non pin/debolmente pin quando il rischio è concreto;
- self-hosted runner raggiungibile da PR pubbliche senza gate manuale.

Non trasformare questo task in un audit supply-chain generale: correggi la matrice/report, non i workflow. I fix appartengono ai successivi task CI.

# Matrice finale
Aggiorna **lo stesso file** MegaVault aggiungendo/compilando per ogni repo:
- `audit_status`: `PASS`, `PASS_WITH_REMEDIATION`, `PRIVATE_BY_POLICY`, `RETIRED`, `BLOCKED`;
- `secret_findings`: conteggi per severità, mai valori;
- `sensitive_artifacts`: sole categorie/path redatti;
- `history_clean`: yes/no/unknown;
- `required_remediation`;
- `final_recommendation`: `PUBLIC`, `PRIVATE`, `RETIRE`;
- `confidence`: high/medium/low.

Regole:
- `PUBLIC_AFTER_AUDIT` diventa `PUBLIC` solo con storia/tree puliti oppure con finding chiaramente falso/placeholder documentato;
- un repo attualmente pubblico con segreto reale, dato personale sensibile o artefatto operativo non necessario => `PASS_WITH_REMEDIATION`, `final_recommendation=PRIVATE` e priorità P0;
- se il finding è un credential potenzialmente attivo, remediation deve dire **rotate/revoke + history cleanup before any republication**, senza riportarne il valore;
- `PRIVATE` resta privato salvo evidenza forte che sia solo codice riusabile e ci sia beneficio concreto alla pubblicazione; non promuoverlo per inerzia;
- `RETIRE` resta `RETIRE` e non viene scandito.

# Report privato
Crea/aggiorna:
`/home/daniele/projects/MegaVault/ai/repository-publication-audit.md`

Contenuto compatto:
- data/audit tool/version;
- repos audited/skipped/retired;
- finding per repo solo redatti;
- P0 remediation;
- riepilogo finale PUBLIC/PRIVATE/RETIRE;
- nessun secret value, payload personale, cookie, token o dump scanner.

# Scrittura e verifica
- Non modificare i repository auditati.
- Sono ammesse modifiche solo a matrix/report MegaVault e al bookkeeping finale della roadmap.
- Prima del commit MegaVault: `git diff --check` sui due file; nessun test globale MegaVault perché non cambia codice/SQLite.
- Push MegaVault una sola volta alla fine.
- Se durante il task emerge un secret reale già pubblico, **non** riscrivere history, non ruotare credenziali e non cambiare visibility: registralo come P0 e continua l'audit, a meno che la prosecuzione rischi di esporre ulteriormente il valore.

# Risparmio token / tool-call
- una sola inventory GitHub;
- una sola scelta scanner;
- batch loop per fetch+scan dei target;
- niente lettura README/source generale dei repo;
- apri solo file/path concreti prodotti dagli scanner/filtri;
- niente doppia verifica con scanner equivalenti;
- niente retry identico senza nuova evidenza;
- non analizzare dipendenze, qualità codice, bug o CI oltre ai rischi di pubblicazione sopra;
- problemi collaterali: registra senza investigarli;
- quando matrix+report sono completi, STOP.

# Acceptance
Audit completato se:
- tutti i repository attualmente pubblici e tutti i `PUBLIC_AFTER_AUDIT` non-retired sono classificati;
- storia Git + current tracked tree sono stati coperti con un solo scanner e i controlli artefatti mirati;
- la matrice privata contiene una `final_recommendation` motivata per ogni repo;
- il report privato contiene solo evidenza redatta;
- nessun repository ha cambiato visibilità e nessun secret value è stato stampato/committato;
- MegaVault matrix/report sono pushati.

I finding non rendono l'audit `BLOCKED`: usa `RESULT=AUDIT_COMPLETE_WITH_FINDINGS` e completa il task. `BLOCKED` solo se non è possibile ottenere l'inventario o eseguire una scansione affidabile della storia dei target.

# Stop
Dopo `AUDIT_COMPLETE` o `AUDIT_COMPLETE_WITH_FINDINGS`:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 940316 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 940316`

`push_verified=git_push_exit_0` è terminale: niente altri audit/status/fetch. Output massimo 7 righe: RESULT, scanner+versione, audited/skipped, PUBLIC/PRIVATE/RETIRE counts, P0 findings count+repo names only, MegaVault commit, blocker eventuale.
