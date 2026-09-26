PROMPT_ID=328371

# Goal
Eliminare il gap tra applicazione canonica di una mutation e visibilità in dashboard Workflowy. Le issue #1114–#1119 erano già chiuse/applied ma non comparivano finché non è stato eseguito manualmente roadmap-sync.

# Canonical starting point
- C2 work item: wi:cdab43b2b6b64a5f9f118deb4d34d85e
- Repository: gernalix/workflowy-importer
- The work item scope and acceptance below are authoritative. Inspect only files needed to satisfy them.
- Use the assigned isolated worktree and the repository single-writer/integration path. Do not edit canonical branches directly.
- Do not broaden scope into unrelated cleanup, refactors or audits.
- Existing verified evidence:
  - codex-roadmap main a5873827 c2_scheduler.configure_auto requires structured execution.worktree and materialized prompt/exact metadata for Codex; this intake has no work_item_execution_specs row.
  - workflowy-importer main 9542b493 uses periodic workflowy-roadmap-sync.timer; no writer-applied immediate projection trigger.

# First bounded action
Trigger idempotent Workflowy roadmap sync after applied writer mutation.

# Acceptance
- Ogni mutation applicata innesca o programma immediatamente la proiezione Workflowy
- La dashboard espone chiaramente eventuale stato pending projection
- Test E2E verifica work item visibile dopo writer apply senza intervento manuale

# Execution rules
- Fix only failures necessary for this goal; preserve unrelated local/runtime state.
- Use targeted tests first and widen only if evidence requires it.
- On incidental C2 bugs/bottlenecks, capture only the description to the C2 Inbox and continue.
- Stop immediately when acceptance is verified; do not wait on CI/merge in a model turn.
