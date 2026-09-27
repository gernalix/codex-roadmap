# Final gate for the C2 executor contract

## Objective and constraints

Verify `wi:bea9c3476acb4386a39d64073f4938da` against all eight canonical
acceptance criteria. The parent `wi:62300f2257dd4d76a743c9b3ce1b5bfd`
was temporarily BLOCKED only to release this required child. Use the protected
C2 Git path and a strict single-writer terminal receipt.

## Checklist and evidence

- [x] Child executor start Issue #2798 applied; canonical status running.
- [x] Merged PR #2793 supplied a single `C2_EXECUTOR_CONTRACT.md`, referenced
  by AGENTS, README, standard prompt, semantic guide, and task-state guide.
- [x] Targeted review found Codex intake preparation and prompt report
  formatting lived only in AGENTS; add both to the shared contract. Clarify
  the README terminal rule as prompt-specific.
- [x] Contract remains 496 words and uses only headings/bullets.
- [x] `git diff --check` and 24 targeted prepare/start/result/finish tests PASS.
- [ ] Commit/push and merge final gate patch; guarded pull and runtime sync.
- [ ] Submit strict child PASS; verify applied. Then submit strict parent PASS.

## Blockers

None for source integration. Terminal receipts wait for protected merge.

## Next action

Commit and push this final gate patch, merge its PR after required checks,
guarded pull/sync, then submit and verify child and parent PASS receipts.
