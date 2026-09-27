PROMPT_ID=158995

# Goal
Evitare che nuovi bug/colli di bottiglia/migliorie appena catturati sembrino spariti perché finiscono solo in una sezione IN ATTESA collassata; introdurre una UX che renda evidente il nuovo intake senza alterare la priorità reale.

# Canonical starting point
- C2 work item: wi:e2dd3666c60c42298e63272af94df6bd
- Repository: gernalix/workflowy-importer
- The work item scope and acceptance below are authoritative. Inspect only files needed to satisfy them.
- Use the assigned isolated worktree and the repository single-writer/integration path. Do not edit canonical branches directly.
- Do not broaden scope into unrelated cleanup, refactors or audits.
- Existing verified evidence:
  - codex-roadmap main a5873827 c2_scheduler.configure_auto requires structured execution.worktree and materialized prompt/exact metadata for Codex; this intake has no work_item_execution_specs row.
  - workflowy-importer main 9542b493 work_items_projection.py recent view includes completed only; pending intake stays collapsed.

# First bounded action
Expose newly captured pending intake in a recent/indicator view without changing priority.

# Acceptance
- I nuovi work item sono riconoscibili subito dopo il sync
- La dashboard continua a distinguere Ready da In attesa
- Nessun duplicato o falsa runnable state

# Execution rules
- Fix only failures necessary for this goal; preserve unrelated local/runtime state.
- Use targeted tests first and widen only if evidence requires it.
- On incidental C2 bugs/bottlenecks, capture only the description to the C2 Inbox and continue.
- Stop immediately when acceptance is verified; do not wait on CI/merge in a model turn.
