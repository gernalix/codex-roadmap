[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=157771 | project_id=51 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Dopo la revisione umana della checklist, creare **un unico archivio ZIP verificato** di tutti i repository lasciati `[ ]` e poi eliminarli da GitHub e dal filesystem locale. I repo `[x]` devono restare intatti.

Sorgenti autoritative:
- `/home/daniele/projects/MegaVault/ai/repository-retention-checklist.md`
- `/home/daniele/projects/MegaVault/ai/repository-retention-checklist.generated.json`

# Gate umano — fail closed
1. Leggi checklist + sidecar una sola volta e calcola SHA256 corrente.
2. Se SHA256 corrente == `checklist_sha256` generato: `BLOCKED_CHECKLIST_NOT_REVIEWED` e STOP, senza archive/delete.
3. Accetta solo righe repository nel formato esatto `- [x] NAME`, `- [X] NAME` o `- [ ] NAME`; duplicate/malformed => BLOCKED.
4. Fai una sola inventory GitHub owned attuale. Ogni repo attuale deve essere rappresentato una volta nella checklist; repo nuovo/mancante => BLOCKED, nessuna cancellazione.
5. `MegaVault` e `codex-roadmap` devono essere `[x]` perché questo workflow dipende da entrambi. Se `codex-usage-monitor` è `[x]`, anche `codex-usage` deve essere `[x]`. Incoerenza => BLOCKED, non correggere la scelta autonomamente.

`[x]` = KEEP. `[ ]` = RETIRE. Non reinterpretare nomi o intenzioni.

# Archivio prima di qualunque delete
Target archive: `/home/daniele/Documents/repository-archives/gernalix-retired-repositories-YYYYMMDD-HHMMSS.zip`.

Preflight spazio: stima sorgenti locali + staging e richiedi margine ragionevole; spazio insufficiente => BLOCKED prima di modificare repo.

Per ogni repo `[ ]`:
- risolvi il clone locale solo tramite MegaVault/path canonico o `/home/daniele/projects/<nome>` esatto; niente `find ~/`;
- se esiste clone locale, `git fetch --all --prune --tags` senza reset/stash e crea un `git bundle --all` verificabile;
- inoltre crea `local-snapshots/<repo>.tar.gz` dell'intero clone locale **inclusi `.git`, file ignorati, untracked e modifiche non committate**, così nessuno stato locale va perso;
- se non esiste clone locale, usa un mirror temporaneo del remoto e crea comunque il bundle completo;
- non stampare contenuti di `.env`, token, cookie, key o altri secret: possono finire nell'archivio offline, mai nei log.

Lo staging deve contenere almeno:
- `bundles/<repo>.bundle`
- eventuali `local-snapshots/<repo>.tar.gz`
- `MANIFEST.md` e/o JSON con repo, remote URL, visibility, default branch, HEAD/ref info essenziali e SHA256 degli artefatti.

Verifica **ogni** bundle con `git bundle verify`, ogni tar con `tar -tzf`, poi il ZIP con `unzip -t`. Calcola SHA256 finale dello ZIP. Se una verifica fallisce: STOP, nessun delete.

# Runtime/hook detach — dopo archive PASS, prima del delete locale
Per ogni repo `[ ]` che ha un clone locale, verifica in modo mirato se ha installato integrazioni esterne che continuerebbero a puntare al clone: launcher/wrapper, shell function/alias, symlink in PATH, desktop entry, timer/service systemd user/system, cron o config generata. Usa soltanto installer/uninstaller, manifest, documentazione operativa e path esatti dichiarati dal repo/MegaVault; niente scansioni generali della home.

Se esistono integrazioni:
1. registra nel manifest quali riferimenti esterni sono stati trovati;
2. disinstalla/disabilita **solo** quelli appartenenti al repo `[ ]`, preferendo l'uninstaller canonico se esiste;
3. verifica che nessun riferimento residuo noto punti al clone da eliminare e che l'eventuale comando/app sottostante continui a funzionare;
4. se non puoi dimostrare una rimozione sicura, **non eliminare il clone locale** e marca quel repo BLOCKED; non improvvisare cleanup più ampi.

Caso esplicito `codex-session-logger`, se `[ ]`: rimuovi i soli wrapper/function/alias/symlink/tmux config installati dal logger secondo il suo installer; poi prova in una shell pulita/non interattiva che `codex` risolva al binario Codex reale e che `codex --version` funzioni. Non disinstallare Codex stesso e non cancellare i log utente fuori dal clone salvo istruzione esplicita.

# Delete — solo dopo archive PASS
Per ciascun repo `[ ]`:
1. elimina il remoto `gernalix/<repo>` via `gh`/GitHub API, mai Chrome;
2. verifica una volta che il remoto non esista più;
3. solo se il delete remoto è riuscito **e il runtime/hook detach locale è PASS o non applicabile**, elimina il clone locale canonico già archiviato, con `realpath` obbligatoriamente sotto `/home/daniele/projects/`; nessun glob/find-delete;
4. se il remoto non è eliminabile per auth/permessi, conserva anche il clone locale e registra BLOCKED per quel repo; continua gli altri senza workaround rischiosi.

Non cancellare mai repo `[x]`.

# Bookkeeping dopo i delete riusciti
- MegaVault: conserva identità/project_id/storia, marca i repo eliminati come retired/archived e registra path+SHA256 dello ZIP; non riusare project_id.
- `repository-public-private-matrix.md`: i repo eliminati diventano `RETIRE`/non più candidati alla pubblicazione, così l'audit successivo li ignora.
- Se `github-autosync` è `[x]`, rimuovi soltanto riferimenti operativi esatti ai repo eliminati che causerebbero `missing/no_upstream`, con test mirati. Se `github-autosync` è `[ ]`, non modificarlo: verrà eliminato come gli altri.

# Non-goal
Niente audit codebase, refactor, migrazione dati, history rewrite, nuova CI, browser, cancellazione di account/issue/release separata, retry identici, cancellazione di dati runtime/log utente fuori dai clone o pulizia di file estranei ai riferimenti installati verificati.

# Acceptance
PASS solo se:
- la checklist risulta modificata dall'utente e valida 1:1;
- ZIP unico esiste, `unzip -t` PASS, SHA256 registrato;
- ogni repo `[ ]` ha bundle verificato e snapshot locale se esisteva un clone;
- runtime/hook dei repo `[ ]` risultano safely detached o non applicabili prima della cancellazione locale;
- tutti i repo `[ ]` eliminabili sono rimossi da GitHub e localmente;
- tutti i repo `[x]` sono intatti;
- MegaVault/matrice riflettono il risultato;
- nessun repo fuori target è stato toccato.

Se anche un repo `[ ]` resta per blocker, lascia il task pendente e riporta solo quel blocker; non rifare archive già verificati senza nuova evidenza.

# Stop
Solo a PASS completo:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 157771 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 157771`

Output massimo 7 righe: RESULT, KEEP/RETIRE counts, ZIP path+SHA256, bundle/snapshot verify, runtime/hook detach, remote+local deletes, MegaVault/blocker.