[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=157771 | project_id=51 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Dopo la revisione umana della checklist, creare **un unico archivio ZIP verificato** di tutti i repository lasciati `[ ]` e poi eliminare da GitHub e dal filesystem locale soltanto quelli per cui non resta alcuna dipendenza runtime attiva. I repo `[x]` devono restare intatti.

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

# Dependency gate — prima di qualunque delete
Per ogni repo `[ ]`, usa MegaVault **solo per quel repo/project_id** per verificare se risultano servizi, timer, cron, container, launcher, desktop integration, runtime path o job ancora attivi su Fedora, Oracle o altri host registrati.

- Se un runtime su host diverso da Fedora è ancora marcato attivo e non esiste nel task una procedura di detach esplicita e verificabile, marca **quel repo** `BLOCKED_ACTIVE_RUNTIME:<host>`: archivialo ma non cancellare remoto né clone.
- Non spegnere servizi remoti/VM o runtime di altri host per deduzione. Questo task può disattivare automaticamente solo integrazioni Fedora locali esattamente attribuibili al repo `[ ]` e contemplate sotto.
- Stato MegaVault vecchio/non conclusivo non basta per cancellare: se indica possibile runtime attivo, fai al massimo una verifica read-only mirata dell'host pertinente; se resta ambiguo => BLOCKED per quel repo.
- Un repo senza runtime/integration attiva passa al normale archive/delete.

# Archivio prima di qualunque delete
Target archive: `/home/daniele/Documents/repository-archives/gernalix-retired-repositories-YYYYMMDD-HHMMSS.zip`.

Crea la directory archivio con permessi privati (`0700`) e il ZIP finale `0600`: l'archivio può contenere secret/cookie/config storici e non deve essere world-readable.

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
- `MANIFEST.md` e/o JSON con repo, remote URL, visibility, default branch, HEAD/ref info essenziali, dependency-gate result e SHA256 degli artefatti.

Verifica **ogni** bundle con `git bundle verify`, ogni tar con `tar -tzf`, poi il ZIP con `unzip -t`. Calcola SHA256 finale dello ZIP e conferma mode `0600`. Se una verifica fallisce: STOP, nessun delete.

# Runtime/hook detach — dopo archive PASS, prima del delete locale/remoto
Per ogni repo `[ ]` che passa il dependency gate e ha integrazioni Fedora, verifica in modo mirato se ha installato riferimenti esterni che continuerebbero a puntare al clone: launcher/wrapper, shell function/alias, symlink in PATH, desktop entry, timer/service systemd user/system, cron, GNOME/Chrome integration o config generata. Usa soltanto installer/uninstaller, manifest, documentazione operativa e path esatti dichiarati dal repo/MegaVault; niente scansioni generali della home.

Regole comuni:
1. registra nel manifest quali riferimenti esterni sono stati trovati;
2. disinstalla/disabilita **solo** quelli appartenenti al repo `[ ]`, preferendo un uninstaller canonico se esiste e se non rimuove dati utente estranei;
3. prima di rimuovere un symlink/file, verifica che sia realmente quello del repo (target, contenuto o unit ExecStart coerente); path omonimo non attribuibile => non toccarlo;
4. verifica che nessun riferimento noto continui a dipendere dal clone e che l'eventuale comando/app sottostante continui a funzionare;
5. non cancellare DB, log, state, backup, token/config o altri dati runtime esterni al clone salvo quando sono esclusivamente file di integrazione necessari al detach;
6. se non puoi dimostrare una rimozione sicura, marca quel repo BLOCKED e **non cancellare né remoto né clone**.

## Caso esplicito `codex-session-logger`, se `[ ]`
L'installer noto crea:
- `~/.local/bin/codex-live`
- `~/.local/bin/codex-log`
- `~/.local/bin/codex-session-capture`
- `~/.bashrc.d/50-codex-session-logger.sh` (definisce `codex()` + alias `codex-*`)
- opzionalmente `~/.tmux.conf` come symlink a `<repo>/config/tmux.conf`.

Rimuovi **solo** questi riferimenti se sono symlink/file attribuibili al repo. Non cancellare `~/.local/state/codex-session-logger/` né le sessioni/log storici. Dopo il detach, in un ambiente che non abbia in memoria la vecchia shell function, verifica `type -a codex`/`command -v codex` e `codex --version`: devono risolvere e funzionare col Codex reale. Se no => BLOCKED e conserva repo.

## Caso esplicito `wayland-workspace-switcher`, se `[ ]`
È ad alto rischio perché l'installer modifica più superfici. Non usare il solo `scripts/rollback-launcher.sh`: è parziale. Usa `scripts/install.sh` + `~/.config/wayland-workspace-switcher/install-info.json` per risolvere gli identificatori esatti e, solo se presenti/attribuibili a WWS:
- stop/disable + rimozione di `~/.config/systemd/user/wayland-workspace-switcher-bridge.service`, poi `systemctl --user daemon-reload`;
- rimuovi i symlink WWS in `~/.local/bin/` (`wwsctl`, `wws-gui`, `wws-native-host`, `wws-chrome`, `wws-bridge-server`, `wws-start`, `wws-kitty-logged-shell`) **solo se puntano nel repo**;
- disabilita e rimuovi l'estensione GNOME `wayland-workspace-switcher@daniele` solo se coincide con quella installata da WWS;
- rimuovi i Native Messaging Host/Proxy e gli External Extension JSON di Chrome/Chromium solo quando nome/extension_id e path puntano agli artefatti WWS; per l'eventuale `/usr/share/google-chrome/extensions/<id>.json`, toccalo solo se il contenuto `external_crx` punta nel repo;
- rimuovi le due custom keybinding WWS dai `custom-keybindings` GNOME e resetta soltanto i relativi path/schema;
- se `~/.local/share/applications/com.google.Chrome.desktop` è la variante WWS (`Exec=.../wws-chrome`), rimuovi **solo quella override utente** e verifica che rimanga disponibile il launcher Chrome sottostante; rimuovi anche le desktop entry/copie WWS esatte;
- per Kitty **non ripristinare ciecamente l'ultimo backup**: rimuovi soltanto le righe WWS esatte dal `kitty.conf` corrente, salvo equivalenza del backup dimostrata;
- ispeziona il Flatpak override di `com.google.Chrome`; rimuovi solo i permessi specificamente aggiunti da WWS (`filesystem` del repo e talk-name relativo) se ciò è possibile senza resettare altri override. Vietato `flatpak override --reset` se eliminerebbe preferenze non WWS. Se non è possibile separare con certezza => BLOCKED e conserva repo.

Preserva `~/.config/wayland-workspace-switcher/` e altri state/log esterni al clone salvo i file di integrazione esplicitamente sopra. Dopo il detach verifica almeno che Chrome sottostante resti disponibile e che l'unit WWS non sia più enabled/active.

## Casi systemd noti fra i RETIRE
- `git-change-ledger`: se installati, disable/stop e rimuovi soltanto `git-change-ledger.service`/`.timer` e il launcher `~/.local/bin/git-change-ledger` se attribuibili al repo. **Preserva** `/home/daniele/sync_root/db/git_change_ledger.sqlite3` e qualsiasi DB/state esterno al clone.
- `mint-freeze-forensics`: controlla esattamente `mint-freeze-forensics.service`, `mint-resource-guardian.service` e `mint-resource-guardian.timer`; rimuovi solo unit/install refs attribuibili al repo. Preserva output/state esterni.
- `surface-recovery-hardening`: contiene numerose unit/config di hardening. **Non revertire automaticamente hardening OS, udev/modprobe/logind/sshd/Xorg o config copiate indipendenti**. Disabilita/rimuovi soltanto unit/launcher installati che dipendono ancora da path dentro il clone da cancellare. Se una unit attiva ha semantica non chiara o una config di sistema dipende dal repo => BLOCKED per quel repo.
- `app_lifecycle_monitor` e `codex_weekly_limit_monitor`: gli installer presenti sono PowerShell/Windows. Non dichiarare disinstallati eventuali Scheduled Task su un altro host Windows dalla sola verifica Fedora; se MegaVault indica ancora quel runtime attivo su altro host => BLOCKED_ACTIVE_RUNTIME.

# Delete — solo dopo archive PASS + dependency/runtime gate PASS del singolo repo
Per ciascun repo `[ ]` non bloccato:
1. elimina il remoto `gernalix/<repo>` via `gh`/GitHub API, mai Chrome;
2. verifica una volta che il remoto non esista più;
3. solo se il delete remoto è riuscito **e il runtime/hook detach è PASS o non applicabile**, elimina il clone locale canonico già archiviato; per `/home/daniele/projects/<repo>` usa `realpath` e verifica il prefisso `/home/daniele/projects/`. Per un diverso path canonico restituito da MegaVault, non cancellarlo automaticamente se non esiste un root consentito esplicito nel record/protocollo: marca il clone `BLOCKED_LOCAL_PATH` anziché ampliare il guard;
4. se il remoto non è eliminabile per auth/permessi, conserva anche il clone locale e registra BLOCKED per quel repo; continua gli altri senza workaround rischiosi.

Non cancellare mai repo `[x]`.

# Bookkeeping dopo i delete riusciti
- MegaVault: conserva identità/project_id/storia, marca i repo eliminati come retired/archived e registra path+SHA256 dello ZIP; non riusare project_id.
- `repository-public-private-matrix.md`: i repo eliminati diventano `RETIRE`/non più candidati alla pubblicazione, così l'audit successivo li ignora.
- Se `github-autosync` è `[x]`, rimuovi soltanto riferimenti operativi esatti ai repo eliminati che causerebbero `missing/no_upstream`, con test mirati. Se `github-autosync` è `[ ]`, non modificarlo: verrà eliminato come gli altri.

# Non-goal
Niente audit codebase, refactor, migrazione dati, history rewrite, nuova CI, browser automation, cancellazione di account/issue/release separata, retry identici, cancellazione di dati runtime/log utente fuori dai clone o rollback generico di configurazioni OS. Non usare cleanup broad (`find ~/`, glob distruttivi, reset di config intere) per inseguire integrazioni residue.

# Acceptance
PASS solo se:
- la checklist risulta modificata dall'utente e valida 1:1;
- ZIP unico esiste, mode `0600`, `unzip -t` PASS, SHA256 registrato;
- ogni repo `[ ]` ha bundle verificato e snapshot locale se esisteva un clone;
- dependency gate registrato per ogni repo `[ ]`;
- runtime/hook dei repo eliminati risultano safely detached o non applicabili prima della cancellazione;
- tutti i repo `[ ]` **non bloccati** sono rimossi da GitHub e localmente dove il path guard lo permette;
- nessun repo con runtime attivo/ambiguo viene cancellato;
- tutti i repo `[x]` sono intatti;
- MegaVault/matrice riflettono il risultato;
- nessun repo fuori target è stato toccato.

Se anche un repo `[ ]` resta per blocker, lascia il task pendente e riporta solo blocker e repo interessati; non rifare archive già verificati senza nuova evidenza.

# Stop
Solo a PASS completo:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 157771 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 157771`

Output massimo 7 righe: RESULT, KEEP/RETIRE counts, ZIP path+SHA256, dependency gate, bundle/snapshot verify, runtime/hook detach+deletes, MegaVault/blocker.