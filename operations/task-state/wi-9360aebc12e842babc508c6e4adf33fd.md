# wi:9360aebc12e842babc508c6e4adf33fd — Atomic prepare fence renewal

Related work item: wi:a28043e6f2e84afead5f47c94a27f651

## Objective
Make c2_prepare_codex mutations survive writer-queue latency without weakening fencing, and keep replay identity consistent with the exact fenced payload.

## Verified facts
- Planner became live and queued execution mutations #7265/#7266.
- Both were rejected as stale_or_expired_supervisor.
- Renewal #7267 was applied immediately afterward, proving an ordering race between operation and separate renewal.
- c2_prepare_codex request identity previously included fencing_token but not lease_expires_at, so a renewed fenced payload could also collide with an older request key.

## Checklist
- [x] Prepend c2_renew_supervisor atomically in every c2_prepare_codex phase mutation.
- [x] Keep the actual operation in the same writer document after renewal.
- [x] Include lease_expires_at in c2_prepare_codex transport request identity.
- [x] Preserve idempotency for identical authority + arguments.
- [x] Add regression coverage for same-expiry replay and renewed-expiry replay.
- [x] 15 targeted c2_prepare_codex/c2_mutations tests PASS.
- [x] py_compile and git diff --check PASS.
- [ ] Merge current origin/main and rerun tests.
- [ ] Commit + push + integrate.
- [ ] Deploy guarded runtime.
- [ ] Retry the two affected prepared items and verify execution specs apply.
- [ ] Submit PASS for wi:9360... and wi:a280....

## Current
Implementation verified locally; integration/readback next.

## Evidence
- GitHub Actions writer run 36704254663 rejected #7265/#7266 with stale_or_expired_supervisor and then applied renewal #7267.
- Focused tests: 15 PASS.

## Next action
Merge latest origin/main, rerun focused tests, commit/push/integrate, then re-run preparation for prompt IDs 103001 and 941059.
