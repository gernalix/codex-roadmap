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

# Delete — solo dopo archive PASS
Per ciascun repo `[ ]`:
1. elimina il remoto `gernalix/<repo>` via `gh`/GitHub API, mai Chrome;
2. verifica una volta che il remoto non esista più;
3. solo se il delete remoto è riuscito, elimina il clone locale canonico già archiviato, con `realpath` obbligatoriamente sotto `/home/daniele/projects/`; nessun glob/find-delete;
4. se il remoto non è eliminabile per auth/permessi, conserva anche il clone locale e registra BLOCKED per quel repo; continua gli altri senza workaround rischiosi.

Non cancellare mai repo `[x]`.

# Bookkeeping dopo i delete riusciti
- MegaVault: conserva identità/project_id/storia, marca i repo eliminati come retired/archived e registra path+SHA256 dello ZIP; non riusare project_id.
- `repository-public-private-matrix.md`: i repo eliminati diventano `RETIRE`/non più candidati alla pubblicazione, così l'audit successivo li ignora.
- Se `github-autosync` è `[x]`, rimuovi soltanto riferimenti operativi esatti ai repo eliminati che causerebbero `missing/no_upstream`, con test mirati. Se `github-autosync` è `[ ]`, non modificarlo: verrà eliminato come gli altri.

# Non-goal
Niente audit codebase, refactor, migrazione dati, history rewrite, nuova CI, browser, cancellazione di account/issue/release separata, retry identici o pulizia di file fuori dai repo selezionati.

# Acceptance
PASS solo se:
- la checklist risulta modificata dall'utente e valida 1:1;
- ZIP unico esiste, `unzip -t` PASS, SHA256 registrato;
- ogni repo `[ ]` ha bundle verificato e snapshot locale se esisteva un clone;
- tutti i repo `[ ]` eliminabili sono rimossi da GitHub e localmente;
- tutti i repo `[x]` sono intatti;
- MegaVault/matrice riflettono il risultato;
- nessun repo fuori target è stato toccato.

Se anche un repo `[ ]` resta per blocker, lascia il task pendente e riporta solo quel blocker; non rifare archive già verificati senza nuova evidenza.

# Stop
Solo a PASS completo:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 157771 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 157771`

Output massimo 7 righe: RESULT, KEEP/RETIRE counts, ZIP path+SHA256, bundle/snapshot verify, remote deletes, local deletes+MegaVault, blocker eventuale.