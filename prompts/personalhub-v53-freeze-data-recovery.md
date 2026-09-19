PROMPT_ID=583742

MODEL: GPT-5.6 Sol
REASONING: medium
MEGAVAULT_MODE: STANDARD

PersonalHub v53 sul Pixel 8a Android 17 è gravemente regressa:

- l'app parte;
- appena provo ad aprire QUALUNQUE modulo, resta bloccata/freezata durante la prima animazione di apertura;
- sospetto inoltre che i dati precedentemente presenti siano spariti/non vengano più caricati.

Indaga direttamente sul device via ADB, trova la causa reale e applica il fix minimo necessario nel repo PersonalHub.

## Priorità assoluta: preservare i dati

PRIMA di qualsiasi azione potenzialmente distruttiva:

- NON eseguire `pm clear`;
- NON cancellare database/preferences/files;
- NON disinstallare l'app;
- NON reinstallare sopra l'installazione esistente se questo rischia di alterarne lo stato;
- NON eseguire migrazioni manuali distruttive.

Considera i dati attualmente presenti sul device come evidenza da preservare.

Se possibile, crea prima una copia/read-only dello stato rilevante dell'app (DB + eventuali WAL/SHM + prefs/file pertinenti) tramite `run-as` o altro metodo sicuro consentito dal device/build.

## Procedura

1. Leggi solo il contesto strettamente necessario:
   - `AGENTS.md`;
   - documentazione MegaVault/PersonalHub direttamente pertinente;
   - manifest/versioning/database/navigation del repo.
   
   Niente audit generale del repository.

2. Identifica via `adb devices -l` il Pixel 8a Android 17 attualmente collegato e usa esplicitamente quel serial per tutti i comandi se esiste più di un device.

3. Conferma sul device:
   - package PH installato;
   - versionName/versionCode;
   - processo/PID;
   - directory dati disponibili;
   - database presenti e relative dimensioni/timestamp;
   - eventuali WAL/SHM;
   - preferences/files rilevanti.

4. Determina subito se i dati sono:
   - realmente assenti/cancellati;
   - ancora presenti ma DB sbagliato/non aperto;
   - presenti in un vecchio DB/schema/path;
   - nascosti da filtri/query;
   - non caricati per failure/migrazione/versioning.

Non assumere che “UI vuota = dati cancellati”.

5. Riproduci il freeze via ADB:
   - svuota solo il buffer `logcat`, NON i dati app;
   - avvia PH;
   - riproduci l'apertura di un modulo;
   - cattura logcat focalizzato sul package/PID e sugli errori Android rilevanti;
   - controlla crash, ANR, exception, deadlock/main-thread blocking, Compose/navigation, Room/SQLite, coroutine, migration e StrictMode se emergono;
   - usa `dumpsys activity` / process state / ANR diagnostics solo se utili.

Non raccogliere log enormi se il primo failure concreto è già evidente.

6. Confronta il comportamento con il codice introdotto tra l'ultima versione funzionante nota e v53. Parti dai file/componenti direttamente implicati dal failure osservato; amplia solo se necessario.

7. Individua la root cause, non aggirare il sintomo.

Particolare attenzione a regressioni recenti relative a:
- startup/database initialization;
- schema versioning/migrations;
- multi-database/database routing;
- navigation/module opening;
- animazioni/transizioni Compose;
- lifecycle/coroutine/main thread;
- repository/DAO che possono bloccare il rendering iniziale;
- modifiche che possono aver fatto puntare PH a un DB nuovo/vuoto invece di quello storico.

8. Applica il MINIMO fix necessario.

Vincoli:
- preservare compatibilità con il DB utente esistente;
- nessuna perdita dati;
- niente refactor/cleanup/modernizzazioni fuori scope;
- non correggere problemi collaterali non bloccanti;
- riusa risultati già verificati;
- niente retry identici senza nuova evidenza.

9. Verifica con test mirati:
   - build/compile dei componenti modificati;
   - unit/instrumentation test direttamente pertinenti se esistono;
   - installa la build corretta sul Pixel SOLO quando hai stabilito che è sicuro per i dati esistenti;
   - riapri PH;
   - verifica via ADB/device che almeno più moduli differenti si aprano senza freeze;
   - verifica che i dati storici risultino nuovamente accessibili.

Se serve una migrazione DB, aggiungi anche un regression test che dimostri l'apertura/migrazione dello schema precedente senza perdita di righe.

10. Se scopri che la v53 ha effettivamente cancellato dati, NON inventare dati e NON proseguire distruttivamente:
   - identifica esattamente quando/come sono stati cancellati;
   - cerca copie recuperabili già esistenti (DB autoexport/Git/backup) usando solo fonti note del progetto;
   - recupera solo se la procedura è verificabile e sicura.

## Git / scope

Segui le regole canoniche del progetto e di MegaVault.

Non creare branch temporanei inutili. Se il workflow corrente richiede un branch, completalo e integralo secondo le regole canoniche del repo; niente branch zombie.

Non modificare la roadmap salvo che emerga lavoro realmente Codex-only non necessario per chiudere questo bug.

## Stop condition

Termina immediatamente quando sono verificati tutti questi criteri:

- root cause identificata con evidenza;
- freeze risolto;
- almeno più moduli apribili sul Pixel;
- stato dei dati determinato con certezza;
- dati storici accessibili oppure causa/percorso di recupero documentati;
- test mirati PASS;
- working tree finale coerente/pulito secondo il workflow del progetto.

Nessun audit ulteriore dopo il PASS.

## Report finale conciso

La PRIMA riga deve essere esattamente:

`PROMPT_ID=583742`

Poi:

`RESULT=PASS|BLOCKED|FAIL`
`ROOT_CAUSE=<causa concreta>`
`DEVICE=<device/versione Android>`
`INSTALLED_VERSION=<versionName/versionCode>`
`DATA_STATUS=<presenti e recuperati | presenti ma non caricati | realmente mancanti | altro>`
`FIX=<modifica applicata>`
`ADB_EVIDENCE=<evidenza minima decisiva>`
`TESTS=<test eseguiti e risultato>`
`COMMIT=<hash se applicabile>`
`REMAINING=<solo eventuali blocker reali>`

Non raccontare cronologicamente l'esplorazione.
