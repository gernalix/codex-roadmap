# Esecuzione Codex della roadmap

## Default manuale — nessun prompt intermedio

Per una normale sessione Codex Desktop **non incollare un launcher generico** e non chiedere a Codex di selezionare il task.

1. Individua fuori da Codex il primo elemento di `roadmap.md`.
2. Apri il relativo `prompts/<task>.md`.
3. Imposta nel selettore Codex Desktop progetto, `model=` e `reasoning=` indicati nei metadata del file.
4. Incolla **l'intero contenuto del file prompt come unico prompt iniziale**.

Il file `prompts/<task>.md` è la specifica autoritativa e deve essere autosufficiente: starting point già verificato, scope, test, PASS/stop, output e finalizzazione della roadmap devono stare nel file stesso. Codex non deve eseguire `roadmap_guard.py select`, né rileggere README/roadmap/spiegazioni per capire cosa fare.

Questo è il percorso preferito perché evita il round-trip `launcher → select → execution pack → prompt_content` e usa la quota Codex direttamente sul task reale.

## `roadmap_guard.py`

Il guard resta utile per due scopi:

- **selezione unattended/automatica**: `python3 tools/roadmap_guard.py select` può ancora restituire l'execution pack quando non c'è un operatore che sceglie il file;
- **finalizzazione su PASS**: ogni prompt pendente deve contenere direttamente il proprio comando `complete --prompt-id ...`, con dry-run seguito da complete.

Una risposta `complete` con `status=completed`, `commit=<SHA>` e `push_verified=git_push_exit_0` è prova canonica del push della roadmap. Non fare controlli Git equivalenti dopo il PASS e non aprire il task successivo nella stessa sessione.

Su BLOCKED/FAIL non archiviare, non rinumerare e non avanzare la roadmap.

## Fallback unattended

Solo quando la selezione deve essere fatta automaticamente da Codex si può usare questo launcher compatto:

```text
Esegui SOLO il primo task pendente di gernalix/codex-roadmap. Come prima tool-call esegui `python3 tools/roadmap_guard.py select`, usa `prompt_content` come task completo e non rileggere README/roadmap/spiegazioni salvo incoerenza concreta. Considera già verificato ciò che il task dichiara verificato, mantieni scope e test mirati e fermati a PASS/BLOCKED/FAIL. Su PASS usa il `complete` previsto dal task; non aprire il task successivo.
```

Questo fallback non è il workflow manuale normale.

## Contratto di manutenzione

Ogni nuovo prompt o modifica sostanziale di un prompt pendente deve preservare l'esecuzione diretta. In particolare il file deve:

- dichiarare `PROMPT_ID`, `project_id`, modello, reasoning e MegaVault quando applicabili;
- contenere direttamente goal, starting point/source-of-truth, scope/non-goal, verification e PASS/stop;
- vietare discovery/audit già sostituiti da evidenza preparata;
- richiedere solo test proporzionati al rischio;
- contenere la finalizzazione roadmap su PASS con il proprio `PROMPT_ID`;
- non dipendere dal launcher generico o dall'output di `select` per informazioni necessarie all'esecuzione.

Quando workflow o guard cambiano, aggiornare questo file solo se il cambiamento modifica davvero uno dei due percorsi: esecuzione diretta manuale o fallback unattended.
