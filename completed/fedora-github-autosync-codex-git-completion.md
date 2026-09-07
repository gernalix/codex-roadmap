# Fedora GitHub autosync + Codex Git completion guard

PROMPT_ID: 628431

**Modello consigliato:** GPT-5.5  
**Reasoning:** medium  
**MegaVault:** STANDARD

## Goal

Su Fedora, rendere `/home/daniele/projects` una copia locale automaticamente mantenuta dei repository GitHub dell'utente `gernalix`, usando **ghorg** invece di reimplementare discovery/clone/pull. Ogni repository `gernalix` realmente nuovo deve inoltre essere registrato automaticamente e in modo idempotente nel `megavault.sqlite` autorevole con un nuovo `project_id` permanente. Integrare inoltre un controllo Git passivo al completamento di ogni task Codex e rendere permanente la disciplina Codex `commit -> singolo push finale -> singola verifica -> STOP`.

Questa automazione deve privilegiare la sicurezza del lavoro locale: non deve mai cancellare/modificare lavoro non committato, commit non pushati, repo divergenti o copie locali di repository rimossi dal remoto.

## Scope e sorgenti autorevoli

Target Fedora locale; **non modificare Oracle VM**.

Parti soltanto da:

- `/home/daniele/projects/codex-usage-monitor`
- `codex_usage_publisher.py`
- `codex_usage_publisher_legacy.py` solo per i simboli effettivamente chiamati dal publisher corrente
- test pertinenti del publisher
- `systemd/codex-usage-publisher.{service,timer}`
- le unit/systemd helper già presenti nel repo, solo come pattern
- il corrente `MegaVault/ai/MEGAVAULT_PROTOCOL.md` **remoto** per la disciplina Git globale
- `MegaVault/megavault.sqlite` e il minimo codice/CLI MegaVault necessario a registrare in modo sicuro un nuovo progetto/repository; non fare audit generale di MegaVault

Non fare audit generale degli altri repo in `/home/daniele/projects`. Allarga la lettura solo se un riferimento concreto nei file sopra lo richiede.

## Fatti già verificati da riusare

- Il publisher Fedora corrente è `/home/daniele/projects/codex-usage-monitor/codex_usage_publisher.py` e riusa `codex_usage_publisher_legacy.py` tramite compatibility layer.
- Il runtime Codex nativo scrive le sessioni sotto `~/.codex`; l'infrastruttura corrente del publisher/archive le legge già. **Non creare un secondo watcher delle sessioni.**
- `codex-usage-publisher.timer` esiste già: riusa il suo ciclo/event detection per il controllo post-task.
- `ghorg` corrente supporta `--clone-type=user`, `--protect-local`, `--fetch-all` e `--fetch-prune`. `--protect-local` deve essere la protezione primaria: aggiorna i repo sicuri ma salta quelli con modifiche non committate o commit non pushati e preserva il branch di lavoro.
- `ghorg --prune` è concettualmente diverso da `--fetch-prune`: il primo può eliminare directory locali di repo non più remoti; **non usarlo**. `--fetch-prune` elimina soltanto remote-tracking refs obsolete ed è consentito.
- La destinazione canonica richiesta è direttamente `/home/daniele/projects/<repo>`, senza directory intermedia `gernalix/`.
- Il protocollo MegaVault corrente stabilisce che `megavault.sqlite:projects + project_aliases` è l'unica fonte dei `project_id`, che gli ID sono permanenti e non riutilizzabili, ma non impone oggi la registrazione automatica di ogni nuovo repo: questa regola va quindi implementata esplicitamente qui e resa permanente nel protocollo.
- Non memorizzare un nuovo token GitHub in chiaro: riusa l'autenticazione GitHub già funzionante (`gh auth`) e passa a ghorg il token solo a runtime se necessario.

## Fase A — ghorg + autosync sicuro

1. Verifica `gh auth status`, ownership `gernalix` e se `ghorg` è già installato. Se manca, installa la release stabile ufficiale corrente con il metodo minimo e riproducibile adatto a Fedora; preferisci installazione user-local (`~/.local/bin`) se non c'è un motivo concreto per usare root.
2. Aggiungi nel repo `codex-usage-monitor` il minimo wrapper/config versionato necessario per eseguire ghorg in modo non interattivo.
3. Configura ghorg affinché a ogni run:
   - enumeri tutti i repo GitHub dell'utente `gernalix`, inclusi nuovi repo futuri;
   - cloni i repo mancanti direttamente in `/home/daniele/projects/<repo>`;
   - aggiorni i repo esistenti solo quando sicuro usando `--protect-local`;
   - faccia fetch di tutti i branch e prune delle sole remote-tracking refs (`--fetch-all --fetch-prune`);
   - non usi mai `--prune`, `--prune-no-confirm`, `--prune-untouched*`, force reset custom o qualunque opzione che possa cancellare copie locali;
   - non tocchi repo dirty, con commit locali non pushati o in situazione non sicura;
   - non richieda una lista manuale di repository.
4. Non reimplementare discovery, clone o pull in Python/Bash: il wrapper deve limitarsi ad autenticazione, invocazione sicura di ghorg, lock anti-run-concorrenti, registrazione MegaVault descritta sotto e logging/exit code strettamente necessari.
5. Aggiungi unità `systemd --user` versionate nel repo per eseguire l'autosync ogni **5 minuti**, con `Persistent=true` e prevenzione delle esecuzioni concorrenti. Installa/abilita le unità sul Fedora reale dell'utente.
6. Un repository che sparisce da GitHub deve rimanere intatto localmente.

### Registrazione automatica dei nuovi repo in MegaVault

Dopo la discovery/sync, riconcilia i repo `gernalix` scoperti con il `megavault.sqlite` remoto/autorevole:

1. Prima di inserire qualcosa, risolvi l'esistenza tramite almeno `remote_url`, repository già registrati, slug/alias pertinenti e canonical worktree. **Non creare duplicati** se il progetto/repository è già rappresentato con un nome o alias diverso.
2. Per ogni repo realmente nuovo e non rappresentato:
   - crea un nuovo record `projects` con un `project_id` nuovo, permanente e mai riutilizzato secondo le regole MegaVault;
   - crea/aggiorna il relativo record `repositories` con almeno remote GitHub canonico, branch canonico/default branch verificato live e `canonical_worktree=/home/daniele/projects/<repo>`;
   - aggiungi alias solo se necessari e verificabili;
   - per fatti non ricavabili in modo affidabile usa `UNKNOWN`/null secondo lo schema e il protocollo: non inventare descrizioni, host, runtime, secret o integrazioni.
3. Riusa un comando/API di scrittura MegaVault già esistente se disponibile. Se non esiste, aggiungi al repository MegaVault il **minimo comando idempotente** necessario per registrare un repo/progetto; niente editing SQL sparso nel wrapper e niente nuovo registry parallelo.
4. Dopo ogni batch di nuove registrazioni esegui una sola `python3 megavault.py validate` e richiedi foreign keys/integrity PASS.
5. La registrazione futura deve avvenire automaticamente nello stesso ciclo che scopre il nuovo repo. Per mantenere il MegaVault remoto autorevole, è ammesso **solo per questa manutenzione metadata MegaVault** un commit/push automatico strettamente limitato alle modifiche prodotte dal registrar, ma soltanto se il worktree MegaVault era pulito e sincronizzato prima della registrazione. Non includere mai altre modifiche preesistenti nel commit.
6. Se MegaVault è dirty, ahead, behind/diverged, la validazione fallisce o il push metadata non è sicuro: non alterare né sovrascrivere lavoro esistente; registra l'anomalia, lascia il repo applicativo clonato/sincronizzato e ritenta la sola registrazione MegaVault a un ciclo successivo quando lo stato torna sicuro.
7. L'eccezione di auto-push sopra riguarda **esclusivamente** il metadata MegaVault creato automaticamente per nuovi repo. Non autorizza push automatici dei repository applicativi né dei commit prodotti da Codex.
8. Nella prima esecuzione reale, riconcilia anche gli attuali repo `gernalix`: registra soltanto quelli effettivamente mancanti da MegaVault e non toccare/duplicare quelli già presenti.

## Fase B — controllo Git passivo dopo `task_complete`

Integra nel publisher corrente, **senza un nuovo daemon/watch loop**, un controllo post-task eseguito quando il parser rileva il completamento reale della sessione Codex.

Requisiti:

1. Riusa il segnale/evento di task completion già disponibile nell'infrastruttura delle rollout; non usare timeout, inattività, polling della GUI o euristiche sul processo Codex.
2. Ricava dai metadati della sessione il working directory/repo interessato. Non scandire tutti i repo a ogni task completion. Se non è determinabile in modo affidabile, registra `unknown` e non indovinare.
3. Per ogni repo effettivamente associato alla sessione, classifica almeno:
   - `clean_synced`: working tree pulito e HEAD == upstream;
   - `dirty`: modifiche non committate/untracked rilevanti;
   - `ahead`: commit locali non pushati;
   - `behind`;
   - `diverged`;
   - `no_upstream` / `unknown` quando appropriato.
4. Il check può fare un singolo fetch mirato se serve a evitare un confronto stale, ma **non deve fare commit, merge, rebase, reset, pull o push**.
5. Persisti il risultato in modo leggero nello state SQLite già usato dal publisher oppure in una piccola tabella nello stesso state DB; evita un nuovo database se non necessario. Deve essere consultabile e comparire nei log/journal in caso di anomalia.
6. Il post-task guard non deve inviare progressi Telegram e non deve introdurre notifiche/chat nuove. È un controllo di sicurezza, non un secondo workflow di pubblicazione.
7. Deve essere idempotente: rileggere la stessa completion non deve creare duplicati né ripetere fetch inutilmente.

## Fase C — disciplina Git e registrazione progetti permanente per Codex

Aggiorna il corrente `MegaVault/ai/MEGAVAULT_PROTOCOL.md` remoto, senza duplicare regole esistenti, affinché la disciplina globale dica in modo inequivocabile:

- durante un normale task Codex non fare push intermedi salvo necessità esplicita del task;
- dopo acceptance PASS, per ciascun repo modificato: commit finale necessario, **un solo push finale**, poi **una sola verifica** che HEAD/upstream remoto siano sincronizzati;
- dopo quella verifica non ripetere `status`, `fetch`, `log`, `rev-parse` o audit Git equivalenti senza nuova evidenza;
- se push/verifica fallisce, investigare solo il blocker concreto; niente retry identici senza nuova evidenza;
- quando tutti gli acceptance criteria e le operazioni terminali obbligatorie sono PASS, STOP immediato;
- l'autosync esterno non sostituisce il push di Codex: Codex resta responsabile di commit+push dei cambiamenti del proprio task; il guard post-task è solo una rete di sicurezza passiva;
- quando Codex crea un nuovo progetto/repository `gernalix`, o rileva nel proprio scope un repo `gernalix` non ancora rappresentato in MegaVault, deve registrarlo in `megavault.sqlite` prima del PASS usando un nuovo `project_id` permanente e i metadata verificabili minimi, senza duplicati e senza inventare fatti.

Mantieni questa modifica globale breve e coerente con le regole token-saving già presenti.

## Safety / non-goals

- Niente GitKraken: è una GUI alternativa, non serve per questa automazione headless.
- Niente webhook/GitHub App/server pubblico: polling locale ghorg + systemd è sufficiente.
- Niente `git push` automatico esterno sui repository applicativi o sui commit prodotti da Codex; unica eccezione: il solo commit/push metadata MegaVault generato dal registrar automatico dei nuovi repo, con i guard descritti sopra.
- Niente stash automatico.
- Niente reset/force-pull/force-push.
- Niente eliminazione di repo locali perché archiviati/eliminati/rinominati sul remoto.
- Niente refactor generale di `codex-usage-monitor` o MegaVault.
- Niente modifiche ai repo applicativi soltanto per testarli.

## Test mirati

Esegui solo i test necessari:

1. test unitari mirati del nuovo Git completion guard usando repository Git temporanei per almeno `clean_synced`, `dirty`, `ahead`, `diverged/no_upstream` e idempotenza;
2. test/dry-run ghorg che dimostri la destinazione `/home/daniele/projects`, discovery user `gernalix` e protezione locale;
3. test idempotente del registrar MegaVault con un repo fixture: prima registrazione crea esattamente un progetto/repository con ID nuovo; seconda esecuzione non crea duplicati; validazione MegaVault PASS;
4. una run reale controllata dell'autosync, dopo aver fotografato lo stato Git dei repo non puliti, verificando che nessuno di essi venga modificato e che eventuali repo `gernalix` realmente mancanti vengano registrati una sola volta in MegaVault;
5. `systemctl --user` per verificare unit/timer enabled+active e prossima esecuzione;
6. test esistenti del publisher strettamente pertinenti dopo la modifica.

Non eseguire suite ampie se i test mirati passano e non emerge evidenza di regressione.

## Acceptance criteria

PASS solo se:

- ghorg stabile è installato e invocabile su Fedora;
- tutti i repo GitHub `gernalix` sono discoverable senza lista manuale e i mancanti possono essere clonati direttamente sotto `/home/daniele/projects`;
- repo con lavoro locale o commit non pushati vengono saltati senza modifiche;
- nessuna copia locale viene eliminata perché assente dal remoto;
- ogni repo `gernalix` realmente nuovo/non rappresentato viene registrato una sola volta in MegaVault con `project_id` permanente e metadata minimi verificati;
- la prima riconciliazione non crea duplicati e `python3 megavault.py validate` passa;
- le future registrazioni MegaVault sono automatiche, idempotenti e non possono inglobare/pushare modifiche preesistenti;
- il timer user autosync è realmente installato, enabled e active ogni 5 minuti;
- non esistono run concorrenti dell'autosync;
- il publisher corrente registra una sola classificazione Git per completion e non effettua push/modifiche Git;
- i test mirati passano;
- MegaVault remoto contiene sia la disciplina `commit -> unico push finale -> unica verifica -> STOP` sia la regola permanente di registrazione dei nuovi progetti/repo;
- le modifiche a `codex-usage-monitor` e MegaVault sono committate e pushate secondo la disciplina appena definita;
- nessun lavoro fuori scope è stato svolto.

## Stop condition

Appena gli acceptance criteria sono verificati, esegui le sole operazioni terminali richieste dal workflow della roadmap e STOP. Non fare audit ulteriori.

## Output finale

Solo:

- `PROMPT_ID=628431`
- `RESULT=PASS|BLOCKED|FAIL`
- versione/percorso ghorg
- stato timer autosync
- esito sintetico della prima sync: discovered / cloned / updated / protected-skipped / errors
- MegaVault reconciliation: already-registered / newly-registered / deferred / validation
- esito Git completion guard + test
- commit SHA `codex-usage-monitor`
- commit SHA MegaVault
- eventuale blocker reale, se presente
