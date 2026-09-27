# C2 executor contract integration

## Objective and constraints

Complete `wi:62300f2257dd4d76a743c9b3ce1b5bfd` from the verified but unmerged
prompt 233366 result. Preserve canonical single-writer state, isolated Git
integration, and the existing task history. Then run the required final gate
`wi:bea9c3476acb4386a39d64073f4938da` before terminal parent PASS.

## Checklist

- [x] Confirm parent executor start Issue #2776 applied and canonical status running.
- [x] Inspect old `task/233366` commit `fc6f8ca4` and reuse its contract.
- [x] Correct terminal entry points: prompt-backed `roadmap_finish.py`, non-prompt `c2_executor_result.py`.
- [x] Link AGENTS, README, semantic, standard prompt, and task-state docs to one contract.
- [x] Check 500-word target and targeted writer/runtime entry-point tests.
- [ ] Commit and push isolated branch; integrate through protected PR.
- [ ] Run final verification child, then submit strict parent PASS receipt.

## Verified facts and evidence

- Canonical parent acceptance requires one contract, <=700 words with <=500
  target, covered lifecycle/identities, references without competing rules, and
  targeted checks. Child final gate has eight exact acceptance strings in DB.
- Prompt 233366 is canonically complete, but its `fc6f8ca4` source commit
  remained unmerged; its finalizer text incorrectly covered non-prompt items.
- Current contract reuses that source and is under 500 words. All five linked
  documents resolve to the contract. `git diff --check` and the two targeted
  executor start/result unittest modules passed (5 tests).

## Blockers

- None for source integration. Final child cannot start while parent is running;
  after source integration, use a truthful interim parent state if required by
  the canonical lifecycle, preserving evidence for final PASS.

## Next action

Commit and push this isolated branch, create/merge the protected PR, guarded
pull main and sync runtime, then dispatch the final verification child.
