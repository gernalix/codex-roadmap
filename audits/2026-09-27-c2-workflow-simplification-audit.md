Sì. Ho ispezionato il repo C2/`codex-roadmap` in sola lettura sul `HEAD 8435bf73...`, separando le modifiche locali attualmente in corso. Il problema principale non è un singolo blocker: è **l’accumulo di più generazioni di protocolli che convivono**.

### Dove snellirei

| Impatto | Area | Cosa vedo | Cosa farei |
|---|---|---|---|
| **Molto alto** | **Compatibilità post-cutover** | Il DB è già definitivamente nel nuovo modello (`prompts` è una view), ma il runtime continua a portarsi dietro `c2_cutover_writer`, `work_items_migration`, `work_items_cutover`, `work_items_state_import`, vari controlli `work_items_cutover_active()` e recovery transitori. Solo questo blocco vale circa **2.000 LOC**. | Dichiarare il cutover concluso come invariante. Spostare migration/cutover in tooling offline/archivio e rimuovere i branch dual-mode dal normale runtime. |
| **Molto alto** | **Chiusura dei task** | `c2_scheduler.py` ha molti modi diversi di “finire” lavoro: `executor_result`, `finish_browser_work_item`, `verify_work_item`, `complete_verified`, `complete`, `reconcile_terminal_run`; `roadmap_finish.py` e `roadmap_result.py` aggiungono altri strati. La stessa query sui figli obbligatori è copiata **5 volte**. | Una sola primitive canonica `finalize/result`. Browser, Codex, manuale e native diventano sottili adapter. L’integrazione Git deve essere un evento separato, non un altro protocollo di completion. |
| **Molto alto** | **Trasporto delle mutazioni** | Anche un minuscolo `executor_started` passa per **GitHub Issue → GitHub Action → checkout → SQLite → render → commit → push → close Issue**. `c2_runtime`, start/result, override, supervisor ecc. passano tutti di qui. | **Tenere il single writer**, ma dare al C2 locale una coda/writer locale serializzato. GitHub Issue resta fallback per veri caller remoti e disaster recovery. È probabilmente il singolo intervento con maggior riduzione di latenza e failure mode. |
| **Molto alto** | **Proiezioni generate in Git** | Workflowy è dichiarato unico cockpit umano e SQLite canonico, ma il writer continua a versionare `roadmap.md`, `spiegazioni.md`, `prompt-registry.md`, Obsidian, `completed/`, `falliti/`, ecc. Sono **851 file tracked di compatibilità**. `roadmap.sqlite` pesa ~9,9 MB; `.git` ~131 MB; **111 degli ultimi 120 commit** hanno modificato il DB binario. | Non rigenerare/committare tutte le proiezioni a ogni micro-mutazione. Generarle on-demand o periodicamente. Più avanti valuterei anche SQLite come snapshot ricostruibile invece che blob Git modificato continuamente. |
| **Alto** | **PROMPT_ID vs work_item_id vs run_id** | L’identità viene tradotta continuamente. 14 file Python gestiscono contemporaneamente PROMPT_ID e work-item ID. Il task `999198` documenta già un vero FK failure causato da mapping errato fra `prompt:<id>` e `wi:...`. | `work_item_id` unica identità interna. `PROMPT_ID` diventa solo alias esterno per Codex/UI; `run_id` solo figlio di esecuzione. Risoluzione dell’alias una volta al boundary. |
| **Alto** | **Checkpoint duplicati** | Lo stato operativo può stare contemporaneamente in `operations/task-state/*.md`, `work_item_checkpoints`, `work_item_runs.checkpoint_commit` e receipt finali. Ci sono 37 file Markdown di checkpoint, ~412 KB. Inoltre `c2_worker.py` dice che i checkpoint sono opzionali, mentre `AGENTS.md` li rende obbligatori per quasi ogni task non banale. | SQLite come checkpoint canonico. Markdown/Git soltanto per task molto lunghi/rischiosi o come proiezione generata. Eliminerei l’obbligo blanket di commit+push di task-state. |
| **Alto** | **Protocollo PROMPT_ID vecchio** | `AGENTS.md` impone ancora `MegaVault allocate → roadmap mutation → MegaVault materialize`. Ma `c2_identity.py` ha già il registry importato e `c2_intake.prepare_codex()` **alloca e materializza atomicamente nel writer C2**. | Il percorso C2 nativo deve diventare l’unico normale. Il vecchio bridge MegaVault va relegato a compatibilità esterna/legacy. Questo elimina più round-trip e molta istruzione procedurale. |
| **Medio-alto** | **Start duplicato** | `AGENTS.md` continua a definire `roadmap_start.py` obbligatorio, mentre un run gestito da C2 viene già portato `running` dallo scheduler e riceve `executor_started`. Molti prompt storici contengono ancora istruzioni `roadmap_start.py`. | `roadmap_start.py` solo per avvio manuale/legacy. Un worker già schedulato da C2 non deve rifare claim, pull, mutation Issue e setup. |
| **Medio** | **Ordinamento** | Lo scheduler combina `manual_rank`, P0/P1/P2, `sort_order`, data di creazione e anche `drain_first`. Sono troppi modi parzialmente sovrapposti per rispondere a “cosa viene prima?”. | Una funzione/view `effective_order` canonica usata sia da Workflowy sia dallo scheduler. `drain_first` resta al massimo un filtro temporaneo di lane, non un altro sistema di ranking. |
| **Medio** | **Schema installato a runtime** | Ho trovato **21** call-site `install_schema()`; alcune operazioni di lettura finiscono per verificare/creare/rifare schema/view. È tipico di una fase di transizione che è diventata permanente. | Migrazioni versionate una volta. Il runtime dovrebbe solo verificare `schema_version`, non costruire lo schema opportunisticamente. |

### Il punto più indicativo

`AGENTS.md` è ormai in parte un **fossile stratificato**: contiene precauzioni corrette, ma anche procedure nate prima delle capacità che C2 ha acquisito successivamente. Il caso MegaVault è particolarmente chiaro: la regola impone diversi passaggi remoti che il codice nuovo ha già condensato atomicamente.

Lo stesso vale per `roadmap_start`, checkpoint Git e alcuni percorsi terminali. In pratica, nuove feature sono state aggiunte **senza rimuovere completamente il protocollo precedente**.

### Cosa non eliminerei

Terrei il **single-writer come proprietà**, le resource lease sui dispositivi/worktree condivisi, le receipt idempotenti e il fencing contro supervisor stale. In particolare il doppio controllo del supervisor sembra complesso, ma ha già bloccato concretamente una renewal stale: qui la complessità compra affidabilità. Il punto è rendere queste garanzie **interne e invisibili**, non chiedere a ogni executor/modello di ritualizzarle.

### Sequenza che adotterei

1. **Pulizia immediata delle regole obsolete**: vecchio protocollo MegaVault, doppio start, obbligo indiscriminato dei Markdown checkpoint.
2. **Unificare completion + identità**: un terminal path e `work_item_id` interno unico.
3. **Congelare il cutover** e togliere migration/compatibility dalla hot path.
4. **Ridurre drasticamente le proiezioni Git**.
5. **Sostituire GitHub Issues come IPC locale**, conservando esattamente lo stesso single writer e GitHub come fallback remoto.
6. Solo dopo, semplificare ordinamento e API minori.

Questa non sarebbe una semplice “pulizia estetica”: secondo quanto ho visto, può togliere **migliaia di LOC dalla superficie operativa**, diversi round-trip per task e una buona parte dei blocker artificiali senza indebolire le protezioni importanti.

Durante l’audit sono emersi due difetti abbastanza concreti da essere registrati automaticamente nella C2 Inbox: **#2428** per la scarsa discoverability del CLI di intake e **#2434** per il protocollo PROMPT_ID/MegaVault ormai obsoleto rispetto al writer C2.
