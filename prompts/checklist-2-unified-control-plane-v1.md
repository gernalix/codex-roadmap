PROMPT_ID=874695 | project_id=51 | MegaVault=STRICT

# Goal
Unifica l’attuale roadmap e i checkpoint/checklist operativi in una sola “Checklist 2.0” autorevole basata su SQLite, con proiezioni live verso Obsidian e Workflowy e orchestrazione automatica RDC→Codex. Elimina lo split-brain già osservato tra roadmap.sqlite e operations/task-state senza creare una seconda source of truth.

# Starting point verificato
- /home/daniele/projects/codex-roadmap/roadmap.sqlite è già la source of truth del lifecycle prompt.
- operations/task-state/*.md contiene stato operativo/checkpoint separato e può divergere dal DB.
- Workflowy è la dashboard operativa; Obsidian/Markdown sono già proiezioni.
- chatgpt-rdc-supervisor gestisce già recovery/checkpoint di worker ChatGPT ma non la coda Codex.
- chrome-codex-switcher espone il contratto di launch Codex; usa il runtime corrente dopo la dipendenza canonica.
- Non interferire con prompt già running né alterarne testo/metadati.

# Architettura richiesta
1. Estendi roadmap.sqlite invece di creare un DB canonico parallelo. Aggiungi solo le entità necessarie per task operativi/checklist, item gerarchici ordinati, blocker/evidence/next action, tag/relazioni, worker run/lease e checkpoint.
2. Mantieni prompts/dependencies/executions e il single-writer esistenti compatibili. PROMPT_ID resta l’identità dei task Codex; task ChatGPT/RDC senza PROMPT_ID devono avere TASK_ID stabile e possono collegarsi opzionalmente a un prompt.
3. Migra losslessly lo stato utile corrente da operations/task-state/*.md nel DB con backup/rollback e deduplica; dopo il cutover quei file diventano soltanto proiezioni generate/read-only compatibili.
4. Genera live note Obsidian dal DB con YAML tag, wikilink espliciti e backlink/bidirectional links per prompt, task, dipendenze, relazioni e progetti. Nessuna modifica manuale delle note deve diventare implicitamente canonica.
5. Estendi la dashboard Workflowy per leggere esclusivamente lo stesso DB/proiezione: Ready, Waiting, Running, Integration, Blocked/Needs fix, Done, current step, Next action, executor, modello/ragionamento e link utili.
6. Rendi RDC l’orchestratore event-driven: osserva DB/Git/processi/systemd/GitHub senza chiamate modello di polling; sceglie azioni deterministiche quando bastano e Codex solo per lavoro che richiede agente/coding/diagnostica.
7. Per Codex usa sempre metadati canonici del task; rispetta modalità Goal quando prompt_type=Goal; fail-closed se progetto/modello/ragionamento richiesti non sono applicabili. Mai fallback silenziosi.
8. Impedisci spreco token: dopo roadmap_start passa direttamente prompt canonico + worktree; vieta rediscovery generale di roadmap/memoria/MegaVault salvo mismatch concreto; nessun heartbeat al modello, nessun retry identico senza nuova evidenza.
9. Scheduler: rispetta dipendenze, manual prerequisites, lease e single-writer per repo; nessun doppio worker sullo stesso task/repo. Parallelizza soltanto failure domain indipendenti con concorrenza bounded.
10. Supervisiona Codex via stato processo/thread, worktree, checkpoint Git, integratore e telemetry codex-usage. Su freeze/crash riprendi dal checkpoint canonico; non ricostruire dalla chat.
11. Usa i dati reali codex-usage per scegliere in futuro il livello minimo sufficiente per classi di task, senza cambiare metadati di prompt già running.
12. Mantieni segreti, transcript privati e credenziali fuori dal DB/proiezioni. Non loggare prompt privati oltre al materiale canonico già previsto.

# Scope repo
Tocca solo ciò che serve in codex-roadmap e, se necessario per il cutover end-to-end, workflowy-importer, chatgpt-rdc-supervisor e chrome-codex-switcher. Per ogni repo modificato rispetta il suo single-writer/worktree; niente refactor laterali.

# Migrazione e rollout
- Prima crea backup verificabile del DB e test di migrazione/rollback.
- Importa lo stato operativo corrente senza perdere Completed/Remaining/Blockers/Evidence/Next action.
- Mantieni temporaneamente le viste legacy generate per compatibilità; nessun dual-write canonico.
- Testa con fixture sintetiche prima di assumere controllo di task reali.
- Solo dopo PASS abilita l’orchestrazione live; i prompt già running restano intoccati e vengono solo osservati.

# Acceptance
PASS solo se:
- esiste una sola fonte canonica SQLite per roadmap + checklist/checkpoint operativi;
- migrazione/rollback, FK/integrity e idempotenza PASS;
- stato legacy utile è preservato e non esistono writer canonici Markdown concorrenti;
- Obsidian si rigenera live con tag, link e backlink coerenti;
- Workflowy mostra lo stesso stato del DB senza divergenze;
- RDC decide deterministicamente executor e può lanciare un task Codex sintetico con metadati esatti, Goal quando richiesto, senza auto-fallback;
- scheduler evita collisioni same-repo e rispetta dipendenze/prerequisiti;
- supervisione/recovery usa processo+Git+DB senza polling a modello;
- un crash sintetico riprende dal checkpoint senza rifare lavoro verificato;
- telemetria costi resta passiva e utilizzabile per future scelte;
- suite mirate e un E2E sintetico live PASS;
- nessun prompt running corrente viene mutato o rilanciato.

# Stop
Dopo PASS e deploy live, finalizza una volta e STOP. Non aprire audit cosmetici o follow-up senza failure reale.