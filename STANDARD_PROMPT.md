# Esecuzione Codex della roadmap

## Default manuale — nessun prompt intermedio

Per una normale sessione Codex Desktop **non incollare un launcher generico** e non chiedere a Codex di selezionare il task.

1. Individua fuori da Codex il primo elemento di `roadmap.md`.
2. Apri il relativo `prompts/<task>.md`.
3. Imposta nel selettore Codex Desktop progetto, `model=` e `reasoning=` indicati nei metadata del file.
4. Incolla **l'intero contenuto del file prompt come unico prompt iniziale**.

Il file `prompts/<task>.md` è la specifica autoritativa e deve essere autosufficiente: starting point già verificato, scope, test, PASS/stop, output e finalizzazione della roadmap devono stare nel file stesso. Codex non deve eseguire `roadmap_guard.py select`, né rileggere README/roadmap/spiegazioni per capire cosa fare.

Questo è il percorso preferito perché evita il round-trip `launcher → select → execution pack → prompt_content` e usa la quota Codex direttamente sul task reale.

La roadmap contiene soltanto attività che richiedono realmente Codex (filesystem/toolchain locale, device, VM, segreti/config runtime o servizi locali). Modifiche eseguibili direttamente sui repository remoti non vanno rimandate a Codex.

## Efficienza di esecuzione

Per task già pre-localizzati il costo principale è spesso il numero di round-trip modello↔tool, non il reasoning. I prompt devono quindi imporre queste regole quando applicabili:

- se lo starting point è dichiarato autoritativo, non leggere `~/.codex/memories/MEMORY.md`, README, roadmap, spiegazioni, MegaVault o altra memoria/documentazione aggiuntiva salvo un dato realmente mancante che blocchi l'esecuzione;
- raggruppare in una sola tool-call i controlli read-only indipendenti compatibili (stato Git, simboli/file già noti, stato runtime), invece di fare una chiamata per ciascun controllo;
- riusare output già ottenuti: niente rilettura di file invariati, retry identici o verifiche equivalenti dopo un PASS;
- usare direttamente il runner/test command indicato dal prompt; non sondare framework alternativi se il runner canonico è già noto;
- niente messaggi intermedi di avanzamento: tool-call dirette, testo intermedio solo per un blocker/decisione dell'utente, poi report finale conciso;
- per un task localizzato e pre-localizzato, **obiettivo indicativo ≤10 tool-call**; superarlo solo quando una failure o nuova evidenza rende davvero necessaria ulteriore indagine. Non sacrificare correttezza o safety per rispettare il numero.

## Campagne

Se più prompt condividono `campaign_id`, ogni fase resta autosufficiente ma deve rispettare il contratto della campagna. Per PersonalHub le fasi intermedie non fanno bump versione, final APK, installazione del package reale Pixel o Telegram delivery; queste operazioni comuni si eseguono una sola volta nella fase finale. Non eseguire task PersonalHub concorrenti della stessa o di altre campagne.

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
- consolidare build/device/delivery nella fase finale quando appartiene a una campagna compatibile;
- contenere la finalizzazione roadmap su PASS con il proprio `PROMPT_ID`;
- non dipendere dal launcher generico o dall'output di `select` per informazioni necessarie all'esecuzione.

Quando workflow o guard cambiano, aggiornare questo file solo se il cambiamento modifica davvero uno dei due percorsi: esecuzione diretta manuale o fallback unattended.
