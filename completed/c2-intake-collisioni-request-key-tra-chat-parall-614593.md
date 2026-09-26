PROMPT_ID=614593

# Goal
Evitare collisioni tra worker ChatGPT concorrenti che generano request-key sequenziali locali uguali, causando request_key_conflict anche per work item distinti.

# Canonical starting point
- C2 work item: wi:b505b3ee6c0e439cba2fcc107395acf2
- Repository: gernalix/codex-roadmap
- The work item scope and acceptance below are authoritative. Inspect only files needed to satisfy them.
- Use the assigned isolated worktree and the repository single-writer/integration path. Do not edit canonical branches directly.
- Do not broaden scope into unrelated cleanup, refactors or audits.
- Existing verified evidence:
  - codex-roadmap main a5873827 c2_scheduler.configure_auto requires structured execution.worktree and materialized prompt/exact metadata for Codex; this intake has no work_item_execution_specs row.
  - codex-roadmap main a5873827 submit_mutation.py detects request_key_conflict but c2_control.py still requires caller-generated keys without cross-chat namespace.

# First bounded action
Add collision-resistant task/worker namespace and test concurrent intake keys.

# Acceptance
- Le request-key prodotte da worker paralleli sono deterministicamente uniche
- Replay dello stesso comando resta idempotente
- Collisioni semantiche reali continuano a fallire chiuso

# Execution rules
- Fix only failures necessary for this goal; preserve unrelated local/runtime state.
- Use targeted tests first and widen only if evidence requires it.
- On incidental C2 bugs/bottlenecks, capture only the description to the C2 Inbox and continue.
- Stop immediately when acceptance is verified; do not wait on CI/merge in a model turn.
