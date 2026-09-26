PROMPT_ID=592418

# Goal
Impedire collisioni reali tra chat parallele: durante 707603 due sessioni RDC hanno modificato lo stesso worktree PersonalHub, producendo file uncommitted concorrenti e rischio di commit parziale.

# Canonical starting point
- C2 work item: wi:84f3e2c4cc5b42b78db679d1eb02739f
- Repository: gernalix/chatgpt-rdc-supervisor
- The work item scope and acceptance below are authoritative. Inspect only files needed to satisfy them.
- Use the assigned isolated worktree and the repository single-writer/integration path. Do not edit canonical branches directly.
- Do not broaden scope into unrelated cleanup, refactors or audits.
- Existing verified evidence:
  - codex-roadmap main a5873827 c2_scheduler.configure_auto requires structured execution.worktree and materialized prompt/exact metadata for Codex; this intake has no work_item_execution_specs row.
  - chatgpt-rdc-supervisor main 69b3b5cd has no cross-chat worktree lease; C2 scheduler resource leases do not fence legacy RDC writers.

# First bounded action
Fence legacy RDC writes by canonical worktree/task lease before file or Git action.

# Acceptance
- Un work_item/worktree ha un solo writer attivo alla volta
- Claim/lease è visibile e verificato prima di ogni modifica
- Secondo worker viene reindirizzato a task indipendente o fermato prima di scrivere
- Recovery non perde modifiche già presenti

# Execution rules
- Fix only failures necessary for this goal; preserve unrelated local/runtime state.
- Use targeted tests first and widen only if evidence requires it.
- On incidental C2 bugs/bottlenecks, capture only the description to the C2 Inbox and continue.
- Stop immediately when acceptance is verified; do not wait on CI/merge in a model turn.
