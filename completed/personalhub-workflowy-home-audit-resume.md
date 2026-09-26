PROMPT_ID=669941 | project_id=49

# Goal

Riprendi ESATTAMENTE lo stato già implementato nel repo PersonalHub e chiudi questo intervento con il minimo lavoro necessario.

Devi completare/verificare tre risultati già quasi finiti:

1. jump universale `🔗` da qualunque entità PH a Workflowy;
2. spostamento dei vecchi pulsanti della barra orizzontale superiore della Home dentro il grid principale, presentati come tile/moduli;
3. Audit log visibile dalla Home e collegato alla fonte audit autorevole corrente.

NON rifare analisi già concluse e NON riprogettare queste feature.

# Starting point verificato

Repo:
`/home/daniele/projects/PersonalHub`

Branch corrente:
`chatgpt/workflowy-auto-jump`

Baseline verificata recente:
`9a8cac3d`

Prima fai solo:
- `git status --short --branch`
- `git fetch` mirato al branch corrente e `main`
- fast-forward/reconcile solo se necessario, senza perdere modifiche già presenti.

Il branch contiene già:

## Workflowy

- integrazione globale `Integra Workflowy`;
- API key salvata cifrata tramite Android Keystore;
- target predefinito `today`;
- dopo `Save` riuscito nelle impostazioni Workflowy la UI torna automaticamente alla schermata Settings;
- il campo API key torna vuoto dopo il salvataggio: è INTENZIONALE, per non riesporre il secret;
- azione `🔗` sulle entità PH;
- se esiste già un unico Workflowy link associato all'entità, `🔗` lo apre direttamente;
- questo percorso deve funzionare anche se successivamente manca la API key;
- se non esiste ancora un link, `🔗` crea un nodo Workflowy sotto `today`, usa l'ID restituito dall'API per derivare il deep link, collega il resource all'entità tramite Hub Context e apre Workflowy;
- se attach PH fallisce dopo la creazione remota, preserva il rollback del nodo Workflowy già implementato;
- non scegliere automaticamente tra più link Workflowy già associati;
- test/device helper esistente:
  `WorkflowyAutoJumpDeviceTest.kt`.

## Home

La vecchia barra orizzontale scorrevole dei pulsanti utility è stata rimossa.

Questi elementi devono apparire nel MEDESIMO grid verticale dei normali moduli, con tile coerenti:

- Context
- Tags
- Audit log
- Since when
- Data
- Settings

I moduli normali restano:
People, Timer, Places, Substances, WordPulse, Soldi.

L'indicatore piccolo dello stato auto-export NON faceva parte della vecchia barra da promuovere: può restare separato.

## Audit

È stato accertato che NON bisogna riattivare `hub_activity_log` quando Git Data è attivo.

Contratto architetturale da preservare:

- con Git Data attivo, Git History è la fonte audit durevole/autorevole;
- SQLite conserva `hub_git_history_index` come indice locale ricostruibile;
- i payload before/after durevoli vivono nella history Git;
- `hub_activity_log`, `history_audit_log` ecc. vengono esclusi dal tracking Git per evitare una ricorsione “history of history”;
- proiezioni/runtime tecniche come snapshot Timer sono escluse per evitare crescita enorme della history/DB.

Evidenza già verificata sul precedente device:
- `hub_activity_log`: ultimo evento 2026-09-19 07:07:23;
- `hub_git_history_index`: 13.706 eventi e aggiornato fino a 2026-09-26 18:22:28;
- entrambi gli store usano newest-first;
- Git History: `ORDER BY occurred_at DESC, id DESC`.

Il branch contiene già `HubAuditLogScreen.kt`:
- se Git Data è attivo deve leggere `GitHistory` / `hub_git_history_index`;
- se Git Data è disattivo può fare fallback al legacy `HubHistorySearchScreen`;
- NON duplicare gli eventi nei due store;
- NON riattivare `HubActivityCapture` quando Git Data è attivo.

Il registro deve essere esplicitamente esposto come tile `Audit log` nella Home.

# HARD RULE DEVICE

Per TUTTO il testing Android di questo task usa ESCLUSIVAMENTE il TCL reale.

TCL:
- modello `6102H`;
- è un device esclusivamente di testing e può essere modificato liberamente;
- NON disinstallare Telegram.

VIETATO per questo task:
- Pixel 8a;
- emulatori/AVD;
- qualunque altro device Android.

Non usare il Pixel nemmeno come fallback se un gate TCL fallisce.

Host/unit test sul Fedora sono consentiti.

# Esecuzione minima

1. Ispeziona solo i file già toccati e le dipendenze direttamente necessarie. Niente audit repo-wide.

2. Verifica compilazione/test host minimi:
   - `:core:hub-context:testDebugUnitTest`
   - eventuali test mirati Audit/Home già pertinenti
   - `:app:assembleDebug`
   - `git diff --check`

3. Verifica la Home sul TCL:
   - installa l'APK corrente con `adb -s <TCL>`;
   - preserva i dati dell'app salvo necessità reale;
   - conferma che la vecchia barra utility non esista più;
   - conferma nel grid principale tutti e 12 i tile:
     People, Timer, Places, Substances, WordPulse, Soldi,
     Context, Tags, Audit log, Since when, Data, Settings;
   - apri almeno Audit log e Settings e verifica back navigation.

4. Verifica Audit log:
   - se Git Data è attivo sul TCL, il registro DEVE leggere `hub_git_history_index`;
   - verifica newest-first con `occurred_at DESC, id DESC`;
   - confronta il timestamp del primo elemento UI con il massimo timestamp della fonte corrente;
   - non considerare `hub_activity_log` stale un bug quando Git Data è attivo;
   - se Git Data non è attivo sul TCL, testa il fallback legacy sul TCL e aggiungi/usa un test host mirato che dimostri la scelta corretta della fonte quando Git Data è enabled;
   - non abilitare/configurare Git Data solo per forzare questo test se richiederebbe credenziali o side-effect non necessari.

5. Workflowy E2E sul TCL:
   - assicurati che `Integra Workflowy` sia enabled;
   - target = `today`;
   - se la API key non è già configurata sul TCL, usa il secret canonico già esistente sul Fedora SOLO tramite un percorso secret-safe;
   - NON stampare, loggare, copiare in Git/report/prompt la API key;
   - se non puoi trasferire il secret senza esporlo, NON usare Pixel come workaround: lascia solo quel gate live BLOCKED e completa gli altri gate.

   Per il test live:
   - usa o crea UNA sola entità sintetica chiaramente riconoscibile sul TCL;
   - conferma che `🔗` sia disponibile;
   - tap `🔗`;
   - verifica creazione di un solo nodo sotto Workflowy `Today`;
   - cattura/verifica l'ID/deep link restituito senza esporre credenziali;
   - verifica che Workflowy Android si apra sul nodo corretto;
   - torna in PH;
   - verifica che lo stesso deep link sia persistito come resource Hub Context dell'entità;
   - tappa di nuovo `🔗` e verifica che riapra lo STESSO nodo senza crearne un secondo;
   - verifica quindi idempotenza del percorso già-linked.

   Dopo aver raccolto l'evidenza, elimina solo eventuali dati sintetici creati appositamente se la cleanup è sicura e non compromette la prova; non modificare dati personali non necessari.

6. Se trovi un bug direttamente in questi tre scope, applica il minimo fix e rilancia SOLO il gate pertinente.

7. Non fare:
   - refactor;
   - cleanup generale;
   - redesign;
   - migrazioni DB non necessarie;
   - modifiche Datasette;
   - modifiche Git Data non necessarie;
   - modifiche a moduli non coinvolti;
   - test Pixel/emulatore;
   - retry identici senza nuova evidenza.

# Git / chiusura

Quando tutti i gate eseguibili sono PASS:

- commit/push di ogni residuo sul branch corrente;
- usa il normale protocollo PH del repo per integrare il branch in `main`;
- prima dell'integrazione rispetta eventuale lock/fencing già previsto dal repo;
- se un altro executor possiede legittimamente il lock/integration phase, lascia il candidato pushed e segnala solo quel blocker;
- non sovrascrivere lavoro concorrente;
- dopo integrazione riuscita, elimina il branch temporaneo se previsto dal protocollo PH.

# Acceptance

PASS solo se:

- build/test host mirati PASS;
- testing Android effettuato SOLO sul TCL;
- Home non contiene più la vecchia barra utility e tutti i suoi pulsanti sono tile nel grid principale;
- `Audit log` è accessibile dalla Home;
- con Git Data enabled, Audit usa Git History e non il legacy `hub_activity_log`;
- Audit è newest-first;
- con Git Data disabled resta disponibile il fallback legacy;
- `Save` Workflowy mantiene la key cifrata, non la riespone e torna a Settings;
- `🔗` è disponibile sulle entità PH;
- senza link precedente: crea sotto Today → salva deep link → apre;
- con link già presente: riapre lo stesso nodo senza duplicarlo;
- nessun Pixel/AVD usato;
- risultato finale integrato secondo il protocollo PH oppure unico blocker di integrazione chiaramente documentato.

Stop appena questi acceptance criteria sono verificati.

Output finale massimo 7 righe:
`RESULT=PASS|BLOCKED|FAIL`
`HOST=PASS|FAIL`
`TCL_HOME=PASS|FAIL`
`AUDIT=PASS|FAIL`
`WORKFLOWY_E2E=PASS|BLOCKED|FAIL`
`GIT=INTEGRATED|CANDIDATE_PUSHED|FAIL`
`BLOCKER=<none|testo minimo>`