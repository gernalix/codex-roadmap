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
- Current isolated branch updates `C2_EXECUTOR_CONTRACT.md` with that routing;
  contract remains exactly 500 words and `git diff --check` passes.

## Checklist

- [x] Verify canonical MegaVault rule and C2 executor start.
- [x] Draft minimal shared C2 routing rule under 500 words.
- [ ] Resume after Inbox is empty; verify exact acceptance, commit source PR,
  merge through protected lane, guarded pull/runtime sync, strict C2 receipt.

## Blocker

- Temporary user-priority hold for full C2 Inbox processing; source branch is
  durable and this work item remains running. Do not duplicate its executor.

## Next action

After the C2 Inbox is canonically empty, return to this branch and complete
the AndroidKeyStore routing task from the verified draft and acceptance.
