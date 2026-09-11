# codex-roadmap

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]] · [[STANDARD_PROMPT|Prompt standard Codex]]

Repository dei task operativi Codex. Le regole globali di scope, test, side issue e stop sono in `/home/daniele/.codex/AGENTS.md`; qui restano solo le regole specifiche della roadmap.

**Per una normale esecuzione leggere solo `Esecuzione: fast path`.** Le altre sezioni servono quando si modifica/manutiene la roadmap o quando il guard segnala un'incoerenza.

## Struttura canonica

- `roadmap.md`: lista numerata dei pendenti, una riga per prompt, nessuna spiegazione.
- `spiegazioni.md`: una riga per pendente, stesso ordine.
- `prompts/*.md`: task pendenti autosufficienti.
- `completed/*.md`: task completati con PASS.
- `STANDARD_PROMPT.md`: prompt canonico da copiare in Codex Desktop; va mantenuto aggiornato quando workflow o lezioni post-run cambiano.
- `tools/roadmap_guard.py`: selezione/finalizzazione canonica da `origin/main`, senza dipendere dal worktree locale.
- `tests/test_roadmap_guard.py`: test del guard.

`spiegazioni.md` usa esattamente:

`# | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt`

`#`, ordine e link devono essere 1:1 con `roadmap.md`; `Livello ragionamento` deve coincidere con `reasoning=` del prompt; `Tipo prompt` è solo `Prompt` o `Goal`.

## Contratto dei prompt

Ogni prompt deve poter partire in una nuova sessione usando solo il proprio contenuto, `project_id`/MegaVault quando richiesti, AGENTS e questo workflow. Non dipendere da chat precedenti salvo dipendenza esplicita verificabile.

Quando applicabile dichiarare: `PROMPT_ID`, `project_id`, modello, reasoning, MegaVault, goal, starting point, non-goal, verification, acceptance/stop e output finale.

- `Prompt`: percorso già delimitato; esecuzione diretta, diff minimo.
- `Goal`: risultato ampio/cross-component; Codex sceglie i sottopassi senza ampliare scope.
- Il titolo interno `# Goal` non determina `Tipo prompt`.
- Filename semantici stabili; `PROMPT_ID` non ordina i task.
- Ogni pendente linka `[[roadmap|Roadmap]]` e `[[spiegazioni|Spiegazioni]]`; niente wikilink pendenti.

### Scelta modello/reasoning

I valori `model=` e `reasoning=` nel prompt sono **indicazioni operative per il selettore di Codex Desktop**: non cambiano automaticamente il modello o il livello attivo, quindi l'operatore deve impostarli manualmente prima dell'esecuzione.

Regola minima per `reasoning=`:

- `low` per task lineari/meccanici **e per verifiche deterministiche già preparate**: file/comandi/acceptance già determinati, nessuna scelta architetturale, nessuna discovery generale e nessuna correzione prevista. L'uso di Git/systemd/ADB non richiede da solo `medium` se il task prescrive esattamente i comandi e il comportamento su PASS/failure; se emerge una failure non banale, il task successivo/correttivo può salire a `medium`;
- `medium` è il default quando Codex deve prendere decisioni durante l'esecuzione, diagnosticare failure ambigue, mantenere più invarianti/condizioni di stop, gestire blocker non deterministici, modificare più componenti o orchestrare più fasi con branching reale;
- `high` solo quando la difficoltà/rischio lo giustifica concretamente.

Regola modello: usa GPT-5.5 per task delimitati; passa a GPT-5.6 Sol quando il task è cross-module/architetturale, coinvolge schema/migrazioni/undo-audit/rischio dati o richiede ragionamento più robusto. Non abbassare reasoning solo per risparmiare token se aumenta il rischio di violare istruzioni esplicite o produrre retry/tool-call aggiuntivi.

## Prompt standard Codex Desktop

Il prompt canonico da copiare nelle normali sessioni Codex Desktop è in **`STANDARD_PROMPT.md`**. Prima dell'invio, impostare manualmente progetto Codex Desktop, modello e reasoning adatti al task.

`STANDARD_PROMPT.md` è parte del workflow, non semplice documentazione: se un cambiamento del guard/workflow o un'analisi post-run mostra che una regola generale può prevenire instruction-loss, workaround non autorizzati, discovery/retry inutili, spreco token o rischi operativi, il prompt standard va aggiornato nello stesso intervento quando applicabile.

## Esecuzione: fast path

Per eseguire il primo pendente, la **prima azione di tool** deve essere:

```bash
python3 tools/roadmap_guard.py select
```

Prima di `select` non servono `pwd`, `ls`, `git status`, `git pull`, `git fetch`, lettura MEMORY/storia o altri preflight della roadmap. `select` fa il fetch canonico e restituisce un **execution pack** con identità, modello, reasoning, MegaVault, tipo, eventuale `campaign_id`, `execution_contract` e `prompt_content` direttamente da `origin/main`.

Dopo `select`:

1. usa `prompt_content` come task completo;
2. **non rileggere** `roadmap.md`, `spiegazioni.md`, README o il file prompt separatamente, salvo incoerenza/blocker concreto;
3. non leggere/investigare prompt successivi;
4. non leggere MEMORY/storia salvo che `prompt_content` dichiari una lacuna concreta non risolvibile con AGENTS/MegaVault/source-of-truth pertinente;
5. usa starting point/CODE_MAP/file indicati; amplia solo su failure o lacuna concreta;
6. raggruppa check/comandi indipendenti nella stessa tool-call quando sicuro e riusa evidenza già verificata finché lo stato non cambia;
7. niente audit generale, retry equivalente, schema discovery ripetuta, test duplicati, cleanup/refactor fuori scope;
8. limita output/log/dump alla sola evidenza necessaria; per suite Python `unittest`, usa `-b/--buffer` quando stdout/stderr dei test non sono acceptance evidence, così il rumore dei test verdi viene scartato ma resta disponibile sulle failure;
9. test mirati prima; allarga solo se rischio o failure lo richiedono;
10. durante l'esecuzione **non inviare progress report narrativi**: usa direttamente i tool; scrivi testo intermedio solo per un blocker che richiede una decisione dell'utente;
11. termina a PASS, BLOCKED o FAIL e produci un solo report finale conciso.

Default: **un solo task per sessione**. Eseguire più fasi solo se il prompt selezionato dichiara `campaign_id` e le fasi consecutive sono compatibili.

### PASS

Quando possibile usa una sola tool-call shell:

```bash
python3 tools/roadmap_guard.py complete --prompt-id PROMPT_ID --dry-run && \
python3 tools/roadmap_guard.py complete --prompt-id PROMPT_ID
```

La risposta reale `status=completed`, `commit=<SHA>`, `push_verified=git_push_exit_0` è la prova canonica che il push della roadmap è riuscito. **Non** eseguire dopo `git status`, `git rev-parse`, `git ls-remote`, pull/fetch o verifiche equivalenti sulla roadmap e non sincronizzare il checkout locale solo per il report: `complete` usa intenzionalmente un worktree isolato, quindi il checkout locale può restare indietro.

Produrre il report finale richiesto e **STOP**. Non aprire il task successivo.

### BLOCKED / FAIL

Non archiviare, non rinumerare, non avanzare. Riportare solo blocker/evidenza utile e fermarsi.

## Sicurezza del guard

Il worktree locale può essere sporco: non usare stash/reset/checkout per selezionare o completare task.

`select` legge solo `origin/main` e non modifica il worktree.

`complete`:

- accetta solo il `PROMPT_ID` del primo pendente corrente;
- usa un worktree detached temporaneo da `origin/main`;
- sposta solo quel prompt in `completed/` e aggiorna roadmap/spiegazioni;
- consente nello staged diff solo i path task-owned attesi;
- commit + push fast-forward `HEAD:main`, mai force;
- considera il push verificato solo se `git push` termina con exit code 0 e restituisce `push_verified=git_push_exit_0`;
- su push bloccato preserva il worktree isolato e restituisce il path.

Prima di modificare guard/workflow eseguire solo:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

## Campagne continue

Una campagna esiste solo con stesso `campaign_id` e metadata compatibili. Ogni fase resta autosufficiente e ordinata; PASS intermedio è checkpoint; BLOCKED/FAIL ferma tutto. Build/install/QA comuni vanno consolidati nella fase finale quando sicuro. Per PersonalHub usare una sola versione per campagna (`base + 1`). Archiviare/rinumerare una volta solo a campagna interamente PASS.

## Manutenzione

Quando si modifica la roadmap:

- mantenere `roadmap.md`, `spiegazioni.md`, prompt e wikilink coerenti;
- `Spiegazioni` resta semplice e non duplica acceptance/dettagli tecnici;
- sincronizzare `reasoning=` e colonna `Livello ragionamento`;
- rivalutare modello/reasoning con la policy sopra quando cambiano i requisiti operativi del task;
- per task di sola verifica già preparata, preferire `GPT-5.5 + low` e riservare `medium` alla diagnosi/correzione se una failure concreta lo richiede;
- rivalutare `Tipo prompt` solo se cambia davvero autonomia/scope;
- consolidare task solo se riduce realmente bootstrap/build/QA/tool-call senza creare mega-task indipendenti;
- **riesaminare e aggiornare `STANDARD_PROMPT.md` ogni volta che serve**, soprattutto dopo modifiche al workflow/guard o quando un run reale rivela una lezione generale riutilizzabile; non lasciare che il prompt standard diverga dalle regole operative correnti;
- se una modifica al workflow rende obsoleto il prompt standard, aggiornarlo nello stesso intervento;
- non modificare/assorbire task attivamente in esecuzione;
- non cancellare stash/branch storici senza provarne la ridondanza.

## Launcher minimo

Scorciatoia compatta derivata dal prompt standard; in caso di divergenza prevale `STANDARD_PROMPT.md`.

```text
Esegui il primo task pendente di gernalix/codex-roadmap. Come prima tool-call esegui direttamente `python3 tools/roadmap_guard.py select`, senza MEMORY/storia né preflight `pwd/ls/status/pull/fetch` della roadmap. Usa l'execution pack come unica sorgente roadmap; non rileggere README, roadmap.md, spiegazioni.md o il prompt salvo blocker/incoerenza. Raggruppa check indipendenti quando sicuro, limita output e usa `unittest -b` quando stdout dei test non è acceptance evidence. Se c'è una campagna continua esegui solo le fasi consecutive consentite; altrimenti un solo task. Su PASS esegui dry-run + complete nella stessa tool-call quando possibile e considera `push_verified=git_push_exit_0` verifica canonica: niente controlli Git successivi sulla roadmap. Produci un solo report finale conciso e fermati.
```
