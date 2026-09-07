# Fedora Codex completion guard — final hardening

PROMPT_ID: 947261

**Modello consigliato:** GPT-5.5  
**Reasoning:** low  
**MegaVault:** FAST

## Goal

Chiudere in modo strettamente localizzato i difetti residui del completion guard introdotto in `gernalix/codex-usage-monitor`, senza riaprire l'autosync ghorg/MegaVault già funzionante.

Il risultato deve garantire che:

1. il CWD generale sia usato **solo** quando nessun repo esplicito è stato ricavato dai tool call;
2. ogni rollout venga letto/parso una sola volta per run del publisher, senza il secondo `path.read_text().splitlines()` aggiunto dal wrapper;
3. un fetch/confronto Git fallito non possa mai essere classificato come `clean_synced`;
4. il fix non provochi un altro backfill/ripublish massivo di cicli storici per sole variazioni di metadati derivati del guard.

## Scope stretto / starting points

Parti soltanto dai file remoti correnti seguenti e dai test direttamente pertinenti:

- `gernalix/codex-usage-monitor/codex_usage_publisher.py`
  - `_repo_root`
  - `classify_git_repo`
  - `_repo_roots`
  - `_explicit_paths_from_payload`
  - `parse_session`
  - `_fingerprint`
  - `record_git_completion_guard`
  - `command_run`
- `gernalix/codex-usage-monitor/codex_usage_publisher_legacy.py`
  - **solo** `parse_session` e le strutture `current/metrics` necessarie per evitare la seconda lettura del rollout
- `gernalix/codex-usage-monitor/tests/test_usage_publisher.py`

Non modificare `github_autosync.py`, MegaVault, systemd, ghorg, codex-roadmap oltre alle normali operazioni terminali della roadmap. Non fare audit generale del repo. Non leggere `~/.codex/memories/MEMORY.md`.

## Evidenza già verificata da riusare

- Commit corrente da correggere: `9069ee73f574204d76678d44aac8f3a8de46553b` (`Harden autosync completion guard`).
- `RESULT=PASS|BLOCKED|FAIL` ora viene esportato correttamente; il vecchio prompt `628431` risulta già `status=PASS`. **Non toccare questo parser salvo dipendenza strettamente necessaria.**
- Il fail-safe ghorg/MegaVault ora è corretto. **Non riaprirlo.**
- `repo_projects` ora raccoglie i repo espliciti dei tool call, ma `parse_session()` aggiunge comunque sempre `metrics.repo_project` ai candidati. Nella sessione reale `781264`, oltre ai repo realmente toccati, è comparso anche `/home/daniele/Documents/ChatGPT/Fedora`. Il requisito corretto è: CWD/session repo solo se non è stato trovato alcun repo esplicito dai tool call.
- Il test esistente con 3 repo non vede questo bug perché usa un CWD fuori da qualunque repo Git.
- Il publisher legacy continua a fare un singolo `source_root.glob("**/*.jsonl")` ogni run e `codex_usage_publisher_legacy.parse_session()` legge già ogni rollout interamente con `path.read_text()` e lo percorre riga per riga.
- Il wrapper corrente chiama prima `_legacy_parse_session(path, con)` e poi rilegge lo stesso file con `path.read_text(...).splitlines()` per estrarre i path dei tool call. Quindi ogni rollout viene letto/parso due volte.
- Il secondo glob globale aggiunto dal task 628431 è già stato eliminato: **non serve un altro watcher né un altro indice di file**. Va eliminata soltanto la seconda lettura/parsing dentro il wrapper.
- `classify_git_repo()` oggi, se `git fetch` fallisce, imposta `fetched=0` ma continua. Se `rev-list` non produce conteggi validi, `ahead/behind` restano `None` e il codice può cadere su `clean_synced`: falso positivo vietato.
- La precedente modifica dei metrics ha causato un commit `usage: publish 498 prompt cycles`. Non ripetere questo churn per un cambiamento che riguarda soltanto metadata derivati/locali del guard.

## Fix A — fallback CWD corretto

In `parse_session`:

- raccogli i repo espliciti realmente usati dai tool call della completion;
- se almeno un repo esplicito è stato risolto, `repo_projects` deve contenere **solo** quei repo deduplicati;
- usa `repo_project`/CWD di sessione o turno soltanto quando non è stato risolto alcun repo esplicito;
- non dedurre repo dal testo del comando, dal prompt o da scansioni filesystem.

Test obbligatorio nuovo/aggiornato:

- crea 4 repo Git temporanei A/B/C/D;
- imposta il CWD della sessione dentro A;
- tool call espliciti operano solo in B/C/D;
- verifica che `repo_projects` e le righe `git_completion_guard_repos` contengano esattamente B/C/D, mai A;
- seconda esecuzione idempotente: nessun nuovo guard/fetch.

## Fix B — parsing rollout singolo

Non accettare una soluzione che sostituisca una rescansione con un'altra.

Porta la raccolta dei path dei tool call nel **medesimo passaggio sulle righe JSONL già eseguito da `codex_usage_publisher_legacy.parse_session()`**, con la modifica minima necessaria:

- mentre il legacy parser sta già iterando le righe, raccogli per turno i path espliciti (`workdir`, `cwd`, `path`, `file`, target path quando realmente strutturato) dalle arguments/input dei `function_call`/`custom_tool_call`;
- trasferisci l'informazione nei metrics/cycle restituiti, oppure usa un'altra struttura restituita/compatibile minima;
- nel wrapper `codex_usage_publisher.parse_session()` **rimuovi completamente** il secondo `path.read_text(...).splitlines()` e riusa i dati già prodotti dal primo passaggio;
- non aggiungere un secondo glob, watcher, cache complessa o nuovo DB.

Aggiungi un test che renda il requisito osservabile, per esempio mockando/contando la lettura del file o isolando il parser: una singola `parse_session(path, con)` deve richiedere una sola lettura completa del rollout, non due.

Nota: il `source_root.glob("**/*.jsonl")` già presente nel publisher legacy è fuori scope in questo task; l'obiettivo è **una sola lettura/parsing per file per run**, non ridisegnare l'intero publisher.

## Fix C — mai falso `clean_synced`

Rendi `classify_git_repo()` conservativo:

- `clean_synced` è consentito solo dopo prove Git valide;
- se esiste upstream e il fetch richiesto fallisce, restituisci `status="unknown"` (o equivalente già previsto) con `detail="fetch_failed"` e `fetched=0`; non usare conteggi stale come prova di sync;
- se `rev-list --left-right --count HEAD...upstream` fallisce o non restituisce esattamente due interi validi, restituisci `unknown` con detail esplicativo;
- se il comando per determinare branch/upstream fallisce in modo ambiguo, non trasformarlo automaticamente in `clean_synced`;
- `no_upstream` resta valido quando Git conferma realmente l'assenza di upstream;
- il guard resta completamente passivo.

Test obbligatori con repo temporanei/mock mirati:

- fetch failure -> `unknown`, mai `clean_synced`;
- rev-list failure/malformed output -> `unknown`;
- clean reale e fetch+rev-list validi -> `clean_synced`;
- preserva i test `dirty`, `ahead`, `behind/diverged`, `no_upstream` già pertinenti.

## Fix D — niente nuovo backfill massivo

Il completion guard è metadata operativo locale; modificare il modo in cui vengono derivati `repo_projects`/dettagli del guard non deve rendere centinaia di vecchi cicli improvvisamente "changed" e ripubblicarli.

Applica il minimo fix coerente col publisher corrente:

- separa nel fingerprint ciò che rappresenta il contenuto/versione pubblicabile del ciclo dai soli metadata derivati del guard, oppure altra soluzione equivalente minima;
- **status terminale deve continuare a poter correggere/exportare un ciclo quando cambia realmente** (come è successo per 628431);
- `prompt_id`, final response/eventi e altre semantiche pubblicate esistenti non devono perdere la capacità di triggerare un update quando appropriato;
- `repo_projects` e metadata esclusivamente del guard non devono, da soli, causare ripublish storico;
- non riscrivere manualmente l'archivio `codex-usage` e non fare backfill retroattivi in questo task.

Test obbligatorio:

- un ciclo già pubblicato, ricalcolato con identico contenuto/status ma diversa sola derivazione `repo_projects`/guard metadata, deve restare no-op;
- una variazione reale `UNKNOWN -> PASS` deve invece restare publishable.

## Token/tool-call discipline specifica

Questo è un fix già completamente pre-localizzato:

- **non leggere MEMORY.md**;
- non rileggere README generici di `codex-usage-monitor` o documentazione ghorg;
- non interrogare MegaVault oltre al bootstrap minimo imposto dal protocollo, e non modificarlo;
- non eseguire test dell'autosync ghorg o run sui 65 repo;
- fai una lettura batch dei soli simboli sopra, una patch coerente, `py_compile` e test mirati;
- dopo un test fallito, correggi la causa specifica e rilancia solo quel test/gruppo;
- niente suite complete salvo nuova evidenza concreta;
- niente status/log/rev-parse duplicati a stato invariato;
- dopo PASS: un solo commit, un solo push, una sola verifica per `codex-usage-monitor`, poi operazioni roadmap e STOP.

## Acceptance criteria

PASS solo se:

- con CWD in repo A e tool call nei repo B/C/D vengono registrati esattamente B/C/D;
- il fallback CWD viene usato quando e solo quando non esistono repo espliciti risolvibili;
- ogni rollout è letto/parso una sola volta per `parse_session`/run del publisher; il wrapper non contiene più un secondo `path.read_text().splitlines()`;
- non viene introdotto alcun secondo glob/watcher;
- fetch Git fallito non può produrre `clean_synced`;
- rev-list fallito/malformato non può produrre `clean_synced`;
- clean verificato continua a produrre `clean_synced`;
- una run no-op non rifà guard/fetch per completion già registrate;
- variazioni dei soli metadata derivati del guard non causano un nuovo backfill/ripublish massivo;
- una reale correzione dello status resta comunque esportabile;
- test mirati passano;
- `codex-usage-monitor` viene committato e pushato una sola volta al termine con singola verifica finale;
- MegaVault/autosync/systemd/ghorg restano invariati;
- nessun lavoro fuori scope.

## Output finale

Solo:

- `PROMPT_ID=947261`
- `RESULT=PASS|BLOCKED|FAIL`
- `explicit_repo_fallback=PASS|FAIL`
- `single_parse=PASS|FAIL`
- `false_clean_synced_guard=PASS|FAIL`
- `historical_republish_guard=PASS|FAIL`
- test mirati eseguiti
- commit SHA `codex-usage-monitor`
- eventuale blocker reale
