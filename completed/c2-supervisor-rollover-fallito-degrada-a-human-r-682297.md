PROMPT_ID=682297

# Goal
Rendere robusto il rollover ChatGPT: un tentativo che non ottiene una conversation URL persistita ha lasciato il worker PH in human-required pur avendo checkpoint valido e chat precedente recuperabile.

# Canonical starting point
- C2 work item: wi:2e66af047c194439a8d0fbacaa937052
- Repository: gernalix/chatgpt-rdc-supervisor
- The work item scope and acceptance below are authoritative. Inspect only files needed to satisfy them.
- Use the assigned isolated worktree and the repository single-writer/integration path. Do not edit canonical branches directly.
- Do not broaden scope into unrelated cleanup, refactors or audits.
- Existing verified evidence:
  - codex-roadmap main a5873827 c2_scheduler.configure_auto requires structured execution.worktree and materialized prompt/exact metadata for Codex; this intake has no work_item_execution_specs row.
  - chatgpt-rdc-supervisor main 69b3b5cd supervisor.py rollover path still marks human-required when no persisted conversation URL.

# First bounded action
Implement bounded prior-chat rebind and focused rollover test.

# Acceptance
- Rollover ambiguo non duplica worker
- Checkpoint valido permette retry/rebind bounded senza intervento umano quando sicuro
- Testa URL non persistito e recovery

# Execution rules
- Fix only failures necessary for this goal; preserve unrelated local/runtime state.
- Use targeted tests first and widen only if evidence requires it.
- On incidental C2 bugs/bottlenecks, capture only the description to the C2 Inbox and continue.
- Stop immediately when acceptance is verified; do not wait on CI/merge in a model turn.
