# codex-roadmap

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

Repository dei prompt operativi Codex. Le regole generali di scope, efficienza, test, gestione side issue e stop sono in `/home/daniele/.codex/AGENTS.md`; questo README definisce solo il comportamento specifico della roadmap.

## Struttura Canonica

- `roadmap.md`: lista numerata e ordinata dei prompt pendenti, una riga per prompt, senza spiegazioni o regole operative.
- `spiegazioni.md`: tabella Markdown con esattamente una riga per ogni voce pendente di `roadmap.md`, nello stesso ordine.
- `prompts/*.md`: prompt pendenti, autosufficienti e compatti.
- `completed/*.md`: prompt completati con PASS.

Ogni modifica alla roadmap deve mantenere coerenti `roadmap.md`, `spiegazioni.md`, prompt file e wikilink.

### Tabella obbligatoria di `spiegazioni.md`

La tabella deve avere esattamente queste colonne, in questo ordine:

`# | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt`

Regole:

- `#`: stessa numerazione di `roadmap.md`;
- `Prompt`: wikilink allo stesso file presente nella corrispondente riga di `roadmap.md`;
- `Spiegazioni`: spiegazione semplice in linguaggio umano, senza duplicare acceptance criteria o dettagli tecnici non necessari;
- `Livello ragionamento`: deve rispecchiare esattamente il `reasoning=` dichiarato nel prompt; se cambia uno dei due, aggiornare anche l'altro nello stesso cambiamento;
- `Tipo prompt`: deve essere `Prompt` oppure `Goal`, secondo le regole sotto;
- numero di righe, ordine e identità dei prompt devono essere sempre 1:1 con `roadmap.md`.

## Tipo Prompt: Prompt vs Goal

Entrambi sono task eseguibili e restano in `prompts/`; la classificazione descrive quanto autonomamente Codex deve pianificare il percorso.

### `Prompt`

Usare `Prompt` quando il task è già abbastanza prescrittivo: scope, punti di intervento, comportamento richiesto e verifica sono sufficientemente delimitati. Codex deve privilegiare esecuzione diretta, letture mirate e diff minimo, senza trasformare il task in una nuova fase di progettazione.

### `Goal`

Usare `Goal` quando il risultato è ampio, architetturale o cross-module/cross-system e richiede a Codex di scegliere autonomamente una sequenza di sottopassi pur restando entro scope, vincoli e acceptance del file. Un Goal non autorizza audit generali, redesign fuori scope o espansione illimitata.

Il heading interno `# Goal` di un file descrive l'obiettivo del task e NON determina il valore della colonna `Tipo prompt`.

Quando si crea o si modifica materialmente un task, rivalutare il tipo: non classificare automaticamente tutto come Goal solo perché il lavoro è grande, e non classificare come Prompt un task che richiede vere decisioni architetturali non già prescritte.

## Prompt Permanenti

Ogni prompt in `prompts/` deve essere eseguibile in una nuova sessione Codex. Puo' assumere solo:

1. il proprio contenuto;
2. il `project_id` dichiarato e i fatti che Codex puo' risolvere da MegaVault quando il prompt lo richiede;
3. l'entrypoint generale `/home/daniele/.codex/AGENTS.md` e questo README per la sola orchestrazione roadmap.

Non deve dipendere da chat precedenti, frasi come "come discusso", o altri prompt gia' eseguiti, salvo dipendenza esplicita verificata prima di agire. Quando serve evidenza storica, includere nel prompt solo i fatti decisivi da riusare.

Ogni prompt dovrebbe dichiarare, quando applicabile: `PROMPT_ID`, `project_id`, modello/ragionamento consigliati, modalita' MegaVault, goal, starting point, non-goal specifici, verifiche, acceptance criteria, stop e output finale.

## Ordine e Nomi

L'ordine di esecuzione esiste solo nella lista numerata di `roadmap.md`; `spiegazioni.md` deve copiarne esattamente ordine e numerazione.

- I filename dei prompt sono semantici e stabili; non usare prefissi/suffissi di ordinamento come `04-`, `09b1-`, `task-12-`.
- Quando cambia l'ordine, rinumerare `roadmap.md` e la colonna `#` di `spiegazioni.md`; non rinominare i prompt.
- `PROMPT_ID` e' un identificatore casuale, non un ordinamento.

## Obsidian

Il repository deve restare navigabile come vault Obsidian:

- ogni prompt pendente in `roadmap.md` e' un wikilink al file in `prompts/`;
- la colonna `Prompt` della riga corrispondente in `spiegazioni.md` linka lo stesso file;
- ogni prompt pendente linka `[[roadmap|Roadmap]]` e `[[spiegazioni|Spiegazioni]]`;
- `README.md` e `spiegazioni.md` devono linkarsi tra loro;
- non lasciare wikilink pendenti a prompt rimossi, rinominati o spostati.

## Esecuzione Del Primo Pendente

Quando l'utente chiede di eseguire la roadmap:

1. sincronizzare lo stato canonico del repository, se necessario;
2. aprire `roadmap.md`;
3. selezionare solo il primo prompt pendente;
4. leggere la sua riga in `spiegazioni.md` per verificare `Livello ragionamento` e `Tipo prompt` senza consultare righe successive;
5. se il primo prompt dichiara un `campaign_id`, eseguire anche le fasi consecutive con lo stesso `campaign_id` secondo le regole campagna sotto;
6. altrimenti eseguire solo quel prompt;
7. non leggere, investigare o avviare prompt successivi;
8. usare modello, ragionamento, modalita' MegaVault, scope e vincoli dichiarati nel prompt selezionato; la tabella deve essere coerente con questi metadata;
9. se `Tipo prompt=Prompt`, privilegiare il percorso operativo già prescritto; se `Tipo prompt=Goal`, pianificare internamente i sottopassi necessari senza allargare scope o acceptance;
10. fermarsi a PASS, BLOCKED o FAIL del prompt selezionato, oppure alla fine della campagna.

## Campagne Continue

Il default e' un prompt per sessione. Una sequenza consecutiva e' una campagna continua solo se ogni prompt partecipante dichiara lo stesso `campaign_id` e metadati di fase compatibili.

Regole:

1. ogni prompt resta autosufficiente e con scope proprio;
2. le fasi vengono eseguite in ordine nella stessa sessione;
3. il PASS di una fase intermedia e' solo checkpoint interno;
4. BLOCKED o FAIL ferma subito la campagna;
5. per PersonalHub, la versione e' unica per l'intera campagna: base una volta, target `base + 1`;
6. build/install/QA finali consolidati avvengono nella fase finale, salvo requisito di sicurezza diverso;
7. se tutta la campagna passa, spostare tutti i prompt della campagna in `completed/`, rimuovere tutte le voci, rinumerare una volta e aggiornare la tabella `spiegazioni.md`;
8. se la campagna si ferma prima, lasciare invariata la roadmap e riportare fase raggiunta e blocker.

## Dopo L'Esecuzione

Se il prompt normale selezionato termina con PASS:

1. spostare il file da `prompts/` a `completed/`, preservando il filename;
2. rimuovere la voce da `roadmap.md`;
3. rinumerare le voci rimanenti da `1` a `N`;
4. rimuovere la riga corrispondente da `spiegazioni.md`, rinumerare la colonna `#` e preservare lo stesso ordine di `roadmap.md`;
5. aggiornare i wikilink interessati;
6. commit e push del repository target, se modificato e previsto;
7. commit e push di `codex-roadmap`;
8. non iniziare il prompt successivo.

Se il prompt e' BLOCKED, FAIL o non soddisfa l'acceptance:

- non spostare il prompt;
- non rimuovere la voce da `roadmap.md`;
- non avanzare al task successivo;
- riportare il blocker e fermarsi.

## Manutenzione

- Quando `roadmap.md` cambia, aggiornare sempre la tabella `spiegazioni.md` nello stesso cambiamento.
- `spiegazioni.md` contiene esattamente una riga per ogni prompt pendente, nello stesso ordine e con la stessa numerazione.
- La colonna `Spiegazioni` resta comprensibile senza gergo tecnico non necessario e non duplica acceptance criteria, vincoli di esecuzione o prove tecniche del prompt.
- `Livello ragionamento` e il metadata `reasoning=` del file devono restare sincronizzati.
- `Tipo prompt` va rivalutato quando un task viene accorpato, separato o cambia materialmente scope/autonomia richiesta.
- Prima di aggiungere un prompt, valutare se consolidarlo con prompt pendenti solo quando riduce davvero bootstrap, build, QA o tool-call senza allargare impropriamente lo scope.
- Non ristrutturare, rinominare, riordinare o assorbire prompt attivamente in esecuzione.

## Launcher Minimo

```text
Esegui il primo task pendente di gernalix/codex-roadmap seguendo il README. Usa il livello ragionamento e il tipo indicati nella riga corrispondente di spiegazioni.md. Se il primo prompt dichiara una campagna continua, esegui nello stesso ordine tutte le sue fasi consecutive con lo stesso campaign_id e fermati al termine; altrimenti esegui un solo task e fermati.
```
