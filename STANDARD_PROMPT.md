# Esecuzione Codex della roadmap

> `roadmap.sqlite` è la source of truth. `roadmap.md` e `spiegazioni.md` sono viste generate: non modificarle manualmente per avanzare la coda.

## Default manuale — nessun prompt intermedio

Per una normale sessione Codex Desktop **non incollare un launcher generico** e non chiedere a Codex di selezionare il task.

1. Individua fuori da Codex il primo elemento di `roadmap.md`.
2. Apri il relativo `prompts/<task>.md`.
3. Imposta nel selettore Codex Desktop progetto, `model=` e `reasoning=` indicati nei metadata del file.
4. Incolla **l'intero contenuto del file prompt come unico prompt iniziale**.

Il file `prompts/<task>.md` è la specifica autoritativa e deve essere autosufficiente: starting point già verificato, scope, test, PASS/stop, output e finalizzazione della roadmap devono stare nel file stesso. Codex non deve eseguire `roadmap_guard.py select`, né rileggere README/roadmap/spiegazioni per capire cosa fare.

Per i task localizzati questa autorità va ribadita **dentro il singolo prompt**, non lasciata soltanto in questo documento: il prompt deve dire esplicitamente di non leggere README/roadmap/spiegazioni, `~/.codex/memories/MEMORY.md`, MegaVault o documentazione di contesto già sostituita dallo starting point, salvo un blocker concreto. In questo modo il workflow manuale non deve spendere tool-call per leggere `STANDARD_PROMPT.md` o altra metadocumentazione prima di iniziare.

Questo è il percorso preferito perché evita il round-trip `launcher → select → execution pack → prompt_content` e usa la quota Codex direttamente sul task reale.

La roadmap contiene soltanto attività che richiedono realmente Codex (filesystem/toolchain locale, device, VM, segreti/config runtime o servizi locali). Modifiche eseguibili direttamente sui repository remoti non vanno rimandate a Codex.

## Recovery autonomo obbligatorio

Il prompt deve trattare **goal + acceptance criteria** come contratto terminale e i passi operativi come percorso adattabile. Al primo failure non deve fermarsi automaticamente: deve usare l'errore come evidenza, diagnosticare la causa minima, applicare il fix minimo in-scope, rilanciare il leaf gate e riprendere il goal originale.

Regole terminali:
- `BLOCKED` solo per dipendenza esterna/umana indispensabile, device/servizio richiesto indisponibile senza alternativa valida, lock/concorrenza unsafe o azione distruttiva/ambigua che richiede consenso;
- `FAIL` solo dopo recovery in-scope ragionevole esaurito o quando l'unico fix residuo sarebbe unsafe/materialmente fuori scope;
- remote advance, dirty non sovrapposto, compile/test failure, mismatch di configurazione o tool failure non sono di per sé terminali;
- niente retry identici senza nuova evidenza/stato cambiato; niente audit/refactor/cleanup collaterali; ogni espansione deve essere direttamente causata dal failure concreto;
- un budget tool-call può essere superato solo per failure o dipendenze nuove realmente osservate, senza sacrificare acceptance o safety;
- dopo ogni recovery riuscito, tornare automaticamente alla sequenza di acceptance originaria; dopo PASS, stop immediato.

Un prompt safety/validation-only può vietare la mutazione e quindi fermarsi su uno specifico gate soltanto quando quella mutazione è esplicitamente fuori scope per ragioni di sicurezza o richiede azione umana esterna.

## Efficienza di esecuzione

Per task già pre-localizzati il costo principale è spesso il numero di round-trip modello↔tool, non il reasoning. I prompt devono quindi imporre queste regole quando applicabili:

- se lo starting point è dichiarato autoritativo, non leggere `~/.codex/memories/MEMORY.md`, README, roadmap, spiegazioni, MegaVault o altra memoria/documentazione aggiuntiva salvo un dato realmente mancante che blocchi l'esecuzione;
- per il workflow manuale diretto, non trasformare automaticamente il prompt in un Goal persistente. Usa Goal solo quando la persistenza multi-turn è realmente parte del task; se un Goal è già attivo non tentare mai di crearne un altro o di completarne uno wrapper solo per ricrearlo;
- dichiarare il **checkout/workdir canonico esatto** quando il task è legato a un repo e usarlo dalla prima tool-call; non partire da una directory ChatGPT/progetto incidentale e poi cercare il repository tramite memoria/documentazione;
- se il prompt indica chiavi precise di `.codex/CODE_MAP.tsv`, leggere **solo quelle righe** (per esempio con un `rg` ancorato sulle chiavi), non fare dump del CODE_MAP né inventory del modulo;
- se il task richiede un lease/lock già standardizzato, il prompt deve contenere direttamente i comandi esatti di acquire/release con il proprio `PROMPT_ID`; non obbligare Codex a cercarli in `AGENTS.md`, `/tmp` o nel repository. Per PersonalHub: `python3 tools/personalhub_task_lock.py acquire --prompt-id <PROMPT_ID>` e `python3 tools/personalhub_task_lock.py release --prompt-id <PROMPT_ID>`;
- per task che scrivono su un branch condiviso, sincronizzare **prima** delle modifiche con fetch + fast-forward only e registrare lo SHA remoto iniziale; subito prima del commit/push fare un solo fetch finale. Se il remoto è avanzato durante il task, trattarlo come condizione intermedia: ispezionare soltanto il diff concorrente rilevante, integrare automaticamente quando è chiaramente non sovrapposto/compatibile secondo la policy del repo e rieseguire solo i gate invalidati. Usare BLOCKED solo se overlap, ownership concorrente o ambiguità rendono unsafe scegliere autonomamente;
- se il prompt richiede commit/push soltanto dopo i gate finali, **non creare commit intermedi**. In checkout soggetti ad autosync un commit locale può essere pubblicato da un altro servizio e trasformare una normale sincronizzazione finale in divergenza/rebase/conflitti; mantenere il diff non committato fino al PASS tecnico e fare un solo commit/push finale;
- quando DB, log o servizi richiedono privilegi e il prompt indica già l'helper privilegiato canonico, usarlo dalla prima lettura. Non spendere un probe non privilegiato destinato a fallire; se lo schema SQL non è noto, fare una sola introspezione (`PRAGMA table_info` o equivalente) prima della query invece di indovinare nomi di colonne;
- quando l'acceptance richiede N cicli schedulati reali, avviare **un solo watcher/verifier bounded** che osserva il timer/processo e termina appena N cicli validi sono provati. Evitare sequenze `sleep → readback → sleep → readback` e query remote ripetute equivalenti;
- su filesystem grandi/lenti (specialmente multi-TB, FUSE/NTFS o dischi quasi pieni), non lanciare una scansione monolitica senza output progressivo. Preferire top-level bounded scan, timeout esplicito e approfondimento solo dei pochi directory consumer emersi; interrompere subito un approccio che non produce evidenza utile;
- raggruppare in una sola tool-call i controlli read-only indipendenti compatibili (stato Git, simboli/file già noti, stato runtime), invece di fare una chiamata per ciascun controllo;
- riusare output già ottenuti: niente rilettura di file invariati, retry identici o verifiche equivalenti dopo un PASS;
- per log e journal partire dalla sorgente/produttore già identificato e da una finestra temporale stretta; evitare `journalctl -b`/dump globali senza `--since`/`--until`/`-n` salvo che l'evidenza mirata sia insufficiente. Un output già troncato o di migliaia di token è un segnale per restringere la query, non per ripeterla più ampia;
- per build/compile usate soltanto come gate di exit-code, preferire output quiet/bounded (per Gradle normalmente `--quiet --console=plain`) e riaprire output dettagliato solo in caso di failure; non spendere migliaia di token per liste `UP-TO-DATE` su un PASS;
- dopo un test Gradle FAIL, leggere prima il JUnit XML mirato sotto `build/test-results/...` quando disponibile; non indovinare path HTML e non fare `rg --files` del report tree salvo che il risultato XML manchi realmente;
- dopo un test FAIL, leggere il **minimo failure artifact** necessario e rerunnare solo il test/leaf fallito dopo una correzione basata su nuova evidenza; non rilanciare identico l'intero set dopo ogni ipotesi. Il set completo mirato si riconferma una sola volta alla fine;
- se il task tocca Android resources/stringhe o altri input che possono fallire solo in compile/package, eseguire il più economico compile/resource gate **dopo l'ultima modifica host e prima di dichiarare i gate host chiusi o avviare il device**; una correzione statica tardiva non deve costringere a ripetere l'intera validazione;
- quando un helper canonico risolve già device, APK, processor o altri artifact, usarne direttamente i resolver/default invece di fare `--help`, `rg --files`, `find`, `adb devices` o probing equivalente. Per artifact generati/gitignored non usare `rg --files` come prima sorgente;
- prima di creare watcher/script/service diagnostici persistenti, fare **un solo controllo mirato** per verificare se il progetto/runtime canonico possiede già un collector/watcher equivalente; riusarlo o estenderlo localmente invece di creare un duplicato. Validare privilegi e cattura dell'evento reale prima di abilitarlo stabilmente;
- per watcher basati su snapshot/change detection, confrontare solo lo stato semantico stabile: timestamp/`observed_at` non devono rendere ogni campione artificialmente “diverso”;
- costruire patch coerenti per file: evitare un'unica patch che contiene più operazioni incompatibili sullo stesso path e, dopo una patch applicata con successo, non riscrivere lo stesso file a piccoli passi salvo failure/evidenza concreta;
- usare direttamente il runner/test command indicato dal prompt; non sondare framework alternativi se il runner canonico è già noto;
- non leggere test di riferimento o inventariare `tests/` quando il prompt indica già il file/test target; fallo solo se serve per una failure concreta o per una convenzione non specificata;
- prima del PASS costruire internamente una matrice requirement→evidence per **ogni** acceptance criterion esplicito. Un test verde generico non prova requisiti UI/dati non asseriti: filtri, campi di dettaglio, copy/report e invarianti di persistenza devono avere evidenza diretta nel codice/test/runtime pertinente;
- niente comandi no-op o preparatori privi di effetto (`mkdir /tmp/noop`, probe equivalenti, placeholder shell): ogni tool-call deve cambiare stato utile o produrre evidenza necessaria;
- niente messaggi intermedi di avanzamento: tool-call dirette, testo intermedio solo per un blocker/decisione dell'utente, poi report finale conciso;
- per un task localizzato e pre-localizzato, **obiettivo indicativo ≤10 tool-call**; per task realmente cross-component/DB+device il prompt può fissare un budget più alto coerente con MegaVault, ma superarlo richiede failure o nuova evidenza concreta. Non sacrificare correttezza o safety per rispettare il numero.

## Campagne

Se più prompt condividono `campaign_id`, ogni fase resta autosufficiente ma deve rispettare il contratto della campagna. Per PersonalHub le fasi intermedie non fanno bump versione, final APK, installazione del package reale Pixel o Telegram delivery; queste operazioni comuni si eseguono una sola volta nella fase finale. Implementazioni PH indipendenti possono procedere in parallelo solo su branch dedicati; integrazione in `main`, QA condivisa e release restano serializzate sotto il lock PH e richiedono review semantica prima del merge.

## Finalizzazione roadmap

PASS:

```bash
python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id <PROMPT_ID> --confirm-executed
```

BLOCKED/FAIL:

```bash
python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id <PROMPT_ID> --result BLOCKED --confirm-executed
# oppure --result FAIL
```

Entrambi inviano una mutazione idempotente alla inbox remota; il workflow GitHub Actions single-writer aggiorna `roadmap.sqlite`, archivia il file e rigenera Markdown/Obsidian. Il checkout locale della roadmap non viene modificato. Non fare prima un dry-run nel percorso normale.

Un esito terminale non rende riutilizzabile il PROMPT_ID: un fix o follow-up è sempre una nuova materializzazione con nuovo ID e relazione al padre. Timestamp, durata, token e tool-call reali vengono riconciliati automaticamente dal sync di `codex-usage`.

La prima riga finale resta `RESULT=PASS|BLOCKED|FAIL`. Se codice/test sono PASS ma una finalizzazione obbligatoria fallisce, il risultato complessivo è BLOCKED/FAIL e va registrato coerentemente quando possibile.

## Fallback unattended

Solo quando la selezione deve essere fatta automaticamente da Codex si può usare questo launcher compatto:

```text
Esegui SOLO il primo task pendente di gernalix/codex-roadmap. Come prima tool-call esegui `python3 tools/roadmap_guard.py select`, usa `prompt_content` come task completo e non rileggere README/roadmap/spiegazioni salvo incoerenza concreta. Considera già verificato ciò che il task dichiara verificato, mantieni scope e test mirati, recupera autonomamente i failure intermedi con fix minimi e fermati solo a PASS o a un vero BLOCKED/FAIL terminale. Su PASS usa una sola volta `python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id <PROMPT_ID> --confirm-executed`; non aprire il task successivo.
```

Questo fallback non è il workflow manuale normale.

## Contratto di manutenzione

Ogni nuovo prompt o modifica sostanziale di un prompt pendente deve preservare l'esecuzione diretta. In particolare il file deve:

- dichiarare `PROMPT_ID`, `project_id`, modello, reasoning e MegaVault quando applicabili;
- se riprende un run fallito/bloccato, dichiarare anche `last_result=BLOCKED` o `last_result=FAIL`;
- contenere direttamente goal, starting point/source-of-truth, checkout/workdir canonico, scope/non-goal, verification e PASS/stop;
- dichiarare esplicitamente, quando lo starting point è completo, che README/roadmap/spiegazioni/MEMORY/MegaVault non vanno riletti salvo blocker concreto;
- includere direttamente comandi operativi standard necessari al task (lease/lock, runner canonico, helper già noto) invece di rimandare a discovery documentale;
- vietare discovery/audit già sostituiti da evidenza preparata e, quando il target test è già noto, evitare inventory/letture di test di riferimento non necessarie;
- richiedere solo test proporzionati al rischio;
- per branch condivisi, specificare la policy di sync iniziale e di remote-advance prima del push;
- consolidare build/device/delivery nella fase finale quando appartiene a una campagna compatibile;
- contenere direttamente sia la singola invocazione PASS con `roadmap_finish.py` sia le invocazioni terminali `roadmap_result.py --result BLOCKED|FAIL` con il proprio `PROMPT_ID` e `--confirm-executed`, così Codex non deve ispezionare la CLI per ricostruire la sintassi;
- includere esplicitamente il contratto di recovery autonomo o una forma compatta equivalente, così il prompt resta autosufficiente anche senza rileggere README/STANDARD_PROMPT;
- richiedere `RESULT=PASS|BLOCKED|FAIL` come prima riga finale;
- non dipendere dal launcher generico o dall'output di `select` per informazioni necessarie all'esecuzione.

Quando workflow o guard cambiano, aggiornare questo file solo se il cambiamento modifica davvero uno dei due percorsi: esecuzione diretta manuale o fallback unattended.
