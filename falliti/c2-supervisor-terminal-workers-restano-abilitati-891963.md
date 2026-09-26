PROMPT_ID=891963

# Goal
Correggere il supervisor C2 perché disabiliti automaticamente worker terminali e rispetti la priorità della lane attiva; 175908 risultava completato ma ancora enabled e worker non-PH erano attivi mentre PH era la priorità.

# Canonical starting point
- C2 work item: wi:3c7c9af3af3141b28b44f6d0016e41a4
- Repository: gernalix/chatgpt-rdc-supervisor
- The work item scope and acceptance below are authoritative. Inspect only files needed to satisfy them.
- Use the assigned isolated worktree and the repository single-writer/integration path. Do not edit canonical branches directly.
- Do not broaden scope into unrelated cleanup, refactors or audits.
- Existing verified evidence:
  - codex-roadmap main a5873827 c2_scheduler.configure_auto requires structured execution.worktree and materialized prompt/exact metadata for Codex; this intake has no work_item_execution_specs row.
  - chatgpt-rdc-supervisor main 69b3b5cd disables terminal workers only after browser COMPLETE; canonical terminal/lane gate absent.

# First bounded action
Add terminal and active-lane gate before dispatch; test stale-enabled worker.

# Acceptance
- Worker terminali vengono disabilitati automaticamente
- La priorità PH impedisce l'avvio di lane non-PH incompatibili
- Test di regressione sullo scheduler/supervisor

# Execution rules
- Fix only failures necessary for this goal; preserve unrelated local/runtime state.
- Use targeted tests first and widen only if evidence requires it.
- On incidental C2 bugs/bottlenecks, capture only the description to the C2 Inbox and continue.
- Stop immediately when acceptance is verified; do not wait on CI/merge in a model turn.
