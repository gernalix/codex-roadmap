PROMPT_ID=103001

Resolve work item wi:4cb1d43d39354ab0a2bc7e99e4e03751 in gernalix/PersonalHub.

C2 launch contract: this task is dispatched by the canonical C2 worker after writer-owned claim/executor_started verification. Do NOT call roadmap_start.py or c2_executor_start.py again; do not create another work item or prompt.

Goal: current main fails targeted compile in core:hub-context because HubContextLinks.kt refers to unresolved HubContextComposerDialog and HubContextExplorerDialog, blocking the existing i18n/lint gates. Diagnose current source and make the minimum source fix so the blocked gates can run.

Scope:
- Inspect only the relevant hub-context UI/source and existing references/history needed to determine whether the dialogs were renamed, moved, removed, or imports/packages drifted.
- Apply the smallest correct fix; no broad UI refactor or cleanup.
- Run the narrow compile/test/lint gate that reproduces the original unresolved references, then only the immediately unblocked i18n/lint checks if cheap.
- Do not fix unrelated warnings/failures; capture material unrelated blockers to C2 Inbox.
- Commit and push useful verified work. Stop after the original compile blocker is resolved and targeted acceptance is proven.

Acceptance:
1. HubContextLinks.kt no longer has unresolved HubContextComposerDialog/HubContextExplorerDialog references on current source.
2. The targeted core:hub-context compile passes.
3. No unrelated behavior/refactor is introduced.
4. Commit and push the verified fix.