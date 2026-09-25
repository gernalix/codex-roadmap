PROMPT_ID=175908 | project_id=51 | MegaVault=STRICT

# Goal
Trasforma l’attuale roadmap/checkpoint in Checklist 2.0: UNA sola gerarchia canonica di work item in SQLite, proiettata live in Workflowy e Obsidian, con RDC come orchestratore event-driven che decide quando usare Codex. Non mantenere roadmap e checklist come due strutture canoniche separate.

# Principio dati
- Esiste un solo tipo canonico di elemento azionabile: work_item. Goal, task, fase, step e gate sono valori di kind, non sottosistemi diversi.
- Ogni work_item può avere parent_id, ordinamento, status, executor_policy, current/next action, blocker, progress derivato, project/repo e opzionalmente PROMPT_ID/TASK_ID.
- PROMPT_ID resta identità immutabile delle esecuzioni Codex, collegata al work_item; non è una seconda checklist.
- Tabelle separate sono ammesse solo per dati non equivalenti: dipendenze/relazioni, prompt materialization/metadati esecutivi, run/lease, evidence/checkpoint, eventi/audit. Lo stato di cosa resta da fare vive solo in work_items.
- Migra prompts/task-state senza dual-write canonico; dopo cutover le vecchie viste/file sono compatibility projection read-only.

# Workflowy UX obbligatoria
La vista principale deve rispondere subito a “cosa è stato fatto?” e “cosa resta?”. Mostra nell’ordine:
1. IN CORSO con work item attivi, progress tipo ✅ 17/23 · 74%, current step 👉 e Next action;
2. PRONTI, ordinati secondo scheduler reale;
3. IN ATTESA con dipendenza umana/tecnica espressa in linguaggio semplice;
4. BLOCCATI/NEEDS FIX con blocker concreto;
5. COMPLETATI RECENTEMENTE, collassati di default.
Dentro ogni goal/task espanso mostra figli con ✅/👉/☐, progress derivato dai discendenti e un solo Next action. Dettagli tecnici (branch, commit, CI, token, modello) restano secondari/collassati. Supporta filtri progetto/tag/executor/stato e wikilink/collegamenti utili.

# Progress
- Progress non stimato dal modello: completed actionable descendants / total actionable descendants; supporta pesi solo se esiste una necessità concreta e testata.
- Un parent completa solo quando i gate/figli required sono completati o esplicitamente waived.
- Current step e Next action sono univoci per ramo esecutivo.

# RDC orchestrator
- Integra nel supervisor un scheduler event-driven che legge il DB e reagisce a mutation/eventi Git/processi/systemd/GitHub; niente polling a modello.
- executor_policy = auto|codex|rdc|chatgpt|human. Auto sceglie deterministicamente: coding/test/diagnostica agentica→Codex; GUI/browser/device/runtime→RDC; operazioni deterministiche→RDC/native; attesa esterna→nessun modello; intervento umano→human.
- Rispetta dipendenze, prerequisiti, lease e single-writer per repo. Mai due worker sullo stesso work_item o repo incompatibile. Parallelizza solo failure domain indipendenti con concorrenza bounded.
- Per Codex usa metadati canonici model/reasoning/repo/worktree e Goal mode quando prompt_type=Goal; fail-closed su mismatch, nessun fallback silenzioso.
- Dopo roadmap_start passa direttamente prompt canonico + worktree + acceptance/Next action. Vietata rediscovery generale di roadmap/memoria/MegaVault salvo mismatch concreto.
- Supervisiona processo/thread, worktree, Git checkpoint, integratore e codex-usage; crash/freeze riparte dal checkpoint senza rifare lavoro verificato.

# Obsidian
Genera live dal DB note con YAML tag, parent/children, dipendenze, relazioni, progetto, stato, progress, Next action, backlink e wikilink bidirezionali. Le note non sono writer canonici.

# Migrazione
1. Backup verificabile roadmap.sqlite + rollback test.
2. Introduci schema work_items e compatibilità senza perdere PROMPT_ID, dipendenze, status history, executions e task-state.
3. Importa losslessly Completed/Remaining/Blockers/Evidence/Next action dei task-state come work item/evidence/checkpoint, deduplicando ciò che è già prompt/work item.
4. Rigenera le viste legacy da SQLite; nessun writer Markdown concorrente.
5. Aggiorna Workflowy importer alla nuova UX e Obsidian renderer.
6. Aggiorna RDC supervisor/scheduler; usa sottotask Codex repo-specifici solo se realmente necessari, con modello minimo sufficiente e senza duplicare goal indipendenti.
7. Fixture sintetica completa prima del cutover live; poi adotta task reali senza mutare/rilanciare prompt già running.

# Scope
Repo primario codex-roadmap. Se necessario, modifica workflowy-importer, chatgpt-rdc-supervisor e chrome-codex-switcher con isolamento/single-writer per repo. Niente refactor laterali.

# Acceptance
PASS solo se: una sola gerarchia work_items è fonte canonica del lavoro; roadmap/checklist non possono divergere; migrazione+rollback+FK+integrity+idempotenza PASS; stato utile legacy preservato; Workflowy mostra fatto/restante/progress/current step/Next action dalla stessa fonte; Obsidian live ha tag/link/backlink coerenti; RDC schedula executor e Codex senza polling a modello; metadata/model/reasoning/Goal mode sono esatti e fail-closed; collisioni same-repo impedite; crash sintetico riprende da checkpoint; prompt già running non vengono mutati; E2E sintetico e cutover live PASS.

Dopo PASS finalizza una volta e STOP.