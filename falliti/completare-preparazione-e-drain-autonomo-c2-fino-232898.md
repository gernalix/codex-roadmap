PROMPT_ID=232898

# Goal
Porta C2 dallo stato corrente alla quiescenza usando il control plane canonico, senza rifare lavoro già verificato.

# Starting point
- TASK_ID: wi:755cbb137d74424e8a24833b7213b8eb
- Leggi per primo operations/task-state/C2-AUTONOMOUS-DRAIN-20260927.md e riparti dal checkpoint handoff commit f3db851c.
- Verifica lo stato canonico corrente prima di mutare.

# Required work
- Completa solo le preparazioni residue indicate dal checkpoint.
- Non preparare/avviare prerequisiti manuali o esterni, PersonalHub esterno, né task_state importati come task autonomi.
- Verifica c2_worktree_guard healthy, poi ripristina c2-runtime.timer e c2-runtime.path.
- Lascia al control plane scheduling, dipendenze, resource lease, parallelismo, lifecycle, recovery e reconciliation.
- Supervisiona event-driven; prepara i successori solo quando diventano runnable e sempre dalla base canonica corrente.
- Non eseguire direttamente task applicativi al posto del loro executor.

# Stop condition
Termina solo a quiescenza: nessun runnable/schedulabile, nessun run recuperabile ignorato; ogni residuo deve essere terminale o waiting/blocked/human con blocker reale.

# Finish
Aggiorna checkpoint e C2 con evidenza finale sintetica. Usa il contratto executor canonico e non fare model-driven polling.
