PROMPT_ID=857906
/goal
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=STRICT
PROJECT_ID=49
REPO=gernalix/PersonalHub
DEPENDS_ON=140263

# Goal

Sostituisci tutte le UI user-facing di History/Log/Timeline di PersonalHub con UN solo motore canonico cross-module di cronologia delle modifiche + ricerca live, riusato sia globalmente sia dentro ogni modulo. Parti dall'attuale Registro attività globale già presente su main: evolvilo, non creare un secondo journal o una seconda search architecture.

La UI finale deve rispondere soltanto a “che cosa è cambiato nell'app?”, in linguaggio umano. Niente ID/UUID, tabelle, row key, colonne SQL, INSERT/UPDATE/DELETE, hash, autori tecnici, statistiche audit, bisect o controlli da database admin.

# Starting point verificato — non riscoprire

Current main contiene già la base del PROMPT_ID=835204:
- `core/database/.../HubActivityLog.kt`: `hub_activity_log` + DAO;
- `HubActivityCapture.kt`: bridge People/Timer/Places + capture selettiva di altri write root;
- `HubActivityUndo.kt`: undo compensativo append-only fail-closed;
- `app/.../HubActivityRegisterScreen.kt`: vecchia UI del registro;
- `app/.../HubTemporalSearchScreen.kt`: ricerca temporale di dati di dominio/episodi, concetto distinto dal change history;
- `app/.../capsules/settings/GitHistorySettings.kt`: la schermata tecnica “History & Time Machine” da eliminare come UI;
- `MainActivity.kt` oggi espone separatamente Search e Activity e sceglie GitHistorySettings quando Git data è abilitato.

Usa prima `.codex/CODE_MAP.tsv`, in particolare: `app.activity_register`, `hub.temporal_search`, `people.history`, `places.history`, `timer.timeline`, `wordpulse.root`, `substances.root`, `soldi.root`, `app.shell`, `app.settings`. Apri altri file solo da consumer-preflight o da un failure concreto. Niente audit repo-wide.

Il PROMPT_ID=140263 (Universal Since When) deve essere già terminale/PASS. Preserva la sua capability: se un'azione “Create Since When counter” vive in una legacy history eliminata, ricollocala nel nuovo percorso condiviso o nell'entity detail canonico senza duplicare il motore Since When.

# 1. Contratto unico degli eventi

Mantieni `hub_activity_log` come unica authority della cronologia delle modifiche. NON introdurre un secondo log/event store.

Evolvi il contratto interno, con naming coerente al progetto, in modo che ogni entry possa produrre almeno:
- event id interno stabile, mai mostrato;
- `occurredAt`;
- `moduleId`;
- azione semantica canonica (create/update/rename/delete/restore/archive/start/stop/record/link/unlink o equivalente);
- tipo di dato umano (tag, sessione, evento, transazione, luogo, visita, sostanza, intake, persona, setting, ecc.);
- riferimento interno all'entità, mai mostrato;
- subject/label umano dell'oggetto;
- lista di cambiamenti semantici `fieldLabel + beforeText + afterText`;
- status e reversibilità/undo policy;
- navigation target opzionale;
- testo ricercabile normalizzato costruito SOLO da contenuti human-facing rilevanti.

IDs, nomi di tabelle/colonne, payload encodati, cursor e dettagli di sync possono restare interni ma non devono diventare search/display text.

Ogni modulo può fornire un adapter/humanizer del proprio dominio, ma NON una propria UI/query/history engine. L'adapter traduce l'evento canonico in tipo, subject, titolo umano, diff Prima→Dopo, search text e target di navigazione.

Una singola azione utente che produce più write SQL deve apparire come UNA modifica semantica: usa/estendi correlation/grouping e sopprimi derived writes, cache e bookkeeping. Cattura tutte le mutazioni semanticamente significative dei dati utente; non trasformare sync/cache/telemetria interna in rumore della History e non journalizzare segreti.

# 2. Titolo umano autosufficiente

Ogni riga deve sembrare il titolo di un commit comprensibile senza aprire dettagli:
`<azione presente> <tipo dato> <identità/variazione concreta> · <modulo> · <EEE d/M/yy>`

Esempi di semantica, localizzati tramite resources:
- Rename tag “Shopping” to “Spesa” · Timer · Wed 24/09/26
- Change transaction “Netto” amount from 25 € to 27.50 € · Soldi · Wed 24/09/26
- Delete Timer session “Studio”, started at 14:32 · Timer · Tue 23/09/26

Quando before/after è utile e breve, includilo nel titolo. Se il diff è troppo ampio, il titolo resta autosufficiente e il tap espande un dettaglio semplice “Prima → Dopo”, sempre con label umane. Mai mostrare raw DB metadata.

Usa il formato data esatto `EEE d/M/yy` (M=mese). Weekday localizzato.

# 3. Unica UI History/Search condivisa

Crea/refactora un solo composable/screen host-owned, es. `HubHistorySearchScreen`, parametrizzato da scope immutabile:
- `ALL`
- `MODULE(moduleId)`

Non implementare un “filtro modulo nascosto”: lo scope MODULE deve essere un vincolo della query e non poter essere rimosso dallo state UI.

## Scope ALL — Home PH
La Home espone un solo pulsante/azione `🔍` per aprire questa schermata. Elimina la duplicazione Home “Search” vs “Activity register”: il `🔍` è la ricerca generale della cronologia modifiche.

## Scope MODULE — dentro ogni modulo
Ogni modulo user-facing corrente espone una sezione/azione Search/History che apre LO STESSO screen/codice con `MODULE(moduleId)`. In questo scope il filtro Modulo non compare.

Rispetta le capsule: le feature non devono importare implementazioni private di `:app`. Aggiungi/riusa un piccolo contract/deep-link pubblico host-owned (es. `personalhub://history?module=...`) e fai puntare gli entry point dei moduli a quel contract. Deriva i moduli supportati dalla registry/HubModule esistente, non mantenere una seconda lista manuale.

# 4. Filtri — tutti live, zero pulsanti Apply/Search

In alto mostra SOLO:
- intervallo date Da/A;
- filtro Moduli con checkbox multi-selezione, visibile solo in scope ALL, tutti selezionati di default;
- campo `🔍 Cerca nella cronologia…`;
- `Reset filtri` solo quando lo state differisce dal default.

Qualunque modifica a Da/A, checkbox o qualunque carattere digitato/cancellato aggiorna immediatamente i risultati. Nessun Apply, Conferma, Search/Submit.

Il filtro testuale cerca in TUTTI i campi testuali human-facing dell'entry, compresi subject, tipo, modulo, titolo, field labels e before/after anche se il dettaglio è collassato. Matching:
- case-insensitive;
- substring;
- accent/diacritic-insensitive;
- nessun match su raw ID tecnico salvo che quel valore sia davvero human-facing.

Per ~migliaia di entry deve restare fluido. Preferisci la soluzione più piccola affidabile su Room/SQLite; un debounce interno <=100 ms è ammesso solo se necessario e non deve essere percepibile. Non introdurre FTS o un secondo indice/store se una query/index semplice basta. Lo scrolling può paginare internamente ma NON mostrare un bottone “Load more”.

Default Reset: all-time, tutti i moduli, testo vuoto.

# 5. Riga e Undo

Layout volutamente minimale:
- titolo umano autosufficiente;
- a destra slot `↩️`;
- tap sul corpo: espande Prima→Dopo e/o consente di aprire l'entità quando esiste ancora;
- niente “Copy link”, ID, badge tecnici o controlli di debug nella riga base.

L'undo resta compensativo:
- non cancellare né riscrivere la history;
- verifica stato corrente;
- esegui inverse mutation;
- lascia che la capture aggiunga la nuova entry inversa;
- marca l'originale reverted solo dopo successo;
- stale/referenced/unsafe => fail closed.

Lo slot `↩️` deve esistere coerentemente su ogni riga. Abilitalo quando l'undo è sicuro; per legacy/non-reversible mostra stato disabilitato con ragione accessibile, non un'azione che fallisce silenziosamente. Per le normali nuove create/update/rename/delete conserva abbastanza before/after per rendere reversibili tutti i casi semanticamente sicuri.

Undo normale: tap → esecuzione → snackbar breve “Modifica annullata”. Chiedi conferma solo per una mutazione con conseguenze/cascade importanti. La nuova entry compensativa deve avere a sua volta un titolo umano (es. “Restore transaction amount from 27.50 € to 25 € …”).

# 6. Mappa di rimozione legacy

Rimuovi le UI/pipeline user-facing duplicate; NON cancellare i dati di dominio o i journal interni che servono come source.

### RIMUOVI / SOSTITUISCI
1. `GitHistorySettings.kt` come UI completa: filtri author/table/row/field/op, Apply filters, stats, bisect, Recent edits tecnici, Time Machine restore/compare/milestone/proposal. Rimuovi anche route/button `git-history` da Settings. Se `GitHistory` backend serve ancora a Git sync/recovery, resta backend non user-facing.
2. `HubActivityRegisterScreen.kt` come screen separato: refactoralo nel nuovo shared History/Search oppure eliminalo dopo consumer closure.
3. `MainActivity.kt`: elimina route/entry duplicate “activity” e il branch che sceglie GitHistorySettings in base a GitDataSettings. Home `🔍` apre sempre il nuovo engine.
4. People: elimina `ContactHistoryCapsule` e le UI/query state che servono SOLO a presentare una history parallela; conserva `contact_events`/audit semantic data se servono come source del log canonico. Le capability non-history eventualmente annidate vanno spostate nel detail/entity flow pertinente, non usate per tenere viva una seconda history.
5. Places: elimina la user-facing `ui/history/HistoryScreen.kt` e relativi componenti di timeline/history quando sostituiti. Non cancellare visite/place events. Funzioni uniche non-history (es. “Where was I”, edit entità, map navigation) vanno ricollocate nel luogo/domain screen appropriato o rese raggiungibili dal dettaglio della nuova entry.
6. Timer: elimina la user-facing Timeline/history capsule e `TaskHistoryDialog` se ancora raggiungibile, dopo aver spostato eventuali funzioni non-history indispensabili nel normale flow session/event. Non cancellare sessioni/eventi o motori Timer.
7. WordPulse: rimuovi il tab/surface Timeline user-facing; non cancellare parole/sessioni/metriche sottostanti.
8. Substances/Soldi: usando SOLO le righe CODE_MAP + un targeted reference search dei simboli di history/log/timeline, rimuovi eventuali surface cronologiche parallele; NON rimuovere le normali liste dati (es. transazioni/intake) solo perché ordinate per data.

Regola per casi ambigui: elimina ogni UI il cui scopo principale è “sfogliare una history/log/timeline”. Se quella UI contiene anche una capability di dominio unica, sposta SOLO quella capability nel posto naturale; non conservare il browser cronologico duplicato.

### PRESERVA
- dati canonici di sessioni, eventi, transazioni, visite, intake, persone, tags ecc.;
- `hub_activity_log`, capture e undo;
- audit source tables necessarie alla capture;
- log diagnostici interni non user-facing se ancora usati;
- `HubTemporalSearchScreen` SOLO nella misura in cui serve davvero a Context/episodi/ricerca per tempo di dominio: non è il nuovo `🔍` e non deve più presentarsi come ricerca generale. Se resta, ricollocalo sotto Context/episodi e rimuovi da lì qualunque duplicazione della change-history tecnica.

# 7. Regola architetturale futura

Codifica e documenta questa boundary:
- una sola History/Search UI/query engine globale;
- i moduli possono soltanto registrare/humanizzare eventi e aprire lo scope MODULE tramite contract pubblico;
- vietato aggiungere una nuova change-history UI/DAO/query per modulo.

Aggiungi un architecture/regression guard mirato che fallisca se i legacy entry point rimossi vengono reintrodotti o se una feature aggira il contract condiviso. Aggiorna solo le righe pertinenti di `.codex/CODE_MAP.tsv` e la sezione architetturale minima necessaria.

# 8. Migrazione / compatibilità

Riusa lo schema corrente quando possibile. Se per human diff/search text/reversibilità serve estendere `hub_activity_log`, fai UNA migrazione Room esplicita, non distruttiva, con schema export e test. Nessun reset DB, nessuna perdita della history esistente.

Le entry legacy devono restare consultabili: humanizzale al meglio con i dati disponibili; se un vecchio evento non contiene abbastanza payload per undo completo, non inventare valori e lascia `↩️` non disponibile con ragione.

Non bumpare `version.txt`: questo non è un task di final distributable/release.

# 9. Esecuzione a basso spreco

Prima azione:
`python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 857906`

Procedi solo se ottieni running e usa il worktree restituito come autoritativo.

Poi:
1. leggi AGENTS.md + le sole righe CODE_MAP sopra;
2. apri i file Starting point e i consumer esatti delle legacy surface;
3. fai consumer-preflight PRIMA di rimuovere/rinominare public symbols/DAO/API;
4. modifica per failure domain, senza repo audit/refactor/cleanup collaterali;
5. niente retry equivalente senza nuova evidenza;
6. dopo PASS di un gate non rieseguire audit/scan “per sicurezza”.

# 10. Test / acceptance

Test mirati obbligatori:
- humanizer: create/update/rename/delete/restore con subject e before→after;
- date `EEE d/M/yy`;
- text normalization case + diacritici + substring;
- date filter live;
- multi-module checkbox live;
- text input live per ogni keystroke, nessun Apply;
- scope MODULE non può mostrare altri moduli e non mostra module filter;
- query/search include hidden before/after human text;
- grouping: una user action con derived writes => una sola entry;
- capture semantica rappresentativa per ogni modulo corrente;
- undo create/update/rename/delete sicuri + compensating entry; stale/unsafe fail closed;
- legacy entry senza payload sufficiente resta visibile ma non inventa undo;
- no raw ID/UUID/table/row/column/backend encoding nella UI;
- consumer/architecture guard: legacy user-facing History/Log/Timeline routes rimosse e nessuna nuova implementation per modulo.

Esegui il compile gate minimo dei moduli toccati + `checkArchitectureBoundaries`. Per UI, usa il canonical Pixel_8a emulator e un solo QA mirato finale:
- Home `🔍` apre ALL;
- date/modules/text reagiscono live;
- una ricerca trova testo presente solo nel dettaglio before/after;
- undo sicuro produce entry compensativa;
- apri almeno due moduli differenti e verifica che entrambi aprano lo stesso screen in scope MODULE senza filtro modulo;
- verifica che i vecchi entry point history/timeline non siano più raggiungibili.

Nessun device fisico, release APK, Telegram o QA extra in questo task.

PASS solo se esiste UN engine/contratto, le legacy surface user-facing sono rimosse secondo la mappa, Home e moduli riusano lo stesso codice, filtri sono live, titoli sono umani/autosufficienti, undo è compensativo/sicuro e dati esistenti sono preservati.

Al PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 857906 --confirm-executed`

Per blocker/failure usa `roadmap_result.py` con lo stesso PROMPT_ID. Dopo il risultato terminale STOP: non aspettare integrazione/CI asincrona e non fare ulteriori audit.

Output finale max 10 righe:
PROMPT_ID
RESULT
SHARED_ENGINE
EVENT_CONTRACT
LIVE_FILTERS
LEGACY_REMOVAL
UNDO
MIGRATION
TESTS
BLOCKER
