# AndroidKeyStore C2 gate routing

## Objective and constraints

Complete `wi:9bce57e112e74e06a88189632738fcb5` without touching
PersonalHub workers or running a device gate merely to test policy text.
User steering on 2026-09-27 requires saving this work, then prioritizing total
C2 Inbox processing before resuming this task.

## Verified facts

- Executor start #2821 applied; canonical status running at last readback.
- MegaVault `/home/daniele/MegaVault/ai/MEGAVAULT_PROTOCOL.md` Android section
  already states provider-dependent AndroidKeyStore acceptance belongs on an
  emulator/device, Robolectric provider errors are environment evidence, and
  canonical `Pixel_8a` AVD is the minimum leaf before physical escalation.
- C2 had no AndroidKeyStore/Robolectric gate rule in tools/tests/docs.
- Isolated branch updates `C2_EXECUTOR_CONTRACT.md` with a dedicated Android
  gate section; contract remains exactly 500 words and `git diff --check`
  passes. A targeted check confirmed the three key terms in both C2 and the
  canonical MegaVault protocol.
- User-priority Inbox drain finished: C2 triage PASS #2962 applied, work item
  completed, guarded DB pending count 0. This task now resumes from commit
  `07b2026d` plus the present scoped wording update.

## Checklist

- [x] Verify canonical MegaVault rule and C2 executor start.
- [x] Draft minimal shared C2 routing rule under 500 words.
- [x] Resume after Inbox is empty and verify exact acceptance.
- [ ] Commit source PR, merge through protected lane, guarded pull/runtime
  sync, strict C2 receipt.

## Blocker

- None. This work item remains running under its original executor receipt;
  do not duplicate its executor.

## Next action

Commit and push this resumed branch, integrate by protected C2 PR, guarded
pull/runtime sync, then submit/read back strict C2 PASS for all three criteria.
