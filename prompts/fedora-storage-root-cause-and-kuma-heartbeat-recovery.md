PROMPT_ID=673914 | project_id=15 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST

# Goal

Risolvi alla radice il problema mostrato da Uptime Kuma per `Fedora Storage` #40, senza mascherarlo con soglie/timeout più permissivi. Tratta separatamente e risolvi quanto possibile dei due problemi già provati: **(A)** reale emergenza spazio filesystem al 2.7927%; **(B)** ricomparsa di `No heartbeat in the time window` per Storage e Host malgrado il fix source-side dei heartbeat al minuto.

# Starting point verificato — non rifare discovery generale

- repo: `/home/daniele/projects/fedora-system-monitor`, MegaVault project `15`;
- il branch remoto `main` include il fix `90f28f9` che invia anche `storage` nel heartbeat `minute`;
- il branch remoto include inoltre il deploy canonico runtime-only `scripts/deploy-runtime.sh`, introdotto e hardenizzato fino al commit `1fea2b3aad8fe776ec150ca959b75a8cc7f0d178` o successivo;
- il deploy helper richiede checkout pulito, copia atomicamente il package in `/usr/local/libexec/fedora-system-monitor`, salva `.source-revision`, esegue pre/post `config-check` + `db-check` e rollback su failure;
- alle 06:40 locali del 2026-09-16 Kuma #40 riceveva di nuovo push `storage: collectors complete; active alerts=1`, quindi il precedente bug `No heartbeat` era temporaneamente sparito;
- nello stesso momento esisteva un alert reale `filesystem.free_percent`, severity `emergency`, valore `2.7927%`, device id `fsuuid:22E02106E020E1B1:view:de538a637dd86975bf64`;
- nello screenshot ~07:02 locali #40 è di nuovo rosso e compare nuovamente `No heartbeat in the time window`; anche #39 `Fedora Host` mostra lo stesso errore di heartbeat;
- Kuma #40 ha `interval=480s`; NON aumentarlo e non disabilitare il monitor;
- l'altro alert Host già verificato è reale (`spd5118`/`sensor.alarm`): non risolverlo in questo task, ma assicurati che Host non sia DOWN per heartbeat mancante.

Prompt autosufficiente: non leggere README/roadmap/spiegazioni/MEMORY/MegaVault salvo blocker concreto. Niente audit repo-wide.

# Esecuzione minima

1. Fai una sola fotografia Git del repo e `pull --ff-only` solo se il worktree è pulito. Parti dal runtime reale, non dal codice.

2. Raccogli **una sola fotografia runtime raggruppata**, con output limitato, sufficiente a spiegare i heartbeat mancanti:
   - stato di `fedora-system-monitor-fast.timer` e `fedora-system-monitor-collect@fast.service`, più `systemctl list-timers` filtrato;
   - journal SOLO di queste unità dall'incirca dalle 06:35 locali o ultimi ~30 minuti;
   - ultimi `collector_runs` pertinenti (`minute`/`five_minute`) e alert attivi dal DB locale;
   - se esiste, leggi `/usr/local/libexec/fedora-system-monitor/.source-revision`; verifica che il runtime installato contenga davvero la policy `minute` con `storage`;
   - una sola lettura remota del DB Kuma per monitor #39/#40 (ultimi ~10 heartbeat) usando l'helper già esistente `/home/daniele/projects/vm_oracle/scripts/oracle_ssh.sh`;
   - mappa l'UUID `22E02106E020E1B1` con `lsblk`/`findmnt`/`blkid` al dispositivo, mountpoint, filesystem, capacità e spazio libero reali.

3. Dai dati determina la causa concreta dei heartbeat mancanti: timer non attivo, service failure, deadline/lock, errore push/rete/credenziali, runtime installato obsoleto/divergente o altro leaf direttamente provato. Correggi SOLO quella causa. Non toccare timeout/interval Kuma.

4. Se il runtime installato non corrisponde al commit corrente, oppure serve una modifica source, usa **solo** `sudo scripts/deploy-runtime.sh` per il deploy del package. `scripts/install.sh` è fuori scope. Riavvia/abilita esclusivamente l'unità esatta che lo richiede.

5. Per il vero alert spazio:
   - identifica l'esatto mount e i principali consumatori **solo su quel filesystem**, con una singola scansione stretta;
   - NON eliminare/spostare file personali, media, archivi, backup, VM, progetti o dati di natura incerta senza scelta esplicita dell'utente;
   - se lo spazio è occupato da cache/temp/log chiaramente rigenerabili e sicuri da eliminare, libera il minimo necessario e misura di nuovo;
   - altrimenti NON improvvisare cleanup: quantifica i GiB da liberare per superare 5%, 10%, 20% e per ottenere recovery completa tenendo conto dell'isteresi configurata (target finale >22% se necessario per uscire progressivamente da emergency/critical/warning), e termina come BLOCKED lasciando l'alert reale visibile.

6. Dopo il fix heartbeat, non fare polling manuale ripetuto. Usa il timer reale e verifica **3 cicli schedulati consecutivi** per #39/#40. Una singola `sudo /usr/local/bin/fedora-system-monitor collect minute` è ammessa solo come smoke test iniziale se serve.

7. Se emerge un bug di codice, modifica solo il leaf necessario e usa test mirati (`test_storage_heartbeat_policy` o test direttamente pertinenti). Niente suite globale. Un PASS non si ripete; una failure autorizza un solo fix mirato basato su nuova evidenza. Commit/push una volta dopo PASS. Se non serve codice, non creare modifiche artificiali.

8. Prima di dichiarare PASS verifica:
   - per 3 cicli schedulati consecutivi #39/#40 non compare più `No heartbeat in the time window`;
   - il runtime installato ha `.source-revision` uguale al commit Git che hai validato;
   - UUID `22E02106E020E1B1` è attribuito a mount/device preciso;
   - #40 è UP solo se il vero alert spazio è realmente rientrato; se lo spazio resta pericolosamente basso per dati che non puoi cancellare in sicurezza, resta correttamente DOWN e il task è BLOCKED;
   - #39 può restare DOWN per l'alert hardware `spd5118`, ma non per heartbeat mancante.

# Non-goal

Nessun innalzamento soglie, aumento timeout Kuma, esclusione arbitraria di filesystem/dischi, disabilitazione monitor, cancellazione di dati personali, fix del sensore `spd5118`, reinstallazione generale, update Fedora o audit generale.

# Stop

Solo dopo PASS completo:

`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 673914 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 673914`

`push_verified=git_push_exit_0` è terminale quando è stato necessario un push. Output massimo 7 righe: `RESULT`, `HEARTBEAT_CAUSE`, `HEARTBEAT_FIX`, `STORAGE_DEVICE`, `STORAGE_FIX_OR_BLOCKER`, `KUMA_NOW`, `RUNTIME_REV/TEST/PUSH`.
