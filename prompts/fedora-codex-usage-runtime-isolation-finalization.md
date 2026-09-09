# Fedora Codex usage publisher — runtime isolation + final guard hardening

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=264913 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

## Goal

Chiudere definitivamente i difetti residui di `gernalix/codex-usage-monitor` emersi dopo i prompt 628431, 781264 e 947261, senza riaprire ghorg/MegaVault autosync già funzionanti.

Il risultato deve garantire quattro cose:

1. il publisher di produzione non esegue mai file Python direttamente dal worktree in modifica: systemd usa una **release runtime stabile/versionata**, aggiornata atomicamente solo dopo test + commit + push verificati;
2. una modifica futura ai soli metadata derivati del completion guard non provoca più backfill/ripublish massivi dei cicli storici;
3. il Git guard resta conservativo anche se `git status` o la risoluzione upstream falliscono;
4. distingue i repo con **evidenza di scrittura/modifica** dai repo usati soltanto come `workdir`/lettura, così un repo di appoggio dirty non crea un falso allarme.

## Scope stretto / starting points

Parti solo da:

- `/home/daniele/projects/codex-usage-monitor/codex_usage_publisher.py`
- `/home/daniele/projects/codex-usage-monitor/codex_usage_publisher_legacy.py` solo per i simboli già coinvolti nel parsing
- `/home/daniele/projects/codex-usage-monitor/tests/test_usage_publisher.py`
- `/home/daniele/projects/codex-usage-monitor/systemd/codex-usage-publisher.service`
- `/home/daniele/projects/codex-usage-monitor/systemd/codex-usage-publisher.timer` solo per verificarne/ripristinarne lo stato; non cambiarne la cadenza salvo necessità tecnica concreta
- un nuovo helper di deploy runtime nello stesso repo solo se serve

Non modificare `github_autosync.py`, ghorg, MegaVault, PersonalHub o altri servizi. Non fare audit generale. Non leggere `~/.codex/memories/MEMORY.md`: i fatti decisivi sono qui.

## Evidenza già verificata — non riscoprirla

- Commit corrente target: `3d451e8dd348cf899c78e7f4bf39b0d21e6a56e6` (`Finalize completion guard hardening`).
- `codex-usage-publisher.timer` gira ogni minuto.
- Il service corrente esegue direttamente:
  `/usr/bin/python3 /home/daniele/projects/codex-usage-monitor/codex_usage_publisher.py run`
  con `WorkingDirectory=/home/daniele/projects/codex-usage-monitor`.
- Durante il prompt 947261 il timer ha quindi potuto eseguire codice intermedio non ancora testato/committato e `codex-usage` ha prodotto due commit denominati `usage: publish 502 prompt cycles`.
- Il parsing single-pass, il fallback CWD e `fetch/rev-list -> unknown` del commit 3d451e8d sono sostanzialmente corretti e vanno preservati.
- `classify_git_repo()` non controlla ancora esplicitamente il return code di `git status --porcelain`; inoltre l'attuale `rev-parse @{u}` non distingue in modo robusto l'assenza reale di upstream da un errore ambiguo.
- `repo_paths` rappresenta oggi qualunque path esplicito dei tool call. In una sessione reale può includere `/home/daniele/Documents/ChatGPT/Fedora` anche se quel repo è stato usato solo come directory di appoggio e non modificato.
- Il tentativo corrente di compatibilità fingerprint (`stable fingerprint` + `full fingerprint`) non ha impedito il backfill iniziale: non ripetere la stessa strategia.

## Fase 0 — proteggi il runtime live PRIMA delle modifiche

Prima di editare qualsiasi file del publisher:

1. verifica live `systemctl --user is-enabled/is-active codex-usage-publisher.timer` e annota lo stato;
2. **ferma temporaneamente il timer** (`systemctl --user stop codex-usage-publisher.timer`) e verifica che il relativo service non sia in esecuzione;
3. non disabilitare permanentemente il timer e non modificare dati per compensare la pausa;
4. da questo punto fino al deploy finale, il publisher live non deve poter eseguire il worktree mentre viene modificato.

Se non riesci a fermare il timer/service in sicurezza, `BLOCKED`: non modificare il publisher live.

## Fix A — runtime systemd stabile e atomico

Sposta l'esecuzione di produzione fuori dal worktree.

Architettura richiesta:

- usa una directory user-local stabile, preferibilmente sotto `~/.local/lib/codex-usage-monitor/`;
- crea release **immutabili/versionate per commit**, es. `releases/<git-sha>/`, contenenti solo il minimo dependency closure Python necessario al publisher;
- `current` deve puntare alla release attiva tramite switch atomico (symlink/rename atomico o equivalente);
- `codex-usage-publisher.service` deve eseguire il publisher dalla release `current`, non da `/home/daniele/projects/codex-usage-monitor`;
- niente venv: usa Python/librerie globali come da protocollo;
- il deploy helper deve rifiutare almeno: worktree dirty, HEAD non sincronizzato con upstream, file runtime mancanti o `py_compile` fallito;
- crea prima la nuova release completa, verifica, poi effettua lo switch atomico; mai modificare in-place la release `current`;
- mantieni almeno la release precedente disponibile per rollback semplice; niente sistema di release complesso oltre il necessario;
- registra nella release un manifest minimo con il commit SHA sorgente, così si può verificare quale commit sta girando.

Ordine terminale del task:

1. test sorgente;
2. commit `codex-usage-monitor`;
3. singolo push;
4. singola verifica HEAD == upstream;
5. deploy atomico di **quel commit esatto**;
6. installa/aggiorna la unit user se necessario + `daemon-reload`;
7. ripristina il timer nello stato enabled/active originario;
8. verifica che l'`ExecStart` effettivo punti alla release stabile e che manifest/current == commit pushato;
9. esegui una sola run controllata del service e verifica `Result=success`/comportamento no-op atteso.

Dopo questa migrazione, futuri edit non committati nel worktree non devono poter cambiare il comportamento del publisher live.

## Fix B — fingerprint versionato senza backfill

Sostituisci la compatibilità ad-hoc del fingerprint con una migrazione esplicita e idempotente.

Requisiti:

- definisci una versione/schema del fingerprint persistita nello state SQLite (colonna/tabella minima, senza nuovo DB);
- il fingerprint pubblicabile corrente deve escludere i soli metadata operativi derivati del guard, almeno `repo_project`, `repo_paths`, `repo_projects` ed eventuali campi equivalenti aggiunti in questo task;
- per una riga **già pubblicata** con fingerprint schema precedente, la prima lettura dopo upgrade deve seedare/convertire il nuovo fingerprint stabile **senza marcare il ciclo pending, senza export e senza Telegram**;
- questa migrazione deve avvenire una sola volta per ciclo/versione ed essere idempotente;
- dopo la migrazione, variazioni reali di contenuto pubblicabile devono continuare a triggerare update: almeno `status`, `prompt_id`, final response/eventi e token/metriche non-guard già pubblicate;
- non tentare di dedurre retroattivamente quale vecchia formula hash fosse stata usata e non fare backfill manuale di `codex-usage`;
- non riscrivere centinaia di file storici per installare il nuovo schema.

Test obbligatorio:

- prepara più cicli già pubblicati con fingerprint versione precedente; upgrade -> nessun ciclo pending/export/Telegram, solo state migration;
- seconda run -> no-op;
- dopo migration cambia solo guard metadata -> no-op;
- dopo migration cambia `UNKNOWN -> PASS` o final response -> esattamente quel ciclo diventa publishable;
- non accettare un test che verifica solo `_fingerprint()` isolatamente: deve coprire la decisione pending/export del publisher.

## Fix C — Git classification completamente conservativa

Preserva i fix già fatti e chiudi i due buchi residui:

- controlla il return code di `git status --porcelain`; errore -> `unknown` con detail esplicito, mai `clean_synced`;
- determina upstream con un comando/metodo che distingua in modo affidabile:
  - upstream realmente assente -> `no_upstream` (se il resto è valido);
  - errore nel determinare upstream -> `unknown`;
- `clean_synced` è consentito solo se branch, upstream, fetch, status e rev-list richiesti hanno tutti evidenza valida;
- niente retry, pull, reset, merge, rebase, stash o push nel guard.

Test obbligatori:

- status failure -> `unknown`;
- upstream realmente assente -> `no_upstream`;
- errore upstream -> `unknown`;
- preserva fetch failure/rev-list failure/clean/dirty/ahead/behind/diverged già pertinenti.

## Fix D — repo modificati vs repo solo usati

Non fare parsing euristico arbitrario del testo shell.

Aggiungi una distinzione minimale tra evidenza di associazione e evidenza di scrittura:

- `repo_paths/repo_projects` possono continuare a descrivere i repo associati ai tool call;
- aggiungi un insieme derivato e deduplicato di repo con **write evidence** solo quando il tool/evento strutturato dimostra una modifica, per esempio `apply_patch`/tool di file mutation con path esplicito;
- un semplice `exec_command` con `workdir` è `workdir_only` e non è automaticamente write evidence; non interpretare liberamente la stringa `cmd` per indovinare se scrive;
- il guard può conservare/classificare tutti i repo associati se utile, ma l'anomalia terminale destinata a dire "Codex ha lasciato lavoro Git" deve essere elevata come actionable soltanto per repo con write evidence; i `workdir_only` possono essere registrati separatamente/come informational senza falso allarme;
- se non esiste alcuna write evidence strutturata, mantieni comportamento conservativo e registra l'incertezza invece di inventare che un repo sia stato modificato.

Test obbligatorio:

- repo A usato solo come `exec_command.workdir` ed è dirty prima della completion;
- repo B riceve un `apply_patch`/file mutation strutturato;
- il guard conserva l'associazione ad A se necessario ma l'anomalia actionable deve riguardare B, non A;
- nessun parsing arbitrario di `cmd` introdotto.

## Test/runtime safety

- tutti gli unit test devono usare repo/SQLite temporanei;
- non toccare dati reali `codex-usage` per creare fixture;
- durante lo sviluppo il timer resta fermo, quindi nessun test/patch intermedio viene eseguito dal service reale;
- prima del deploy finale esegui solo `py_compile` + test mirati dei nuovi comportamenti e regressioni direttamente pertinenti;
- non eseguire suite complete senza nuova evidenza;
- dopo deploy, una sola run reale controllata del service è sufficiente.

## Token/tool-call discipline

Task completamente pre-localizzato:

- non leggere MEMORY.md;
- non leggere README generici, ghorg docs, MegaVault docs oltre al bootstrap minimo imposto dal launcher;
- non riesplorare `github_autosync.py`, MegaVault, altri repo o vecchi prompt;
- una lettura batch dei file/simboli sopra, una patch coerente, test mirati;
- niente retry identici;
- niente status/log/rev-parse duplicati a stato invariato;
- non avviare manualmente il publisher ripetutamente durante le patch;
- STOP appena acceptance + deploy runtime sono verificati.

## Acceptance criteria

PASS solo se:

- il timer è stato fermato prima delle modifiche al publisher e ripristinato solo dopo deploy finale;
- `systemctl --user cat/show codex-usage-publisher.service` dimostra che `ExecStart` non punta più al worktree;
- release `current` è atomica/versionata e il suo manifest indica esattamente il commit pushato;
- modificare un file del worktree dopo il deploy (test innocuo/temporaneo, poi ripristinato) non cambia hash/contenuto della release `current`;
- deploy helper rifiuta worktree dirty e HEAD non sincronizzato;
- fingerprint migration di cicli già pubblicati non crea backfill/pending/export/Telegram;
- una vera variazione post-migration resta publishable;
- `git status` failure non produce `clean_synced`;
- upstream assente e upstream error vengono distinti correttamente;
- repo workdir-only dirty non genera falso allarme actionable se un altro repo ha write evidence;
- nessun parsing arbitrario di shell command è stato introdotto;
- test mirati passano;
- una run reale post-deploy del service termina con successo;
- `codex-usage-monitor` ha un solo commit/push finale del task e HEAD == upstream;
- ghorg/MegaVault/autosync restano invariati;
- nessun backfill massivo di `codex-usage` viene provocato dal task;
- nessun lavoro fuori scope.

## Output finale

Solo:

- `PROMPT_ID=264913`
- `RESULT=PASS|BLOCKED|FAIL`
- `runtime_isolation=PASS|FAIL` + active release SHA
- `fingerprint_migration=PASS|FAIL` + historical cycles republished count
- `git_classification=PASS|FAIL`
- `write_evidence_filter=PASS|FAIL`
- timer/service final state
- test mirati eseguiti
- commit SHA `codex-usage-monitor`
- blocker reale, se presente
