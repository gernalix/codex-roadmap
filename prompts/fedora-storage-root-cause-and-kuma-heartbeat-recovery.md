PROMPT_ID=673914 | project_id=15 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST

# Goal

Ripristina alla radice gli heartbeat `Fedora Host` #39 / `Fedora Storage` #40 e diagnostica con precisione il vero alert storage, senza mascherare nessuno dei due problemi. Il task deve chiudere anche se l'alert storage richiede una decisione dell'utente: in quel caso lascia il monitor correttamente DOWN e restituisci `STORAGE_ACTION_REQUIRED` con device/mount/GiB necessari, invece di bloccare l'intera roadmap.

# Starting point autoritativo

- repo/workdir canonico: `/home/daniele/projects/fedora-system-monitor`, MegaVault project `15`;
- `main` include il fix `90f28f9` che invia anche `storage` nel heartbeat `minute` e il deploy runtime-only `scripts/deploy-runtime.sh` hardenizzato fino a `1fea2b3aad8fe776ec150ca959b75a8cc7f0d178` o successivo;
- deploy helper: checkout pulito, copia atomica in `/usr/local/libexec/fedora-system-monitor`, `.source-revision`, pre/post `config-check` + `db-check`, rollback su failure;
- alle 06:40 locali del 2026-09-16 Kuma #40 riceveva `storage: collectors complete; active alerts=1`, ma ~07:02 #39/#40 mostravano di nuovo `No heartbeat in the time window`;
- alert storage reale già provato: `filesystem.free_percent`, severity `emergency`, valore `2.7927%`, device id `fsuuid:22E02106E020E1B1:view:de538a637dd86975bf64`;
- #40 ha `interval=480s`: non aumentarlo e non disabilitare il monitor;
- #39 ha anche un alert hardware reale `spd5118`/`sensor.alarm`: non risolverlo qui, ma elimina il solo errore heartbeat.

Prompt autosufficiente: NON leggere README/roadmap/spiegazioni/MEMORY/MegaVault e non fare audit repo-wide salvo blocker concreto.

# Esecuzione minima

1. Dal workdir canonico fai una sola fotografia Git. Se pulito: `git fetch --prune origin && git pull --ff-only origin main`; registra lo SHA di `origin/main` come base. Se non è fast-forwardabile pulitamente, BLOCKED.

2. Raccogli UNA fotografia runtime raggruppata e bounded:
   - `fedora-system-monitor-fast.timer`, `fedora-system-monitor-collect@fast.service` e `list-timers` filtrato;
   - journal SOLO delle unità pertinenti, finestra ~06:35 locali→ora oppure ultimi 30 min, mai boot dump globale;
   - ultimi `collector_runs` `minute`/`five_minute` e alert attivi dal DB locale;
   - `/usr/local/libexec/fedora-system-monitor/.source-revision` + presenza della policy runtime `minute`→`storage`;
   - UNA lettura remota Kuma #39/#40 (ultimi ~10 heartbeat) tramite `/home/daniele/projects/vm_oracle/scripts/oracle_ssh.sh`;
   - mappa UUID `22E02106E020E1B1` con `lsblk`/`findmnt`/`blkid` a device, mountpoint, filesystem, capacità e free reale.

3. Determina la causa concreta del heartbeat mancante: timer/service, lock/deadline, push/rete/credenziali, runtime obsoleto/divergente o altro leaf provato. Correggi SOLO quella causa. Se serve deploy usa esclusivamente `sudo scripts/deploy-runtime.sh`; `scripts/install.sh` è fuori scope.

4. Storage: una sola scansione stretta dei principali consumatori **sullo stesso filesystem**. Puoi eliminare solo cache/temp/log chiaramente rigenerabili e non personali. Non eliminare/spostare media, archivi, backup, VM, progetti o dati incerti.
   - Se esiste cleanup sicuro e ovvio: libera il minimo utile e misura una volta di nuovo.
   - Altrimenti non improvvisare: calcola GiB necessari per >5%, >10%, >20% e per l'isteresi completa (>22% se applicabile), identifica i maggiori consumatori per categoria/path di primo livello e restituisci `STORAGE_ACTION_REQUIRED`.

5. Verifica heartbeat con al massimo UN collect manuale come smoke iniziale e poi **2 cicli schedulati consecutivi** reali. Niente polling manuale ravvicinato: una singola attesa abbastanza lunga o controlli radi. Fai UNA lettura Kuma finale per #39/#40.

6. Se emerge un bug source: leaf patch + test direttamente pertinente (`test_storage_heartbeat_policy` o equivalente), niente suite globale. Prima del commit/push fai UNA `git fetch origin`; se `origin/main` è avanzato dalla base, BLOCKED senza rebase/merge. Altrimenti commit/push una volta. Se non serve codice, niente commit artificiale.

# Acceptance

PASS se:
- la causa heartbeat è provata e #39/#40 ricevono heartbeat in 2 cicli schedulati consecutivi;
- runtime `.source-revision` corrisponde al commit validato quando c'è stato deploy;
- UUID storage è attribuito a device/mount preciso;
- storage è **o** rientrato in sicurezza **o** diagnosticato fino a un'azione utente concreta (`STORAGE_ACTION_REQUIRED`) senza nascondere l'alert;
- #39 può restare DOWN solo per il reale `spd5118`; #40 può restare DOWN solo per il reale spazio insufficiente.

Un alert reale rimasto visibile NON rende il task BLOCKED se diagnosi, quantità da liberare e prossima azione sono complete. BLOCKED solo se manca accesso/evidenza necessaria per diagnosticare o ripristinare gli heartbeat.

# Non-goal

Nessun innalzamento soglie/timeout, esclusione filesystem, disabilitazione monitor, cancellazione dati personali, fix `spd5118`, reinstallazione generale, update Fedora o audit generale.

# Stop

Dopo PASS tecnico, prova `roadmap_guard complete --prompt-id 673914 --dry-run`; se ready esegui il complete reale. Se il task non è più selezionato solo perché la roadmap è avanzata ma l'implementazione è già pushata, usa `reconcile --prompt-id 673914 --result PASS` dry-run + `--confirm-executed`. Qualunque altro errore guard => BLOCKED.

Output massimo 7 righe: `RESULT`, `HEARTBEAT_CAUSE`, `HEARTBEAT_FIX`, `STORAGE_DEVICE`, `STORAGE_RESULT`, `KUMA_NOW`, `RUNTIME_REV/TEST/PUSH`.
