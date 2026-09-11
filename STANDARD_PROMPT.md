# Prompt standard Codex Desktop

Questo è il **prompt canonico da copiare in Codex Desktop** per eseguire il primo task pendente della roadmap.

Prima di inviarlo, l'operatore deve impostare **manualmente** nel selettore di Codex Desktop il progetto, il modello e il reasoning appropriati per il task. I metadata della roadmap sono indicazioni operative: non modificano automaticamente il selettore.

```text
Esegui SOLO il primo task pendente della roadmap remota `gernalix/codex-roadmap`.

Come PRIMA azione di tool nel checkout locale della roadmap esegui `python3 tools/roadmap_guard.py select`. Prima di `select` NON consultare MEMORY/storia e NON eseguire `pwd`, `ls`, `git status`, `git pull`, `git fetch` o altri preflight della roadmap: `select` fa già il fetch canonico di `origin/main` e restituisce tutto ciò che serve.

Usa l'execution pack restituito come unica sorgente roadmap per il task. Non rileggere `README.md`, `roadmap.md`, `spiegazioni.md` o il file prompt separatamente, salvo incoerenza o blocker concreto.

Segui integralmente `prompt_content` come specifica autoritativa. Considera già verificati starting point, file, simboli, inventory, decisioni e conclusioni esplicitamente riportati nel task: non rifare discovery generale o audit già preparati.

Regole:
- scope strettissimo: fai solo quanto richiesto dal task;
- parti direttamente dai file/simboli/entrypoint già indicati;
- amplia l'indagine solo per una failure concreta, una lacuna reale o un collaborator diretto indispensabile;
- nessun refactor, cleanup, modernizzazione, ottimizzazione o fix fuori scope;
- problemi collaterali: segnalali soltanto, salvo che blocchino esplicitamente il task;
- riusa evidenza e risultati già ottenuti nella sessione finché lo stato non cambia;
- niente retry equivalenti, test duplicati o verifiche ripetute senza nuova evidenza;
- raggruppa check/comandi indipendenti nella stessa tool-call quando è sicuro e non riduce la chiarezza del failure point;
- non separare in più tool-call status/pull/test o verifiche analoghe quando una singola shell condizionale può preservare esattamente le stesse garanzie;
- limita l'output dei tool all'evidenza necessaria: niente dump ampi, log completi o `max_output` sovradimensionati se non richiesti dal task/failure;
- quando esegui suite Python `unittest` e stdout/stderr dei test non sono essi stessi acceptance evidence, usa `-b/--buffer`: su PASS scarta il rumore, su failure conserva l'output diagnostico;
- esegui prima i test mirati richiesti; amplia solo se una failure o il rischio concreto lo richiede;
- non usare force/reset/stash distruttivi e non perdere modifiche locali;
- non aggirare un blocker esplicito per ottenere artificialmente PASS: se il task dice che una condizione implica BLOCKED, rispettala;
- non modificare package installati, file root-owned, `site-packages`, configurazioni di sistema o altre copie fuori dal source-of-truth versionato come sostituto di un fix nel repository, salvo autorizzazione esplicita del task;
- considera PASS solo quando TUTTI gli acceptance criteria sono soddisfatti esattamente; un workaround non autorizzato non trasforma un blocker in PASS;
- durante l'esecuzione non inviare progress report narrativi: usa direttamente i tool; scrivi testo intermedio solo se emerge un blocker che richiede una mia decisione;
- se il task dichiara una campagna continua, esegui solo le fasi consecutive consentite dal relativo execution contract; altrimenti un solo task per sessione.

Su PASS:
- commit/push normali solo dei repo realmente modificati, secondo il protocollo del task; mai force;
- finalizza con `python3 tools/roadmap_guard.py complete --prompt-id PROMPT_ID --dry-run` e, solo se ha successo, `python3 tools/roadmap_guard.py complete --prompt-id PROMPT_ID`; quando possibile esegui i due comandi nella stessa tool-call usando `&&`;
- una risposta reale di `complete` con `status=completed`, `commit=<SHA>` e `push_verified=git_push_exit_0` è già la verifica canonica del push della roadmap: NON eseguire dopo `git status`, `git rev-parse`, `git ls-remote`, pull/fetch o altri controlli equivalenti sulla roadmap;
- il checkout locale della roadmap può restare intenzionalmente indietro perché `complete` usa un worktree isolato: non sincronizzarlo solo per il report finale;
- produci un unico report finale conciso nel formato richiesto dal task e STOP immediato;
- non aprire né analizzare il task successivo.

Su BLOCKED o FAIL:
- non archiviare, non rinumerare e non avanzare la roadmap;
- riporta solo blocker/evidenza utile nel report finale e STOP.
```

## Regola di manutenzione

Questo file è **canonico e vivo**, non un testo da congelare. Va riesaminato e aggiornato ogni volta che serve, in particolare quando:

- cambia il workflow di `roadmap_guard`, il fast path, la finalizzazione o il reporting;
- cambiano le regole per modello/reasoning o per il progetto Codex Desktop da usare;
- un run reale mostra instruction-loss, workaround non autorizzati, tool-call/retry inutili, discovery ripetuta o altri colli di bottiglia ricorrenti;
- una nuova regola globale può ridurre token, latenza o rischio senza rendere il prompt inutilmente più lungo;
- cambia una condizione di sicurezza, source-of-truth, Git o stop/PASS/BLOCKED.

Quando una modifica del workflow rende questo prompt obsoleto, aggiornare `STANDARD_PROMPT.md` **nello stesso intervento**. Quando un'analisi post-run individua una lezione generale e riutilizzabile, incorporarla qui se migliora concretamente le esecuzioni future.

Il `Launcher minimo` nel README è solo una scorciatoia; in caso di divergenza prevale questo file.