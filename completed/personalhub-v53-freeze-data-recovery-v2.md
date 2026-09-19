PROMPT_ID=155893 | RETRY_OF=583742 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STANDARD

# Goal
PersonalHub v53 sul Pixel 8a si freeza alla prima animazione quando si apre qualunque modulo; inoltre i dati storici sembrano assenti. Diagnostica via ADB, preserva i dati, trova la root cause e applica il fix minimo verificato sul device.

Il precedente 583742 è terminato BLOCKED solo per problemi del gate roadmap: nessuna diagnosi PH e nessuna modifica ai dati/app sono state eseguite. Riusa solo questa evidenza, senza ripetere audit della roadmap.

# Safety dati — prima di tutto
Prima di azioni che possano cambiare lo stato:
- vietati pm clear, uninstall, cancellazioni DB/prefs/files e migrazioni manuali distruttive;
- non reinstallare finché non hai stabilito che è sicuro;
- conserva, se tecnicamente possibile, una copia read-only di DB + WAL/SHM + file/prefs pertinenti via run-as o metodo equivalente.

# Esecuzione minima
1. Prima azione: claim con roadmap_start.py per 155893; continua solo su roadmap_status=running.
2. Usa adb devices -l e seleziona esplicitamente il Pixel 8a se ci sono più target.
3. Verifica package, Android, versionName/versionCode, PID e stato storage app. Determina se i dati sono davvero mancanti o invece presenti in DB/path/schema diverso, non caricati, filtrati o bloccati da migration/init.
4. Riproduci UN solo freeze con logcat focalizzato sul package/PID. Usa dumpsys/ANR solo se serve. Fermati al primo failure concreto utile.
5. Confronta solo il codice direttamente pertinente tra ultima versione funzionante e v53. Priorità: DB/init/migration/routing, navigation/Compose transition, coroutine/main-thread, DAO/repository.
6. Identifica la root cause e applica il minimo fix lossless. Niente refactor/cleanup fuori scope.
7. Test mirati soltanto: compile/build toccati + regression test pertinente. Se migration DB, prova esplicitamente apertura/migrazione dello schema precedente senza perdita righe.
8. Solo dopo safety DB verificata, installa la build sul Pixel e prova almeno due moduli diversi + accesso ai dati storici.
9. Se i dati risultano davvero cancellati, non inventarli: identifica causa e usa solo backup/autoexport/Git già noti e verificabili per un eventuale recupero sicuro.

# Efficienza
Niente esplorazione generale, comandi equivalenti, retry identici, audit post-PASS o problemi collaterali non bloccanti. Riusa risultati già verificati. Stop immediato quando gli acceptance criteria passano.

# Acceptance
PASS solo se:
- root cause provata;
- freeze risolto sul Pixel;
- almeno due moduli aprono;
- stato dei dati determinato con certezza;
- dati storici accessibili oppure perdita/percorso di recupero documentati;
- test mirati PASS;
- worktree coerente/pulito secondo le regole PH.

# Report finale
Prima riga esatta:
PROMPT_ID=155893
Poi solo:
RESULT=PASS|BLOCKED|FAIL
ROOT_CAUSE=<causa>
DEVICE=<device/android>
INSTALLED_VERSION=<versionName/versionCode>
DATA_STATUS=<stato>
FIX=<fix>
ADB_EVIDENCE=<evidenza decisiva>
TESTS=<test+esito>
COMMIT=<sha se applicabile>
REMAINING=<solo blocker reali>
