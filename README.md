# codex-roadmap

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]] · [[STANDARD_PROMPT|Esecuzione Codex]]

Repository dei task operativi Codex. Le regole globali di scope, test, side issue e stop sono in `/home/daniele/.codex/AGENTS.md`; qui restano solo le regole specifiche della roadmap.

## Struttura canonica

- `roadmap.md`: lista numerata dei pendenti, una riga per prompt, nessuna spiegazione.
- `spiegazioni.md`: una riga per pendente, stesso ordine.
- `prompts/*.md`: task pendenti **autosufficienti e direttamente incollabili in Codex**.
- `completed/*.md`: task completati con PASS.
- `STANDARD_PROMPT.md`: descrive il fast path diretto e il fallback unattended; non è più un wrapper da incollare nelle normali sessioni manuali.
- `tools/roadmap_guard.py`: selezione unattended e finalizzazione canonica da `origin/main`, senza dipendere dal worktree locale.
- `tests/test_roadmap_guard.py`: test del guard.

`spiegazioni.md` usa esattamente:

`# | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt`

`#`, ordine e link devono essere 1:1 con `roadmap.md`; `Livello ragionamento` deve coincidere con `reasoning=` del prompt; `Tipo prompt` è solo `Prompt` o `Goal`.

## Contratto dei prompt

Ogni prompt deve poter partire in una nuova sessione usando **il solo contenuto del proprio file**, oltre alle regole globali già caricate da Codex e alle fonti esplicitamente autorizzate dal task. Non deve dipendere da un launcher generico, dall'output di `roadmap_guard.py select` o da chat precedenti.

Quando applicabile deve dichiarare: `PROMPT_ID`, `project_id`, modello, reasoning, MegaVault, goal, starting point verificato, scope/non-goal, verification, acceptance/stop, finalizzazione roadmap e output finale.

Ogni pendente deve inoltre contenere una breve istruzione di esecuzione diretta: non eseguire `select`, non rileggere roadmap/README/spiegazioni e usare il file stesso come specifica autoritativa.

- `Prompt`: percorso già delimitato; esecuzione diretta, diff minimo.
- `Goal`: risultato ampio/cross-component; Codex sceglie i sottopassi senza ampliare scope.
- Il titolo interno `# Goal` non determina `Tipo prompt`.
- Filename semantici stabili; `PROMPT_ID` non ordina i task.

### Scelta modello/reasoning

I valori `model=` e `reasoning=` sono indicazioni operative per il selettore Codex Desktop e vanno impostati manualmente prima dell'esecuzione.

- `low`: task lineari/meccanici o verifiche deterministiche già preparate.
- `medium`: default quando servono decisioni, diagnosi di failure, più invarianti o modifiche cross-component.
- `high`: solo quando rischio/difficoltà lo giustificano concretamente.

Usa GPT-5.5 per task delimitati; passa a GPT-5.6 Sol quando il task è cross-module/architetturale, coinvolge schema/migrazioni/undo-audit/rischio dati o richiede ragionamento più robusto.

## Esecuzione manuale: fast path

Per eseguire il primo pendente:

1. individua **fuori da Codex** il primo link in `roadmap.md`;
2. apri il relativo `prompts/<task>.md`;
3. imposta progetto, modello e reasoning dai metadata;
4. incolla in Codex **l'intero contenuto di quel file e nient'altro**.

Non inviare prima un prompt tipo “esegui il primo task”, non chiedere a Codex di leggere la roadmap e non fargli eseguire `roadmap_guard.py select`.

Il vantaggio è che Codex parte direttamente dal task reale: niente tool-call di selezione, niente execution pack aggiunto al contesto e niente reasoning per trasformare un meta-prompt nel lavoro effettivo.

Durante l'esecuzione valgono le restrizioni scritte nel singolo prompt: starting point già verificato, letture consentite, test mirati, nessun audit/refactor fuori scope e stop immediato a PASS/BLOCKED/FAIL.

Default: **un solo task per sessione**. Fasi multiple solo se il prompt dichiara esplicitamente una campagna compatibile.

### PASS

Ogni prompt contiene direttamente il proprio comando di finalizzazione, nella forma:

```bash
python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id PROMPT_ID --dry-run && \
python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id PROMPT_ID
```

La risposta reale `status=completed`, `commit=<SHA>`, `push_verified=git_push_exit_0` è prova canonica del push della roadmap. Non eseguire dopo `git status`, `git rev-parse`, `git ls-remote`, pull/fetch o verifiche equivalenti sulla roadmap. Non aprire il task successivo.

### BLOCKED / FAIL

Non archiviare, non rinumerare e non avanzare. Riportare solo blocker/evidenza utile e fermarsi.

## Selezione unattended/automatica

`python3 tools/roadmap_guard.py select` resta disponibile **solo quando non c'è un operatore che sceglie il file prompt**. In quel caso il guard fa fetch di `origin/main` e restituisce identità, metadata, execution contract e `prompt_content`.

Il launcher unattended compatto è documentato in `STANDARD_PROMPT.md`. Non usarlo nelle normali sessioni manuali.

## Sicurezza del guard

Il worktree locale può essere sporco: non usare stash/reset/checkout per selezionare o completare task.

`select` legge `origin/main` e non modifica il worktree.

`complete`:

- accetta solo il `PROMPT_ID` del primo pendente corrente;
- usa un worktree detached temporaneo da `origin/main`;
- sposta solo quel prompt in `completed/` e aggiorna roadmap/spiegazioni;
- consente nello staged diff solo i path task-owned attesi;
- commit + push fast-forward `HEAD:main`, mai force;
- considera il push verificato solo con exit code 0 e `push_verified=git_push_exit_0`;
- su push bloccato preserva il worktree isolato e restituisce il path.

Prima di modificare guard/workflow eseguire:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

## Campagne continue

Una campagna esiste solo con stesso `campaign_id` e metadata compatibili. Ogni fase resta autosufficiente e ordinata; PASS intermedio è checkpoint; BLOCKED/FAIL ferma tutto. Build/install/QA comuni vanno consolidati nella fase finale quando sicuro. Per PersonalHub usare una sola versione per campagna (`base + 1`).

## Manutenzione

Quando si modifica la roadmap:

- mantenere `roadmap.md`, `spiegazioni.md`, prompt e wikilink coerenti;
- `Spiegazioni` resta semplice e non duplica acceptance/dettagli tecnici;
- sincronizzare `reasoning=` e colonna `Livello ragionamento`;
- rivalutare modello/reasoning quando cambiano requisiti o rischio;
- consolidare task solo se riduce realmente bootstrap/build/QA/tool-call senza creare mega-task indipendenti;
- ogni nuovo prompt deve essere direttamente incollabile in Codex e includere la propria finalizzazione su PASS;
- non reintrodurre un wrapper obbligatorio per l'esecuzione manuale;
- mantenere `select` come fallback per automazione/unattended;
- non modificare/assorbire task attivamente in esecuzione;
- non cancellare stash/branch storici senza provarne la ridondanza.
