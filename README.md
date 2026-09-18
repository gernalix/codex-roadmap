# codex-roadmap

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]] · [[prompt-registry|Registro prompt]] · [[obsidian/Dashboards/Roadmap|Dashboard Obsidian]] · [[STANDARD_PROMPT|Esecuzione Codex]] · [[SQLITE_ROADMAP|SQLite]]

Coda di lavoro **solo per attività che richiedono Codex**: filesystem/toolchain locale, device/emulatore, VM, segreti/config runtime, servizi locali o altre risorse non disponibili nella normale chat. Se una modifica può essere completata direttamente sui repository remoti in chat, va fatta subito e **non** aggiunta alla roadmap.

## Source of truth

`roadmap.sqlite` è l'unica fonte autorevole dei metadati della roadmap. `roadmap.md`, `spiegazioni.md`, `prompt-registry.md` e `obsidian/` sono viste generate e **non vanno modificate manualmente** per cambiare stato, ordine, dipendenze, analisi o relazioni.

Codex registra gli esiti immediati tramite `roadmap_result.py` / `roadmap_finish.py`; il sync locale importa timestamp e metriche reali da `codex-usage`. ChatGPT aggiorna stato logico, analisi, modifiche di codice successive all’analisi, fix e relazioni tramite richieste strutturate in `mutations/inbox/`, applicate transazionalmente da GitHub Actions. Dettagli: [[SQLITE_ROADMAP|Roadmap SQLite]].

## Struttura
- `roadmap.sqlite`: source of truth.
- `roadmap.md`: vista generata dei soli pendenti/running.
- `spiegazioni.md`: vista generata semplice dei pendenti/running con stato, esecuzione, esito, analisi, fix, progetto, chat e dipendenze.
- `prompt-registry.md`: registro generato di tutti i PROMPT_ID.
- `obsidian/`: note generate per prompt/progetto e dashboard con wikilink, backlink e tag.
- `prompts/*.md`: task pendenti/running autosufficienti.
- `completed/*.md`: task conclusi con PASS.
- `falliti/*.md`: task conclusi con BLOCKED/FAIL/CANCELLED/UNKNOWN.
- `tools/roadmap_result.py`: scrittura terminale race-safe nel DB + archiviazione.
- `tools/roadmap_finish.py`: wrapper compatibile per PASS.
- `tools/import_codex_usage.py` + `tools/roadmap_sync.py`: import/backfill e riconciliazione automatica.
- `mutations/inbox/`: canale strutturato per gli aggiornamenti ChatGPT.

## Regola vincolante per `spiegazioni.md`

`spiegazioni.md` è scritto **per Daniele, non per uno sviluppatore**. Deve essere comprensibile anche a una persona che non sa nulla di programmazione Android, Linux, database o Git.

Questa regola è obbligatoria per ogni futura modifica del file:

- usa italiano quotidiano, frasi brevi e parole comuni;
- spiega **cosa cambierà concretamente per l'utente**, **perché serve** e **perché quel lavoro richiede Codex**;
- descrivi le dipendenze con nomi umani delle attività, non con sole catene di PROMPT_ID;
- non copiare nel file il linguaggio tecnico dei prompt;
- non inserire dettagli di implementazione come nomi di classi, funzioni, tabelle, file interni, comandi, percorsi, commit, formati interni o nomi di test;
- evita termini come schema, migration, runtime, branch, worktree, DAO, Room, FK, WAL, WorkManager, AVD, Gradle, systemd, API e simili;
- i nomi propri di prodotti o servizi, per esempio PersonalHub, Obsidian, Datasette, ActivityWatch, Fedora, GitHub, Uptime Kuma e MegaVault, possono restare;
- se un termine tecnico è davvero inevitabile, spiegalo immediatamente nella stessa frase con parole comuni;
- modello, livello di ragionamento e tipo di prompt possono restare nelle rispettive colonne perché sono dati operativi, non parte della spiegazione;
- prima di salvare una modifica, rileggi ogni riga chiedendoti: **“la capirebbe una persona che usa l'app ma non sa come è programmata?”** Se la risposta non è chiaramente sì, semplifica ancora.

I dettagli tecnici completi appartengono ai file in `prompts/`, non a `spiegazioni.md`. La semplicità di `spiegazioni.md` ha priorità sulla precisione implementativa: deve descrivere fedelmente il risultato, non il modo in cui il codice lo ottiene.

## Regola di ammissione — niente spirali
Un nuovo task entra in roadmap solo se soddisfa **entrambi**:
1. richiede davvero una risorsa locale non disponibile in chat;
2. risolve un bug/blocco, rischio dati, requisito funzionale o verifica indispensabile prima di una release.

Non creare task Codex per:
- micro-ottimizzare un helper/monitor/gate che ha già PASS;
- misurare il costo del prompt precedente;
- validare una micro-ottimizzazione appena introdotta da ChatGPT quando test statici/remoti sono sufficienti;
- investigare colli di bottiglia solo potenziali o senza impatto pratico osservato;
- ripetere un PASS con un helper “ancora più efficiente”;
- modificare soltanto repository/workflow/Actions GitHub quando ChatGPT può farlo direttamente tramite GitHub. Se serve prima un audit locale, Codex deve produrre un handoff strutturato e fermarsi lì.

**PASS chiude il sottosistema.** Un follow-up dopo PASS è ammesso solo con nuova evidenza concreta emersa nell'uso reale. Le ottimizzazioni marginali si riportano in chat e si fermano lì.

Quando due task dello stesso repo/campagna richiedono lo stesso checkout/build/emulatore e hanno failure domain compatibili, accorpa i gate nel task funzionale invece di creare un prompt di sola verifica separato. Non accorpare invece migrazioni/rischio dati con feature ordinarie se questo rende il failure domain ambiguo.

Quando due fasi consecutive della stessa campagna richiedono lo stesso device/emulatore, concentra la QA device non indispensabile alla prima fase nella prima fase successiva che deve già avviare quel target. La fase precedente resta host-only quando compile/test host forniscono sicurezza sufficiente.

## Contratto prompt
Ogni prompt deve bastare da solo insieme alle regole globali già caricate. Deve dichiarare almeno metadata, goal, starting point verificato, scope/non-goal, verification, stop e comando di finalizzazione. Vietati inventory/audit generali quando file/boundary sono già noti.

### Identità PROMPT_ID
- `PROMPT_ID` è sempre un numero canonico reale di **6 cifre**.
- Regola assoluta: **1 prompt materializzato = 1 ID unico e immutabile**.
- Qualunque nuova versione, retry o riscrittura di un prompt riceve un **nuovo** `PROMPT_ID`, anche se cambia pochissimo.
- Un ID già assegnato non viene mai riciclato, ereditato o riutilizzato per un task diverso.
- Per mantenere la genealogia si può usare `PARENT_PROMPT_ID=<vecchio_id>`; il vecchio ID resta storico e non torna attivo.
- Se viene scoperta una collisione storica in un prompt ancora pendente, il task resta pendente ma deve ricevere un nuovo ID prima dell'esecuzione.
- Prima di mantenere un prompt in `prompts/`, verifica il suo ID contro l'archivio delle esecuzioni in `gernalix/codex-usage/prompts/`.
- Se l'ID esiste, confronta il **testo storico realmente eseguito** con il prompt pendente: non basta confrontare il numero.
- Se è lo stesso prompt (o la stessa materializzazione), **non cambiare semplicemente ID per rilanciarlo**: rimuovilo dai pendenti e archivialo in `completed/` se l'esito è PASS, oppure in `falliti/` se l'esito è BLOCKED/FAIL/UNKNOWN.
- Un retry è ammesso solo quando è un follow-up materialmente diverso che incorpora nuova evidenza o rimuove il blocker; in quel caso il prompt originale resta archiviato e il follow-up riceve un nuovo ID, con `PARENT_PROMPT_ID` riferito al prompt fallito.
- Se invece l'ID esistente appartiene a un **prompt storico diverso**, è una collisione accidentale: il task corrente non è stato eseguito e riceve un ID libero; non usare `PARENT_PROMPT_ID` verso il prompt non correlato.
- La verifica va fatta contro l'archivio delle esecuzioni, non dedotta da `completed/`, dal risultato PASS/BLOCKED/FAIL o dalla sola cronologia della roadmap.
- `spiegazioni.md` deve mostrare esplicitamente il `PROMPT_ID` corrente di ogni task pendente.
- `spiegazioni.md` deve indicare anche **Progetto**, **Chat Codex** e **Dipendenze** per ogni task pendente.
- **Progetto**: usa il progetto Codex osservabile/inferibile dai rollout (`repo_project`/`repo_projects`) quando disponibile; altrimenti usa il repository/runtime canonico senza inventare etichette UI.
- **Chat Codex**: `Stessa chat di <ID>` solo quando è una continuazione diretta e il contesto precedente riduce davvero lavoro/tool-call; usa `Nuova chat` quando il task è autonomo, il contesto precedente è vecchio/pesante o il progetto cambia.
- **Dipendenze**: elenca soltanto prompt ancora presenti nella roadmap che devono essere conclusi prima; usa dipendenze dirette, non tutta la catena transitiva.
- Una dipendenza non implica automaticamente la stessa chat: ordine di esecuzione e riuso della sessione sono decisioni separate.

Tipi:
- **Prompt**: default. Usalo quando il lavoro è delimitato e può ragionevolmente concludersi in un singolo turno operativo, anche se tocca più componenti.
- **Goal**: usalo solo quando la persistenza multi-turn è concretamente utile al risultato (per esempio campagne seriali lunghe multi-repo o verifiche che devono proseguire attraverso continuazioni). Complessità o rischio, da soli, non giustificano Goal.

### Modello/reasoning
- GPT-5.6 Luna `low`: task semplici, localizzati o meccanici, gate deterministici, test/build/ADB mirati e implementazioni con soluzione evidente.
- GPT-5.6 Terra `medium`: **default** per il lavoro Codex non banale, inclusi debugging runtime già pre-localizzato, lifecycle, migrazioni/schema delimitati e audit guidati da scanner/test deterministici.
- GPT-5.6 Sol `medium`: solo quando la capacità aggiuntiva è concretamente utile, per esempio debugging ambiguo/difficile, decisioni architetturali, modifiche trasversali complesse o task ad alto rischio che Terra non gestirebbe con sufficiente affidabilità.
- `high`: solo con difficoltà concreta non gestibile bene a medium.

Una migrazione, un audit o un task lungo **non giustificano da soli Sol**. Prima riduci scope, discovery, round-trip e output tool; passa da Terra a Sol solo se resta complessità o rischio di ragionamento reale.

## Esecuzione manuale
Apri il primo file indicato da `roadmap.md`, imposta modello/reasoning dai metadata e incolla **solo quel file**. Non inviare meta-prompt, non far leggere roadmap/README/spiegazioni e non eseguire `select` nelle sessioni manuali.

Default: un task per sessione. Raggruppa letture/comandi indipendenti; non ripetere test PASS; retry solo dopo nuova evidenza o stato cambiato; stop immediato a PASS/BLOCKED/FAIL. Per build/comandi lunghi già avviati, preferisci una sola attesa bloccante. Se il tool richiede polling, usa intervalli di almeno 30 secondi salvo un evento concreto che giustifichi un controllo anticipato: niente loop da 5 secondi, polling ravvicinato o messaggi che riportano solo stato invariato.

## Diagnostica runtime a basso round-trip
Per task locali/VM/servizi, il costo principale è spesso il numero di round-trip modello↔tool, non i token uncached. Quindi:
- se prompt/starting point forniscono path, helper, unit, DB, monitor ID o schema già verificati, trattali come autoritativi e non rifare discovery generale;
- raggruppa nello stesso batch i controlli indipendenti; evita sequenze di micro-comandi quando una sola query/lettura mirata può rispondere;
- **worktree dirty non significa automaticamente `BLOCKED`**: fotografa una volta i dirty path e i file che il task o il fast-forward remoto toccherebbero. Se gli insiemi sono disgiunti e l'operazione resta deterministicamente sicura, procedi senza modificare il lavoro utente; blocca solo su overlap, divergenza o ambiguità concreta. Non usare stash/reset/checkout distruttivi per ottenere artificiosamente un worktree pulito;
- SQLite: non indovinare colonne. Se lo schema non è già noto, fai **una sola** `PRAGMA table_info`/schema query e poi la query corretta. Per WAL read-only usa helper del progetto o URI `mode=ro&immutable=1`, non tentativi `sqlite3 -readonly` destinati a creare `-shm`;
- se è già noto un helper privilegiato/canonico (SSH wrapper, installer Android, emulator facade, ecc.), usalo direttamente: niente probe preliminari con permessi insufficienti o reimplementazioni manuali;
- limita `rg`, `journalctl`, tree/XML/log e query a file/unit/finestra pertinenti; evita output da migliaia di token e output troncati. Un dump ampio è ammesso solo dopo failure concreta di una query stretta;
- usa subito l'invocazione test canonica già dichiarata (`PYTHONPATH`, cwd, serial, runner). Non eseguire prima una variante nota destinata a fallire per “provare”; dopo un failure cambia approccio usando la nuova evidenza, niente retry quasi equivalenti;
- dopo PASS dei criteri richiesti non fare audit, status o readback aggiuntivi “per sicurezza”.

**Ordine dei gate:** esegui sempre prima i controlli più economici e indipendenti dal device (static check/unit test/build), poi avvia emulatore/device/servizi solo se quei gate sono PASS. Se l'APK è già stato costruito nello stesso task, installa esattamente quell'artefatto senza una seconda invocazione Gradle. Fanno eccezione solo i test il cui prerequisito tecnico richiede esplicitamente il runtime prima del gate host.

**Disciplina dei retry Gradle:** un gate aggregato serve per scoprire problemi e per la conferma finale, non come inner loop. Se un gate aggregato fallisce:
1. leggi in una volta l'intero report disponibile del task/modulo fallito e raccogli tutti i blocker dello stesso failure domain;
2. applica i fix in batch quando indipendenti;
3. rilancia solo il leaf task fallito (`compile`, test mirato, `lint<Variant>` o modulo specifico), non l'intero `check`/`assemble`;
4. quando tutti i leaf failure sono PASS, esegui **un solo gate aggregato finale**.

Non rilanciare `./gradlew check ...` dopo ogni singolo lint/compile fix. Obiettivo normale: al massimo un gate aggregato di discovery + uno finale; un terzo è ammesso solo se il finale espone un failure domain realmente nuovo che non era presente nei report precedenti. Se il prompt è una fase intermedia e non richiede lint globale, preferisci test mirati + build dell'artefatto necessario e lascia il gate globale alla fase finale/release.

## Campagne
Usa `campaign_id` per più fasi dello stesso prodotto quando questo evita release ripetute.

Per PersonalHub:
- le fasi intermedie fanno implementazione, test mirati, eventuale QA isolata e push;
- **non** incrementano `version.txt`, non installano il package reale Pixel e non inviano APK;
- l'ultima fase fa un solo bump, gate finali consolidati, un solo APK finale, una sola installazione Pixel e una sola Telegram delivery;
- l'ultima fase non ripete automaticamente gate già PASS delle fasi precedenti: li riesegue solo se il diff finale tocca i file, dipendenze o boundary che quei gate coprivano;
- una campagna PH deve essere seriale: niente task PH concorrenti;
- le fasi PH non devono dipendere dall'esistenza di branch remoti temporanei. Se un task usa un branch locale/temporaneo per isolamento, deve integrarlo in `main` ed eliminarlo nello stesso task prima del PASS, salvo eccezione esplicita e motivata nel prompt;
- task di repository diversi possono essere eseguiti in parallelo solo quando non condividono checkout o runtime mutabili. `roadmap_finish.py` supporta il completamento out-of-order/race-safe; un task che modifica il checkout canonico MegaVault non va eseguito in parallelo con task che devono usare quello stesso checkout.

Non creare mega-task se le fasi hanno failure domains indipendenti; consolida build/install/delivery e gate comuni. Una verifica locale di fix già pushati va assorbita nella fase funzionale successiva dello stesso repo quando può condividere lo stesso host gate e la stessa QA.

## PASS
Ogni prompt normale finalizza con una sola invocazione race-safe:

```bash
python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id PROMPT_ID --confirm-executed
```

Il wrapper registra `PASS` in `roadmap.sqlite`, sposta il prompt in `completed/`, rigenera tutte le viste Markdown/Obsidian, committa e pusha in modo race-safe. Non anteporre un dry-run nel percorso normale e non eseguire audit aggiuntivi dopo il PASS.

Timestamp e metriche precise dell'esecuzione vengono poi riconciliati da `codex-usage`; la registrazione terminale immediata serve a chiudere correttamente la coda senza aspettare il sync.

## BLOCKED/FAIL
Un BLOCKED/FAIL è anch'esso terminale per quel PROMPT_ID: **non si rilancia lo stesso prompt**. Registra una sola volta:

```bash
python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id PROMPT_ID --result BLOCKED --confirm-executed
# oppure --result FAIL
```

Il prompt viene tolto dai pendenti e archiviato in `falliti/`. Se serve una correzione, ChatGPT crea un **nuovo PROMPT_ID** e lo collega al padre con relazione `fix` o `followup`. Il sync da `codex-usage` riconcilia comunque l'esito reale se la registrazione immediata non è riuscita.

## `roadmap_guard.py` / `roadmap_finish.py`
`roadmap_guard.py select` resta disponibile solo come fallback unattended/lettura. Con `roadmap.sqlite` presente, lo stato non deve essere avanzato modificando direttamente Markdown.

Usa:
- `roadmap_finish.py` per PASS;
- `roadmap_result.py` per PASS/FAIL/BLOCKED/CANCELLED/UNKNOWN;
- `roadmap_db.py` / mutazioni JSON per manutenzione strutturata;
- `roadmap_sync.py` per riconciliare le esecuzioni reali da `codex-usage`.

Prima di modificare il workflow:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 tools/roadmap_db.py --repo . verify
```

## Manutenzione
Quando aggiorni la roadmap:
- modifica il DB tramite API/helper/mutazioni strutturate; **non** editare manualmente le viste generate;
- ogni nuova materializzazione mantiene la regola assoluta 1 prompt = 1 PROMPT_ID unico;
- un prompt terminale resta storico; eventuali fix/follow-up usano un nuovo ID collegato al padre;
- conserva spiegazioni in italiano semplice: il testo sorgente è il campo `explanation` nel DB, poi `spiegazioni.md` viene rigenerato;
- mantieni dipendenze dirette, progetto, chat consigliata, modello e reasoning nel DB;
- non aggiungere task che ChatGPT può completare direttamente sui repo remoti;
- non assorbire task già in esecuzione;
- non usare la roadmap come backlog generico: deve restare una coda Codex minima e operativa;
- dopo una mutazione esegui `roadmap_db.py verify`; dopo PASS non creare ulteriori audit senza nuova evidenza.
