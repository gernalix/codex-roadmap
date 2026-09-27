# Protect required child gates during C2 tree reconcile

## Objective and constraints

Complete `wi:ef46823e45344e4f9fa41215fddfff28`. A root
`include_descendants=true` reconciliation must not silently supersede an
unfinished required child gate. Preserve single-writer state and unrelated
PersonalHub work; make the smallest C2 source change.

## Checklist and evidence

- [x] Executor start #2809 applied; canonical status running.
- [x] Observed failure: historical root `wi:7009a...` and nested required
  Pixel gate `wi:76ac...` were superseded while QA01–QA12 remained listed.
- [x] Locate cause in `tools/c2_work_item_admin.py`: subtree bulk status
  update changed every nonterminal descendant, with no gate check.
- [x] Add a pre-mutation guard for `kind=gate`, `required=1`, nonterminal
  descendants. Preserve completed/waived/failed terminal gates.
- [x] Add focused nested-gate regression asserting root, child, gate and
  relations remain unchanged on rejection. Existing supersede coverage passes.
- [x] `PYTHONPATH=tools:tests python3 -m unittest test_c2_work_item_admin`:
  7 PASS; `git diff --check` PASS.
- [ ] Commit/push, protected PR integration, guarded pull/runtime sync.
- [ ] Strict C2 terminal PASS receipt with merged evidence.

## Blockers

None for source integration. Historical superseded Pixel QA gate is not
reopened by this source fix; its successor lifecycle remains separate.

## Next action

Commit and push the isolated branch, integrate via PR, verify merged source,
then submit and verify strict C2 PASS receipt.
