PROMPT_ID: 583174

project_id: 49
Recommended model: GPT-5.6 Terra
Reasoning: high
MegaVault: FAST

# Goal
Porta il modulo **Substances/Sostanze di PersonalHub a una versione affidabile e completa**, implementando integralmente i problemi e le migliorie emersi dall'audit precedente. Non limitarti a patchare superficialmente la UI: correggi le cause architetturali e sostituisci le parti del modulo che conviene riscrivere.

Questa è una **riscrittura controllata in-place di Substances**, non un nuovo progetto:
- conserva `personalhub.db` e l'architettura unificata di PersonalHub;
- conserva le infrastrutture comuni sane già esistenti;
- preserva e migra i dati reali;
- puoi riscrivere anche gran parte di `feature/sostanze` se necessario;
- modifica `core/database` solo quanto richiesto per consistenza, schema, query e migrazioni;
- niente refactor/cleanup estranei.

## Contesto e protocollo

Usa **MegaVault FAST**, Project ID `49`, come fonte iniziale.

Prima:
1. leggi `AGENTS.md` e il protocollo governante indicato dal progetto;
2. individua direttamente i file Substances/Sostanze e le infrastrutture condivise pertinenti;
3. NON riesplorare il repository globalmente se MegaVault/AGENTS e i file direttamente collegati sono sufficienti;
4. verifica lo stato corrente del codice perché alcuni problemi dell'audit potrebbero essere già stati corretti;
5. per ogni requisito già realmente risolto, non modificarlo;
6. espandi l'indagine solo quando una dipendenza concreta lo richiede.

Incrementa `version.txt` **esattamente di +1 una sola volta**.

## Principio architetturale obbligatorio

La UI NON deve essere il confine di sicurezza.

Tutti gli entry point che modificano Substances — UI, macro, widget presenti/futuri, notification action, import o altre API interne — devono convergere su un **command/domain layer unico**.

Esempio concettuale:

UI / macro / widget
→ command layer
→ validazione dominio
→ singola transazione DB
→ aggiornamento stato/notifiche

Non duplicare regole di business tra entry point.

Le operazioni almeno equivalenti a queste devono avere una sola implementazione autorevole:
- record intake;
- undo/delete/edit intake;
- create/update/archive/restore substance;
- stock adjustment / set stock;
- macro execution;
- interaction rules;
- prescriptions.

## 1. Integrità dati — PRIORITÀ MASSIMA

Elimina qualunque rischio di cancellazione indiretta della cronologia.

In particolare:
- non usare `INSERT OR REPLACE` per aggiornare entità parent;
- gli update di una sostanza devono essere veri `UPDATE`;
- preserva intake, stock adjustments, prescriptions, interactions, macro items e qualsiasi FK associata;
- mantieni FK e cascade solo dove semanticamente corretto;
- aggiungi i constraint DB utili per impedire quantità/frequenze/intervalli/unità/enumerazioni palesemente invalide;
- aggiungi uniqueness dove semanticamente necessaria, ad esempio per evitare duplicati di rule-target o macro-item;
- `notification_state` non deve lasciare orphan inconsistenti;
- seed/demo data non deve mai apparire automaticamente in un database reale;
- rimuovi ogni comportamento che possa aggiungere silenziosamente Pregabalin/Vitamin D/Psyllium/Ibuprofen/PrEP/Tadalafil o macro personali;
- rendi atomica e sicura l'inizializzazione.

Se serve una schema migration, deve essere non distruttiva e testata su DB preesistente.

## 2. Intake e scheduling terapia

Correggi integralmente il modello temporale.

Devono essere realmente rispettati:
- start date;
- end date;
- forever;
- PRN;
- frequency;
- dose;
- schedule esplicito.

Implementa veri **orari programmati delle dosi**, non semplicemente `24/frequency` dall'ultimo tap.

Deve essere possibile rappresentare almeno:
- una o più dosi a orari scelti;
- giorni specifici;
- intervalli/date di validità;
- terapia continua;
- PRN.

Struttura il modello in modo estensibile anche a cicli/taper senza introdurre complessità inutile se non necessaria ora.

Correggi:
- reset artificiale a mezzanotte;
- future therapy già considerate attive;
- terapie terminate ancora attive;
- frequency=0 interpretata erroneamente;
- stato `LATER`;
- stato `BLOCKED`;
- `TAKEN`;
- dose completion basata solo sul numero di righe invece che sulle quantità;
- phantom missed doses;
- missed dose future;
- timestamp fittizi a mezzanotte;
- applicazione retroattiva del regime corrente alla cronologia passata.

Il calcolo storico deve usare i dati/regime validi nel periodo corretto, senza reinterpretare arbitrariamente il passato.

## 3. Registrazione intake robusta

Prima di scrivere un intake valida atomicamente:
- sostanza attiva/non archiviata;
- terapia attiva nella data/ora;
- interaction blocks;
- scheduling;
- quantità valida;
- disponibilità stock se applicabile;
- idempotenza/duplicazione.

Il command deve restituire un risultato dominio esplicito: successo, blocco, warning, stock insufficiente, dose anticipata, duplicato, ecc.

Implementa protezione contro:
- double tap;
- retry;
- esecuzione macro duplicata;
- futuri widget che ritentano la stessa operazione.

Una dose anticipata deve richiedere una decisione esplicita dell'utente quando opportuno, non essere indistinguibile da una dose normalmente dovuta.

Permetti inoltre:
- quantità intake diversa dal default;
- inserimento manuale a data/ora scelta;
- modifica di un intake;
- eliminazione con conferma;
- eventuale nota/context/reason senza complicare inutilmente la UI.

## 4. Stock come ledger coerente

Elimina qualunque situazione in cui lo stock possa essere matematicamente falsificato.

Invariant obbligatorio:

`stock precedente + delta realmente applicato = stock nuovo`

Quindi:
- se non c'è stock sufficiente, non registrare una dose completa come se fosse stata sottratta;
- undo deve ripristinare esattamente ciò che era stato sottratto;
- adjustment negativo non deve clampare silenziosamente producendo un delta falso;
- adjustment zero non deve creare eventi inutili;
- mostra preview del risultato;
- aggiungi **Set stock to X**;
- ogni modifica manuale dello stock deve produrre ledger/audit;
- mostra adjustment history;
- segnala stock insufficiente;
- coverage/exhaustion deve rispettare start/end/schedule terapia.

Gestisci correttamente le unità.

Non assumere che `stockUnit` e `doseUnit` siano matematicamente intercambiabili.

Evita conversioni silenziose tipo `5 g → 5 mg`.

Se una conversione non è supportata, blocca l'operazione con errore chiaro anziché inventarla.

## 5. Interactions

Le interaction rules devono essere parte del domain layer e non aggirabili da PRN o macro.

Correggi:
- PRN che bypassa BLOCK;
- self-target;
- più BLOCK simultanei;
- expiry calcolata usando il blocco effettivamente più restrittivo;
- WARN distinto da BLOCK;
- durata zero/zero;
- duplicati.

UI completa per:
- vedere le regole;
- crearle;
- modificarle;
- eliminarle;
- scegliere WARN/BLOCK;
- scegliere target specifici oppure all-other-substances;
- capire quali blocchi sono attualmente attivi e perché.

Non etichettare WARN come blocco.

## 6. Macros

Una macro deve usare esattamente lo stesso `RecordIntake` command delle azioni individuali.

Quindi non può bypassare:
- interactions;
- schedule;
- stock;
- terapia;
- idempotenza.

Implementa gestione completa:
- create;
- rename;
- edit items;
- delete/archive;
- gestione sostanze archiviate;
- niente item duplicati della stessa sostanza salvo esista una semantica esplicita per farlo.

L'esecuzione deve restituire un risultato per ogni item e non mostrare “successo” se ha registrato solo una parte senza spiegazione.

Tap = azione intenzionale chiara.
Long-press non deve registrare accidentalmente la stessa macro.

## 7. Prescriptions

Rimuovi limitazioni arbitrarie tipo `take(3)`.

Implementa:
- qualunque sostanza;
- data selezionabile;
- quantità/unità corrette;
- refill interval valido;
- edit;
- delete;
- prevenzione duplicati accidentali;
- next refill;
- refill ricorrente, non una sola data;
- archived substances escluse dove appropriato.

Mostra informazioni utili nella cronologia.

Se compatibile col modello esistente, includi in modo semplice stato richiesto/ritirato e dati necessari al refill; evita overengineering.

## 8. Notifications

Ricostruisci la parte scheduling in modo affidabile.

Servono almeno:
- reminder dose;
- missed dose;
- interaction end;
- refill.

Le notifiche devono essere:
- programmate;
- cancellate/reschedulate quando cambia lo stato;
- ripristinate dopo reboot;
- ripristinate dopo app update;
- corrette dopo cambio timezone;
- corrette dopo cambio ora.

Gestisci i receiver necessari, inclusi dove pertinenti:
- `BOOT_COMPLETED`;
- `MY_PACKAGE_REPLACED`;
- `TIME_SET`;
- `TIMEZONE_CHANGED`.

Non dichiarare exact alarm senza una necessità e un'implementazione coerenti.

Correggi:
- alarm stale;
- missed dose mancante quando prima era LATER/BLOCKED;
- refill non ricorrente;
- archived substances;
- notification state non aggiornato;
- cleanup degli stati scaduti;
- scheduling di timestamp già passati;
- retry dopo errore;
- PendingIntent ID collision;
- notification permission denial.

Ogni notification utile deve avere un `contentIntent` che apra direttamente Substances o la sostanza pertinente.

Usa icone/label Android corrette e comprensibili.

## 9. History e performance

Non identificare una sostanza tramite il nome quando esiste l'ID.

Correggi tutte le query/history per usare identity stabile.

Implementa una History realmente utile:
- grouping temporale leggibile;
- search/filter essenziale;
- substance filter;
- edit/delete intake;
- timestamp/dose corretti;
- missed doses coerenti.

Evita:
- caricamento infinito di tutti gli intake;
- generazione di una riga sintetica per ogni dose mancante su anni di cronologia;
- rescansione dell'intera history ogni minuto;
- `O(days × history)` inutili.

Usa query aggregate/paginate e Flow mirati dove appropriato.

Il ticker temporale deve aggiornare solo ciò che dipende realmente dal clock.

Mantieni corretta la semantica delle date anche attraversando timezone: non reinterpretare arbitrariamente vecchi eventi vicino alla mezzanotte.

## 10. Import/export

L'Import UI deve effettuare un vero import del file scelto usando l'infrastruttura globale PersonalHub già esistente.

Collega correttamente il selected URI alla funzione reale equivalente a `DatabaseVault.importDatabase()` e al restart/refresh previsto dal progetto.

Requisiti:
- validazione DB;
- import atomico;
- rollback/fail-safe;
- messaggio successo solo dopo vero successo.

NON aprire semplicemente la schermata Database come falso “import”.

Non duplicare il sistema globale di backup/export.

Substances deve usare l'auto-export centralizzato già esistente (`DatabaseGate` / `HubAutoExport` o equivalente corrente).

Rimuovi:
- full export sincrono dopo ogni mutation;
- export di sola lettura all'apertura del modulo;
- doppio export;
- configurazioni cartella duplicate.

Elimina il porter legacy che:
- crea `sostanze.db`;
- cancella file estranei dalla cartella;
- sovrascrive in modo non atomico;
- viola il single-DB architecture.

PersonalHub deve continuare ad avere **un solo DB autorevole: `personalhub.db`**.

## 11. Archive

Implementa:
- archive;
- elenco Archived;
- restore.

Le sostanze archiviate non devono diventare irraggiungibili.

Devono essere escluse da intake/macros/reminders/refill dove semanticamente corretto, preservandone però tutta la cronologia.

## 12. UI/UX Substances v2

Dopo aver sistemato domain/data layer, riorganizza la UI.

Home suggerita:

- **Da prendere**
- **Più tardi**
- **Bloccate**
- **Assunte**
- **Al bisogno**

Una sostanza TAKEN non deve sparire.

La card intera non deve registrare accidentalmente una dose se l'utente può ragionevolmente aspettarsi che apra dettagli.

Crea una chiara **Substance detail screen** che concentri:
- stato;
- prossimo intake;
- record intake;
- stock;
- history;
- prescription;
- interactions;
- edit/archive.

Correggi inoltre:
- FAB globale ambiguo;
- ricerca condivisa accidentalmente tra tab;
- fixed 2-column grid quando inadatta;
- TopAppBar/tabs troppo dense;
- touch targets troppo piccoli;
- literal `...`, `+`, `!` usati al posto di icone/semantics corrette;
- banner import/export permanente;
- empty states;
- loading/error feedback;
- dialog che si chiudono prima del completamento reale della write;
- localizzazione italiana incompleta.

La UI deve essere responsive sia su Pixel che TCL.

## 13. Navigazione e stato

Quando l'utente lascia Substances e poi lo riapre, ripristina almeno l'ultima sezione/schermata utile invece di forzare sempre Home, coerentemente con il comportamento desiderato per i moduli PersonalHub.

Non usare solo stato Activity volatile se serve persistenza cross-Activity.

La versione mostrata dal modulo deve derivare dalla versione reale PersonalHub; elimina hardcode tipo `VERSION_NAME = "4"`.

Se mostri la versione nella UI, va in posizione secondaria/non invasiva.

## 14. Capsule/contracts

Esamina gli attuali `capsules/contracts`.

Se sono una astrazione realmente usata dal progetto, completa o riallinea Substances a quell'architettura.

Se invece sono residui incompleti e non servono al design corrente, rimuovili solo se puoi dimostrare che non hanno consumer.

Non mantenere architettura morta per inerzia.

## 15. Test obbligatori

Aggiungi test mirati, non test cosmetici.

Copri almeno:

1. edit substance preserva tutti i figli/FK;
2. insufficient stock non falsifica ledger;
3. undo ripristina quantità esatta;
4. double tap/idempotency;
5. macro rispetta BLOCK;
6. PRN rispetta BLOCK;
7. start/end/forever;
8. dose vicino a mezzanotte;
9. più interaction blocks simultanei;
10. archive/restore;
11. missed-dose logic;
12. schedule esplicito;
13. notification cancel/reschedule;
14. boot/timezone rescheduling dove testabile;
15. recurring refill;
16. import reale + failure/rollback;
17. migration DB precedente;
18. history per ID e non per nome;
19. unit handling;
20. seed demo assente.

Aggiungi inoltre test DAO/domain per le invarianti critiche.

Esegui i test più stretti prima; amplia solo se necessario.

Non lanciare suite distruttive contro l'app reale.

Rispetta integralmente i guardrail benchmark/test già presenti nel progetto.

## 16. Verifica runtime

Installa/aggiorna alla fine **l'app PersonalHub principale reale** sia su:

- Pixel;
- TCL.

Non installare al suo posto benchmark target o clone.

Verifica manualmente almeno:
- apertura Substances;
- creazione sostanza;
- modifica senza perdita history;
- intake;
- undo;
- stock insufficiente;
- Set stock;
- macro;
- interaction BLOCK;
- archive/restore;
- prescription;
- navigation restore;
- import UI fino al punto sicuro testabile;
- layout su entrambi i device.

Controlla inoltre su device:
- tab/top bar senza truncation grave;
- touch target menu;
- card layout;
- niente jank evidente con history;
- niente double tap causato da write/export lento.

Non effettuare import distruttivi del DB reale per dimostrare il test: usa fixture/temp DB o percorso isolato.

## Strategia di implementazione

Lavora in questo ordine:

1. data integrity + migration/tests;
2. command/domain layer;
3. intake/scheduling;
4. stock;
5. interactions;
6. macros;
7. prescriptions;
8. notifications;
9. history/performance;
10. import/export cleanup;
11. archive;
12. UI/navigation;
13. runtime verification.

Puoi sostituire codice legacy invece di stratificare workaround.

Preferisci codice semplice e invarianti esplicite.

NON:
- mantenere due motori di business paralleli;
- duplicare repository;
- creare un secondo DB;
- introdurre framework/librerie non necessarie;
- fare refactor globali;
- cambiare altri moduli salvo integrazione indispensabile;
- modificare protocolli/MegaVault senza necessità concreta.

## Token discipline

Ottimizza il consumo:
- parti dai path indicati da MegaVault;
- niente scansioni repo-wide preventive;
- niente riletture dello stesso file;
- usa search mirate solo per simboli/dependency concrete;
- non narrarmi l'esplorazione;
- non produrre lunghi documenti intermedi;
- non fermarti dopo ogni sottopunto per chiedere conferma;
- risolvi i problemi correlati nello stesso passaggio;
- esegui prima test specifici e solo dopo test più ampi;
- non inseguire warning fuori scope;
- fermati quando acceptance e verifiche sono soddisfatte.

## Acceptance

PASS solo se:

- nessuna modifica sostanza può cancellare history collegata;
- stock e ledger sono matematicamente coerenti;
- UI/macro e altri entry point usano lo stesso domain command;
- BLOCK non è aggirabile;
- scheduling rispetta date/orari reali;
- history non genera phantom data evidenti;
- archive è reversibile;
- prescriptions/macros/interactions sono gestibili;
- import importa realmente;
- export usa solo l'infrastruttura globale;
- legacy `sostanze.db` porter pericoloso è rimosso;
- notification lifecycle è coerente;
- seed personale/demo non appare in produzione;
- test critici passano;
- app principale aggiornata e funzionante su Pixel e TCL.

## Output finale

Rispondi in formato compatto:

PROMPT_ID=
STATUS=PASS|PARTIAL|BLOCKED
VERSION=
ROOT_CAUSES=
IMPLEMENTED=
MIGRATIONS=
TESTS=
PIXEL=
TCL=
REMAINING=

`PASS` solo se tutti i requisiti implementabili sopra sono completati e verificati.

Se trovi un requisito tecnicamente errato perché il codice corrente è già cambiato, non implementare una regressione: indicalo brevemente in `REMAINING`/`IMPLEMENTED` e applica l'equivalente corretto.

Commit e push su `main` solo dopo test e verifiche richieste.