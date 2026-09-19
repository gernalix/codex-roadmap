PROMPT_ID=518420 | PARENT_PROMPT_ID=155893 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Stabilizza PersonalHub dopo la regressione v55 con prove reali, non smoke superficiali. L'utente osserva:
- Timer impiega ~30 s ad aprirsi;
- Places crasha immediatamente all'apertura;
- Substances appare senza dati storici;
- Settings rende ambiguo il rapporto tra SQLite locale, SAF, Datasette e Git.

Esiste già la draft PR #18, branch `chatgpt/v55-stabilization-data-settings`, partita da main@764e2de e contenente:
- contratto esplicito: `personalhub.db` è l'unica source of truth runtime; SAF=backup/import esplicito; Datasette=replica outbound; Git=history outbound + restore/patch espliciti;
- Settings guidate e spiegazione dei secrets;
- rimozione di una lettura fast-path Timer duplicata;
- test di coesistenza trigger Datasette+Git.
Tratta PR #18 come starting point, non come soluzione già verificata. Puoi modificarla quanto serve.

# Safety dati
Il Pixel contiene dati reali. Prima di install/restore/import/migrazioni:
- identifica esattamente package/versione/profilo DB attivo;
- crea una copia coerente read-only di personalhub.db + WAL/SHM se possibile e verifica quick_check/FK;
- vietati pm clear, uninstall e cancellazioni dati sul Pixel;
- nessun restore/import remoto sul Pixel salvo che sia dimostrato necessario, lossless e verificato prima su copia/emulatore.
Sul TCL preserva eventuali dati esistenti prima di azioni distruttive. L'emulatore può usare fixture/DB isolati.

# Prima azione
Esegui il claim canonico:
`python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 518420`
Procedi solo con `roadmap_status=running`.

# Scope obbligatorio
## 1. Baseline forense v55 sul Pixel
Usa gli helper canonici ADB/UI/Perfetto di AGENTS.md. Raccogli una sola baseline mirata:
- Android/package/versione e active DatabaseProfile;
- path/dimensione/schema di personalhub.db;
- quick_check, FK e conteggi almeno per Places, Substances/intake_events e Timer session/snapshot;
- conferma se i dati Substances sono realmente assenti dal DB o solo non mostrati;
- riproduci una volta crash Places con logcat focalizzato;
- misura una cold-open Timer con StartupPerfTrace/Perfetto e identifica le sezioni responsabili del ritardo.

Non assumere che UI vuota = dati persi e non usare SAF/Datasette/Git come fonte di recupero prima di aver stabilito lo stato del DB locale.

## 2. Audit architetturale BOUNDED
Revisiona da cima a fondo soltanto il failure domain runtime/persistenza:
- startup/entrypoint di tutti i moduli mantenuti;
- owner del database e DatabaseProfile;
- SAF import/export;
- Datasette SyncJournal/uploader;
- Git tracking/sync/restore/patch;
- eventuale codice legacy Timer remote-sync ancora raggiungibile;
- Settings relative a dati/sync/secrets.

Parti da .codex/CODE_MAP.tsv e dai file già implicati; niente audit indiscriminato di UI/business logic non pertinente.

Invarianti da rendere vere e testate:
1. active `personalhub.db` = unica autorità runtime per tutti i moduli writable;
2. SAF non popola automaticamente l'app: export automatico, import solo esplicito/validato;
3. Datasette è solo local→remote e non contiene alcun percorso di hydration/replace locale;
4. Git background sync non sostituisce automaticamente il DB; restore completo e patch inbound sono azioni esplicite;
5. Git e Datasette possono essere entrambi attivi senza rimuovere trigger/journal l'uno dell'altro o creare loop;
6. nessun vecchio Timer remote-sync può diventare una seconda autorità;
7. cambiare DatabaseProfile cambia atomicamente tutti i moduli insieme.

Se trovi codice raggiungibile che viola queste invarianti, correggilo e aggiungi il regression test più vicino.

## 3. Fix regressioni reali
- PLACES: usa il crash reale per trovare la root cause; applica il minimo fix e un regression test.
- SUBSTANCES: confronta conteggi DB/DAO/UI e ripristina la visualizzazione dei dati storici senza seed/fabbricazione di righe. Se i dati mancano davvero dal DB attivo, determina prima dove/come sono stati persi e usa solo una fonte di recupero verificata e coerente.
- TIMER: usa la traccia per eliminare il/i collo/i di bottiglia reali. Mantieni il fix già presente in PR #18 solo se l'evidenza lo giustifica. Target: da force-stop a schermata Timer utilizzabile sul Pixel entro 5 s; mira a <3 s senza sacrificare integrity checks. Nessun lavoro pesante non indispensabile sul critical path.
- SETTINGS: completa/aggiusta la UI della PR #18 come wizard/guida. Deve spiegare in linguaggio utente ruolo, direzione dati e motivo di ogni credential prima di chiederla. Nascondi dettagli backend non necessari; mantieni opzioni avanzate solo dove servono.

## 4. Test seri, in questo ordine
Riusa gate PASS già validi; niente rerun ridondanti.

A. JVM/compile mirati:
- consumer preflight per API cambiate;
- test database/sync/data-flow;
- test dei fix Places/Substances/Timer;
- compile dei moduli toccati;
- checkArchitectureBoundaries.

B. Emulatore canonico:
- DB sintetico con dati non vuoti in People, Timer, Places, Substances, WordPulse e Soldi;
- avvia ogni modulo dalla Home/shortcut e verifica niente crash/ANR;
- verifica che i record preesistenti siano visibili;
- modifica almeno un record per i moduli direttamente interessati e verifica persistenza dopo restart;
- verifica Settings wizard;
- verifica data-flow: selezionare SAF non importa dati; Datasette OFF/ON non muta dati locali per effetto di lettura remota; Git sync normale non ripristina remote state; solo l'azione restore esplicita può sostituire il DB.

C. TCL:
- installa l'esatto APK candidato in sicurezza;
- smoke di Home + tutti i moduli mantenuti + Settings; nessun crash/ANR.

D. Pixel 8a Android 17:
- preserva DB reale prima dell'install;
- installa con helper canonico l'esatto APK candidato;
- Home + People + Timer + Places + Substances + WordPulse + Soldi + Settings;
- conferma dati storici reali visibili almeno in Places/Substances/Timer dove esistono nel DB;
- 3 cold-open Timer misurati: nessuno >5 s e mediana <3 s, oppure documenta con evidenza se una soglia hardware inevitabile richiede un valore leggermente superiore e continua a eliminare lavoro evitabile;
- almeno 10 minuti di navigazione/mutazioni leggere senza crash/ANR;
- verifica post-test quick_check/FK e che i conteggi critici non siano diminuiti inaspettatamente.

Non considerare PASS il semplice “activity launched”.

# Git/integrazione
- lavora sul branch PR #18; correggilo in-place;
- incrementa version.txt UNA sola volta da 55 a 56 per questo task;
- usa test mirati prima di ampliare;
- quando branch-local PASS, push PR #18;
- acquisisci il lease solo per integrazione/shared-device QA/release;
- aggiorna main una volta, fai semantic integration review contro main corrente, poi merge;
- elimina il branch dopo merge;
- costruisci, installa e pubblica ESATTAMENTE l'APK 56 che ha superato i gate, secondo AGENTS.md.
Se main avanza, riconcilia solo differenze sovrapposte; niente restart/audit generale.

# Stop conditions
PASS soltanto se TUTTO è vero:
- root cause Places identificata e crash eliminato;
- Substances storico spiegato e visibile/correttamente recuperato;
- Timer startup entro le soglie sopra o con evidenza equivalente non evitabile;
- invarianti SQLite/SAF/Datasette/Git provate da test;
- Settings guidate e comprensibili;
- emulator + TCL + Pixel matrix PASS;
- DB Pixel integro prima/dopo;
- PR #18 integrata in main, branch rimosso;
- APK 56 testato è quello installato/pubblicato.

BLOCKED solo per vero blocker esterno/safety non recuperabile. Failure di compile/test/logcat/ADB/config/helper è evidenza da correggere in-scope, non motivo automatico di BLOCKED.

# Token/tool discipline
Niente dump repo-wide, niente test equivalenti, niente retry identici, niente refactor fuori failure domain, niente audit dopo PASS. Riusa output/trace già verificati. Il report finale deve essere conciso.

# Report
Prima riga: `PROMPT_ID=518420`
Poi:
`RESULT=PASS|BLOCKED|FAIL`
`ROOT_CAUSES=<Places; Substances; Timer>`
`DATA_AUTHORITY=<contratto verificato>`
`PIXEL_DATA=<before/after integrity+critical counts>`
`TIMER_PERF=<3 cold opens + median>`
`DEVICE_MATRIX=<emulator/TCL/Pixel>`
`SETTINGS=<wizard/data flow result>`
`TESTS=<targeted gates>`
`PR=<#18 status>`
`COMMIT=<main sha>`
`APK=<56 artifact/release>`
`REMAINING=<only real remaining blockers>`
