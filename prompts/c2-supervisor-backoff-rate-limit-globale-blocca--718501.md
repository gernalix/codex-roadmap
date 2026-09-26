PROMPT_ID=718501

# Goal
Valutare e correggere la granularità del backoff: il supervisor ha messo PH in stalled per un global rate-limit backoff, impedendo dispatch anche dopo il ripristino manuale del worker.

# Canonical starting point
- C2 work item: wi:991539d322764f218d8d584fcb8fccba
- Repository: gernalix/chatgpt-rdc-supervisor
- The work item scope and acceptance below are authoritative. Inspect only files needed to satisfy them.
- Use the assigned isolated worktree and the repository single-writer/integration path. Do not edit canonical branches directly.
- Do not broaden scope into unrelated cleanup, refactors or audits.
- Existing verified evidence:
  - codex-roadmap main a5873827 c2_scheduler.configure_auto requires structured execution.worktree and materialized prompt/exact metadata for Codex; this intake has no work_item_execution_specs row.
  - chatgpt-rdc-supervisor main 69b3b5cd storage.py persists global backoff and supervisor.py applies it to all active workers.

# First bounded action
Prove account-wide versus worker-specific limit, then scope backoff to the verified boundary.

# Acceptance
- Backoff applicato solo alla portata realmente necessaria
- Worker riprendono automaticamente appena il vincolo scade
- Nessun retry storm o bypass di rate limit

# Execution rules
- Fix only failures necessary for this goal; preserve unrelated local/runtime state.
- Use targeted tests first and widen only if evidence requires it.
- On incidental C2 bugs/bottlenecks, capture only the description to the C2 Inbox and continue.
- Stop immediately when acceptance is verified; do not wait on CI/merge in a model turn.
