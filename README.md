# codex-roadmap

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

Repository dei prompt operativi Codex. Le regole generali di scope, efficienza, test, gestione side issue e stop sono in `/home/daniele/.codex/AGENTS.md`; questo README definisce solo il comportamento specifico della roadmap.

## Struttura Canonica

- `roadmap.md`: lista numerata e ordinata dei prompt pendenti, una riga per prompt, senza spiegazioni o regole operative.
- `spiegazioni.md`: una spiegazione in linguaggio umano per ogni prompt pendente, nello stesso ordine di `roadmap.md`.
- `prompts/*.md`: prompt pendenti, autosufficienti e compatti.
- `completed/*.md`: prompt completati con PASS.

Ogni modifica alla roadmap deve mantenere coerenti `roadmap.md`, `spiegazioni.md`, prompt file e wikilink.

## Prompt Permanenti

Ogni prompt in `prompts/` deve essere eseguibile in una nuova sessione Codex. Puo' assumere solo:

1. il proprio contenuto;
2. il `project_id` dichiarato e i fatti che Codex puo' risolvere da MegaVault quando il prompt lo richiede;
3. l'entrypoint generale `/home/daniele/.codex/AGENTS.md` e questo README per la sola orchestrazione roadmap.

Non deve dipendere da chat precedenti, frasi come "come discusso", o altri prompt gia' eseguiti, salvo dipendenza esplicita verificata prima di agire. Quando serve evidenza storica, includere nel prompt solo i fatti decisivi da riusare.

Ogni prompt dovrebbe dichiarare, quando applicabile: `PROMPT_ID`, `project_id`, modello/ragionamento consigliati, modalita' MegaVault, goal, starting point, non-goal specifici, verifiche, acceptance criteria, stop e output finale.

## Ordine e Nomi

L'ordine di esecuzione esiste solo nella lista numerata di `roadmap.md`.

- I filename dei prompt sono semantici e stabili; non usare prefissi/suffissi di ordinamento come `04-`, `09b1-`, `task-12-`.
- Quando cambia l'ordine, rinumerare solo `roadmap.md`; non rinominare i prompt.
- `PROMPT_ID` e' un identificatore casuale, non un ordinamento.

## Obsidian

Il repository deve restare navigabile come vault Obsidian:

- ogni prompt pendente in `roadmap.md` e' un wikilink al file in `prompts/`;
- ogni heading corrispondente in `spiegazioni.md` linka lo stesso prompt;
- ogni prompt pendente linka `[[roadmap|Roadmap]]` e `[[spiegazioni|Spiegazioni]]`;
- `README.md` e `spiegazioni.md` dovrebbero linkarsi tra loro;
- non lasciare wikilink pendenti a prompt rimossi, rinominati o spostati.

## Esecuzione Del Primo Pendente

Quando l'utente chiede di eseguire la roadmap:

1. sincronizzare lo stato canonico del repository, se necessario;
2. aprire `roadmap.md`;
3. selezionare solo il primo prompt pendente;
4. se il primo prompt dichiara un `campaign_id`, eseguire anche le fasi consecutive con lo stesso `campaign_id` secondo le regole campagna sotto;
5. altrimenti eseguire solo quel prompt;
6. non leggere, investigare o avviare prompt successivi;
7. usare modello, ragionamento, modalita' MegaVault, scope e vincoli dichiarati nel prompt selezionato;
8. fermarsi a PASS, BLOCKED o FAIL del prompt selezionato, oppure alla fine della campagna.

## Campagne Continue

Il default e' un prompt per sessione. Una sequenza consecutiva e' una campagna continua solo se ogni prompt partecipante dichiara lo stesso `campaign_id` e metadati di fase compatibili.

Regole:

1. ogni prompt resta autosufficiente e con scope proprio;
2. le fasi vengono eseguite in ordine nella stessa sessione;
3. il PASS di una fase intermedia e' solo checkpoint interno;
4. BLOCKED o FAIL ferma subito la campagna;
5. per PersonalHub, la versione e' unica per l'intera campagna: base una volta, target `base + 1`;
6. build/install/QA finali consolidati avvengono nella fase finale, salvo requisito di sicurezza diverso;
7. se tutta la campagna passa, spostare tutti i prompt della campagna in `completed/`, rimuovere tutte le voci, rinumerare una volta e aggiornare `spiegazioni.md`;
8. se la campagna si ferma prima, lasciare invariata la roadmap e riportare fase raggiunta e blocker.

## Dopo L'Esecuzione

Se il prompt normale selezionato termina con PASS:

1. spostare il file da `prompts/` a `completed/`, preservando il filename;
2. rimuovere la voce da `roadmap.md`;
3. rinumerare le voci rimanenti da `1` a `N`;
4. aggiornare `spiegazioni.md` nello stesso ordine;
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

- Quando `roadmap.md` cambia, aggiornare sempre `spiegazioni.md`.
- `spiegazioni.md` contiene esattamente una spiegazione per ogni prompt pendente, in ordine, comprensibile senza gergo tecnico non necessario.
- Le spiegazioni non duplicano acceptance criteria, vincoli di esecuzione o prove tecniche del prompt.
- Prima di aggiungere un prompt, valutare se consolidarlo con prompt pendenti solo quando riduce davvero bootstrap, build, QA o tool-call senza allargare impropriamente lo scope.
- Non ristrutturare, rinominare, riordinare o assorbire prompt attivamente in esecuzione.

## Launcher Minimo

```text
Esegui il primo task pendente di gernalix/codex-roadmap seguendo il README. Se il primo prompt dichiara una campagna continua, esegui nello stesso ordine tutte le sue fasi consecutive con lo stesso campaign_id e fermati al termine; altrimenti esegui un solo task e fermati.
```
