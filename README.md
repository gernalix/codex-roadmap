# codex-roadmap

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

Repository dei prompt operativi Codex. Le regole generali di scope, efficienza, test, gestione side issue e stop sono in `/home/daniele/.codex/AGENTS.md`; questo README definisce solo il comportamento specifico della roadmap.

## Struttura Canonica

- `roadmap.md`: lista numerata e ordinata dei prompt pendenti, una riga per prompt, senza spiegazioni o regole operative.
- `spiegazioni.md`: tabella Markdown con esattamente una riga per ogni voce pendente di `roadmap.md`, nello stesso ordine.
- `prompts/*.md`: prompt pendenti, autosufficienti e compatti.
- `completed/*.md`: prompt completati con PASS.
- `tools/roadmap_guard.py`: entrypoint canonico per selezionare/finalizzare il primo pendente senza dipendere dallo stato del worktree locale.
- `tests/test_roadmap_guard.py`: test mirati del guard.

Ogni modifica alla roadmap deve mantenere coerenti `roadmap.md`, `spiegazioni.md`, prompt file e wikilink.

### Tabella obbligatoria di `spiegazioni.md`

La tabella deve avere esattamente queste colonne, in questo ordine:

`# | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt`

Regole:

- `#`: stessa numerazione di `roadmap.md`;
- `Prompt`: wikilink allo stesso file presente nella corrispondente riga di `roadmap.md`; preferire `[[prompts/nome]]` per non introdurre `|` aggiuntivi nella tabella Markdown;
- `Spiegazioni`: spiegazione semplice in linguaggio umano, senza duplicare acceptance criteria o dettagli tecnici non necessari;
- `Livello ragionamento`: deve rispecchiare esattamente il `reasoning=` dichiarato nel prompt; se cambia uno dei due, aggiornare anche l'altro nello stesso cambiamento;
- `Tipo prompt`: deve essere `Prompt` oppure `Goal`;
- numero di righe, ordine e identità dei prompt devono essere sempre 1:1 con `roadmap.md`.

## Tipo Prompt: Prompt vs Goal

### `Prompt`

Usare `Prompt` quando scope, punti di intervento, comportamento richiesto e verifica sono già delimitati. Codex deve privilegiare esecuzione diretta, letture mirate e diff minimo.

### `Goal`

Usare `Goal` quando il risultato è ampio, architetturale o cross-module/cross-system e richiede di scegliere internamente una sequenza di sottopassi. Un Goal non autorizza audit generali, redesign fuori scope o espansione illimitata.

Il heading interno `# Goal` non determina il valore della colonna `Tipo prompt`.

## Prompt Permanenti

Ogni prompt in `prompts/` deve essere eseguibile in una nuova sessione Codex. Può assumere solo:

1. il proprio contenuto;
2. il `project_id` dichiarato e i fatti risolvibili da MegaVault quando richiesto;
3. `/home/daniele/.codex/AGENTS.md` e questo README per l'orchestrazione roadmap.

Non deve dipendere da chat precedenti o altri prompt già eseguiti salvo dipendenza esplicita verificata. Quando serve evidenza storica, includere nel prompt solo i fatti decisivi.

Ogni prompt dovrebbe dichiarare, quando applicabile: `PROMPT_ID`, `project_id`, modello/ragionamento, modalità MegaVault, goal, starting point, non-goal, verifiche, acceptance, stop e output finale.

## Ordine e Nomi

L'ordine di esecuzione esiste solo in `roadmap.md`; `spiegazioni.md` ne copia ordine e numerazione.

- filename semantici e stabili; niente prefissi di ordinamento;
- quando cambia l'ordine, rinumerare solo `roadmap.md` e la colonna `#` di `spiegazioni.md`;
- `PROMPT_ID` è un identificatore casuale, non un ordinamento.

## Obsidian

- ogni prompt pendente in `roadmap.md` è un wikilink al file in `prompts/`;
- la riga corrispondente in `spiegazioni.md` linka lo stesso file;
- ogni prompt pendente linka `[[roadmap|Roadmap]]` e `[[spiegazioni|Spiegazioni]]`;
- `README.md` e `spiegazioni.md` devono linkarsi tra loro;
- non lasciare wikilink pendenti.

## Lettura e Finalizzazione Sicura

Il worktree locale di `codex-roadmap` può contenere modifiche dell'utente. Non usare stash/reset/checkout del worktree per leggere o chiudere un task.

Entry point canonico:

```bash
python3 tools/roadmap_guard.py select
python3 tools/roadmap_guard.py complete --prompt-id PROMPT_ID --dry-run
python3 tools/roadmap_guard.py complete --prompt-id PROMPT_ID
```

`select` esegue un solo fetch del branch canonico e legge `roadmap.md`, prompt selezionato e riga di `spiegazioni.md` direttamente da `origin/main`; non modifica il worktree locale.

`complete`:

- accetta solo il `PROMPT_ID` del primo pendente corrente;
- crea un worktree temporaneo detached da `origin/main`;
- sposta esclusivamente quel prompt in `completed/`, aggiorna `roadmap.md` e `spiegazioni.md`;
- verifica che lo staged diff contenga solo i quattro path task-owned attesi;
- committa nel worktree isolato e pusha con fast-forward normale `HEAD:main`, mai force;
- se il push è bloccato preserva il worktree isolato e restituisce il path per risoluzione esplicita;
- non ingloba dirt preesistente e non archivia task per somiglianza.

Prima di modificare questo workflow eseguire solo:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

## Esecuzione Del Primo Pendente

Quando l'utente chiede di eseguire la roadmap:

1. usare `python3 tools/roadmap_guard.py select` invece di stash/fetch/show ripetuti;
2. selezionare solo il primo prompt pendente;
3. usare i metadata restituiti e il contenuto del prompt selezionato;
4. se dichiara un `campaign_id`, eseguire le fasi consecutive compatibili; altrimenti un solo prompt;
5. non leggere, investigare o avviare prompt successivi;
6. usare modello, ragionamento, modalità MegaVault, scope e vincoli dichiarati;
7. se `Tipo prompt=Prompt`, seguire il percorso già prescritto; se `Goal`, pianificare internamente senza ampliare scope;
8. fermarsi a PASS, BLOCKED o FAIL.

### Regole di efficienza

- non leggere `/home/daniele/.codex/memories/MEMORY.md` se prompt selezionato + AGENTS/README + MegaVault pertinente contengono già i fatti necessari;
- consultare memoria/storia solo per una lacuna concreta dichiarabile;
- raggruppare letture/check indipendenti;
- riutilizzare risultati già verificati nella sessione finché lo stato non cambia;
- non ripetere status, schema discovery, test o comandi equivalenti senza nuova evidenza;
- non fare audit generale dei repository;
- partire da CODE_MAP/MegaVault/file indicati e ampliare solo su failure concreta;
- dopo acceptance PASS, finalizzare una volta con `roadmap_guard.py complete` e STOP.

## Campagne Continue

Il default è un prompt per sessione. Una sequenza è campagna continua solo se ogni prompt dichiara lo stesso `campaign_id` e metadata di fase compatibili.

1. ogni prompt resta autosufficiente e con scope proprio;
2. le fasi vengono eseguite in ordine;
3. il PASS intermedio è checkpoint interno;
4. BLOCKED o FAIL ferma subito la campagna;
5. per PersonalHub, la versione è unica per l'intera campagna: base una volta, target `base + 1`;
6. build/install/QA finali consolidati nella fase finale salvo esigenza di sicurezza;
7. se tutta la campagna passa, archiviare le fasi e rinumerare una volta;
8. se si ferma prima, lasciare invariata la roadmap.

## Dopo L'Esecuzione

Se il prompt normale selezionato termina con PASS:

1. eseguire `python3 tools/roadmap_guard.py complete --prompt-id PROMPT_ID --dry-run`;
2. se `ready`, eseguire lo stesso comando senza `--dry-run`;
3. verificare una sola volta il commit/push risultante;
4. non iniziare il prompt successivo.

Non ricreare manualmente la sequenza sposta/rimuovi/rinumera/commit salvo blocker del guard.

Se il prompt è BLOCKED, FAIL o non soddisfa acceptance:

- non spostare il prompt;
- non rimuovere la voce;
- non avanzare al task successivo;
- riportare il blocker e fermarsi.

## Manutenzione

- quando `roadmap.md` cambia, aggiornare sempre `spiegazioni.md` nello stesso cambiamento;
- `Spiegazioni` resta comprensibile senza gergo tecnico non necessario;
- `Livello ragionamento` e `reasoning=` devono restare sincronizzati;
- rivalutare `Tipo prompt` quando cambia materialmente scope/autonomia;
- consolidare prompt solo quando riduce davvero bootstrap/build/QA/tool-call;
- non ristrutturare o assorbire prompt attivamente in esecuzione;
- eventuali stash/branch locali storici non vanno cancellati per nome: ispezionarli una volta e rimuoverli solo se provatamente ridondanti.

## Launcher Minimo

```text
Esegui il primo task pendente di gernalix/codex-roadmap seguendo il README. Usa tools/roadmap_guard.py per selezione/finalizzazione, senza stash del worktree locale. Usa il livello ragionamento e il tipo indicati nella riga corrispondente di spiegazioni.md. Se il primo prompt dichiara una campagna continua, esegui nello stesso ordine tutte le sue fasi consecutive; altrimenti esegui un solo task e fermati.
```
