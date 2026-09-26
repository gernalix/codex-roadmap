Completa autonomamente tutta la parte PersonalHub ancora realmente aperta nella C2.

SCOPE
- Lavora SOLO su PersonalHub e sui work item C2 necessari alla sua chiusura.
- Repo: `/home/daniele/projects/PersonalHub`.
- Control plane: `/home/daniele/projects/codex-roadmap`.
- `roadmap.sqlite` / `work_items` è la fonte canonica dello stato C2.
- Usa il reale PROMPT_ID a 6 cifre assegnato a questa esecuzione; non inventarlo e non usare placeholder.
- Modello e reasoning sono metadati esterni: non modificarli né inserirli nel prompt/checkpoint.

PRIMA DI MODIFICARE
1. Leggi:
   - `/home/daniele/projects/codex-roadmap/AGENTS.md`
   - `/home/daniele/projects/codex-roadmap/operations/task-state/README.md`
   - `/home/daniele/projects/PersonalHub/AGENTS.md`
2. Sincronizza codex-roadmap solo tramite il meccanismo guarded previsto dal repo.
3. Interroga `work_items` e individua tutti i work item PersonalHub non terminali.
4. Considera il vecchio `CHATGPT-20260924-PERSONALHUB-P0` già terminale: non rifare lavoro P0 già verificato.
5. Riconcilia eventuali vecchie proiezioni `state:*`/task-state che risultino stale rispetto alla C2 canonica; non trasformarle in nuovo lavoro senza evidenza.
6. Crea/usa una sola lane protetta PersonalHub tramite il repository single-writer. Non modificare direttamente `main`.

SET INIZIALE GIÀ IDENTIFICATO
Come minimo risultavano ancora aperti questi work item; rileggili dalla C2 prima di agire perché lo stato può essere cambiato:
- `wi:61d05a0b3e7f4651b17be8c3f5ea5257` — KT-71420 production.
- `wi:a99670bf017e4962822b9c8765ebd178` — KT-71420 nei test.
- `wi:b3c7c89500754d8c929a3a7076a200a1` — nullability `DatabasePreferences`.
- `wi:cad05c039f464596aafa11ea15283496` — CODE_MAP Git Data/History.
- `wi:e7e578ba356a475e89857d53cd04b673` — INTERNET solo nell'androidTest di `core:database`.
- `wi:a75becd338ea44138e78281f3d5af267` — cleartext localhost solo nell'androidTest.
- `wi:754f0b89b1b3427e93b97d85219d4914` — instrumentation failure che può produrre falso exit 0/PASS.
- `wi:5c4748d2131a46a3b1ecb41cacd16206` — `GitDataRestoreDeviceTest` e DatabaseGate frozen/restart contract.

Se esistono ulteriori work item PH canonici realmente azionabili, includili. Non creare duplicati.

STRATEGIA RISPARMIA-TOKEN
- Parti da `.codex/CODE_MAP.tsv`; poi usa ricerche mirate per simbolo/path.
- Niente audit repo-wide salvo evidenza concreta che la mappa sia insufficiente.
- Accorpa modifiche strettamente correlate nello stesso ciclo.
- Ordine preferito:
  1. fix Kotlin/nullability + CODE_MAP;
  2. manifest androidTest INTERNET/cleartext;
  3. fix fail-closed dell'instrumentation;
  4. fix `GitDataRestoreDeviceTest`;
  5. test host mirati;
  6. test Android fisici, prima Pixel e poi TCL solo quando utile/necessario;
  7. integrazione e chiusura C2.
- Non fare refactor, cleanup, modernizzazioni o miglioramenti fuori scope.
- Nessun retry identico senza nuova evidenza.
- Dopo PASS non aggiungere audit/test ridondanti.
- Riusa risultati già verificati.
- Se scopri un bug/collo di bottiglia PH o C2 direttamente causato dal lavoro corrente, registralo in C2; correggilo subito solo se necessario alla chiusura corrente, altrimenti crea il minimo work item separato e continua.

DISPOSITIVI ANDROID — HARD REQUIREMENT
Per tutto il testing device-facing usa ESCLUSIVAMENTE dispositivi fisici, in questo ordine di preferenza:

1. Pixel 8a.
2. TCL 6102H quando serve un secondo dispositivo, quando il test è distruttivo/rischioso per il Pixel, oppure quando il Pixel non è temporaneamente utilizzabile.

NON usare l'emulatore Android per nessun test di questo goal.

Regole:
- Pixel è il target principale di acceptance.
- TCL è il target secondario/fallback e può essere usato liberamente per testing.
- Quando è utile, esegui lo stesso gate prima sul Pixel e poi sul TCL; non duplicare test senza ragione.
- Per test potenzialmente distruttivi, preferisci TCL prima di rischiare dati o configurazione del Pixel.
- Non sostituire un test richiesto esplicitamente sul Pixel con un PASS sul TCL.
- Non avviare AVD/emulatori.
- Non usare `android_emulator_control.py`.
- Ignora eventuali vecchie istruzioni/checkpoint che richiedono `Pixel_8a AVD` o `emulator-5554`: per questo goal sono supersedute da questa regola.
- Se un test esistente è scritto come emulator-only, adattane il minimo necessario per renderlo sicuro su dispositivo fisico oppure verifica la stessa acceptance attraverso un test fisico equivalente. Non avviare l'emulatore come scorciatoia.
- Mantieni le safety guard per dispositivi fisici; non indebolirle per far passare i test.
- Se più device sono connessi, ogni comando ADB deve avere seriale esplicito.
- Risolvi i seriali correnti tramite i helper/preflight canonici: non assumere che gli endpoint Wi-Fi ADB restino invariati.
- Non usare mai ADB unscoped.

PIXEL — PROTEZIONE DATI
- Non distruggere o alterare inutilmente la normale installazione PersonalHub o il DB reale dell'utente.
- Per test che possono essere isolati, usa test APK, package separati, database temporanei o fixture.
- Mai `adb uninstall`, `pm clear`, clear-data, destructive fallback o sostituzione del DB live senza che il task richieda esplicitamente un cutover dati e senza rollback verificato.
- Se serve installare un APK PH sul Pixel, usa gli helper canonici descritti in `PersonalHub/AGENTS.md`.
- Non modificare il DB reale solo per far passare un test.
- Preserva ogni safety gate esistente relativo al Pixel.

TCL
- Il TCL è dedicato al testing e può essere modificato liberamente quando necessario.
- È consentito installare/disinstallare build di test, cancellare dati PH di test e modificare lo stato dell'app sul TCL.
- Non disinstallare Telegram dal TCL.
- Usa comunque seriale ADB esplicito.

IMPLEMENTAZIONE
Applica il cambiamento minimo necessario per ciascun work item.

In particolare:
- elimina KT-71420 tramite type arguments espliciti/minimi fix senza cambiare semantica;
- correggi `DatabasePreferences` in modo null-safe senza cambiare il comportamento;
- aggiungi UNA sola entry semantica CODE_MAP per Git Data/History/restore con sorgenti e test canonici;
- INTERNET e `usesCleartextTraffic=true` devono esistere esclusivamente nell'harness `androidTest` necessario, senza modifica della policy production;
- rendi i gate instrumentation fail-closed: `INSTRUMENTATION_FAILED`, runner failure, uninstall/setup failure o equivalente non possono essere classificati PASS solo perché Gradle stampa `BUILD SUCCESSFUL`/exit 0;
- nel restore test rispetta il contratto prodotto: dopo restore il DatabaseGate resta frozen fino al restart. Verifica il DB sostituito tramite SQLite raw/read-only o altro percorso che non riapra il grafo Room frozen nello stesso processo.

TEST
Esegui soltanto i test necessari in escalation:

1. compile/test host mirati sui file modificati;
2. regression test del wrapper/gate instrumentation;
3. `checkArchitectureBoundaries` se richiesto dalle modifiche a manifest/harness;
4. test Android interessati sul Pixel fisico;
5. test aggiuntivi sul TCL solo quando danno copertura utile, servono per un test più distruttivo o il Pixel non è adatto;
6. verifica esplicita che i gate considerino PASS solo un'esecuzione realmente riuscita.

NON usare emulatori in nessuna fase.

Non avviare più copie dello stesso Gradle/device command. Per comandi lunghi conserva lo stesso PID/log handle e continua a leggerlo.

Quando una vecchia acceptance C2 dice esplicitamente “AVD”, “Pixel_8a AVD” o `emulator-5554`, interpreta il requisito funzionale sottostante e portalo sui dispositivi fisici secondo la priorità Pixel → TCL, senza usare l'emulatore.

C2 E CHECKPOINT
- Non scrivere direttamente `roadmap.sqlite`.
- Usa esclusivamente writer/control-plane canonici.
- Mantieni un solo checkpoint operativo `operations/task-state/<PROMPT_ID>.md` con:
  Objective, Constraints, checklist eseguibile, Current step, Verified facts, Decisions, Completed, Remaining, Blockers, Evidence, Acceptance criteria, un solo `Next action`.
- Commit + push dei checkpoint dopo risultati importanti, test costosi, cambi di piano e prima di operazioni rischiose.
- Aggiorna separatamente ogni work item C2 con evidenza sufficiente; non dichiararlo completo solo perché una modifica simile è stata fatta.
- Se un work item è già risolto dal `main` corrente, dimostralo con test/diff/evidenza e terminalizzalo senza rifare l'implementazione.
- Se trovi task/checkpoint che richiedono ancora emulatori per questi work item, aggiornane lo stato/acceptance operativa per riflettere il nuovo vincolo fisico Pixel → TCL.

INTEGRAZIONE
- Mantieni una sola lane PersonalHub.
- Commit/push solo modifiche relative a questi task.
- Usa il repository single-writer/integrator previsto.
- Non bypassare hook/protezioni.
- Non creare PR manuali se il protocollo le genera.
- Quando `finish` accoda l'integrazione asincrona, non consumare token facendo polling.
- Salva checkpoint e termina quella esecuzione.
- Riprendi lo stesso goal soltanto quando C2/supervisor fornisce una reale transizione di stato.
- Dopo l'integrazione, verifica solo ciò che il protocollo richiede per terminalizzare i work item.

DEFINITION OF DONE
La parte PH della C2 è chiusa solo quando:
- tutti i work item PersonalHub canonici realmente attivi sono `completed`/`waived` con evidenza, oppure esiste un blocker esterno reale registrato;
- nessuno degli 8 problemi iniziali resta aperto;
- i warning richiesti sono eliminati;
- production non ha acquisito INTERNET/cleartext per effetto dei test;
- il gate instrumentation è fail-closed;
- il restore rispetta il restart contract;
- i test host mirati PASS;
- l'acceptance Android rilevante PASS sul Pixel fisico;
- eventuali test supplementari utili sul TCL sono PASS;
- nessuna acceptance di questo goal dipende da emulatori;
- le modifiche sono integrate nel `PersonalHub/main` tramite il protocollo canonico;
- C2 e checkpoint riflettono lo stato effettivo;
- non rimane lavoro PH azionabile non gestito.

Se incontri un blocker reale su un dispositivo:
- prova prima a completare gli altri task indipendenti;
- se il Pixel è temporaneamente indisponibile e il test non richiede specificamente il Pixel, usa TCL;
- non ricadere sull'emulatore;
- persisti il blocker con evidenza e lascia un solo `Next action`.

OUTPUT FINALE
Conciso:
- work item PH completati;
- commit/main integrato;
- test eseguiti sul Pixel e risultato;
- test eventualmente eseguiti sul TCL e risultato;
- conferma che non è stato usato alcun emulatore;
- eventuali blocker residui;
- stato finale C2 PH.

Non ripetere log lunghi né descrivere esplorazioni già documentate.

## Steering successivo per questa esecuzione
- Usa PROMPT_ID canonico 553232, non 107210.
- Usa solo dispositivi fisici: Pixel 8a prima, TCL solo se utile; nessun emulatore/AVD per acceptance.
- Integra i work item PH, poi consegna APK finale minificato e firmato, DB reale piu fresco e compatibile con rollback, entrambi installati sul Pixel.
- Verifica Home, moduli/dati e piu campioni di startup cold sul Pixel; registra tempi ordinati nella C2/checkpoint.
- Riduci drasticamente il DB preservando i dati e il rollback.
- Accelera evitando attese procedurali non necessarie; conserva i vincoli di sicurezza sui dati Pixel.
