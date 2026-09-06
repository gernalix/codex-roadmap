PROMPT_ID: 683419

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Harden the Hub Context Graph that is already on `PersonalHub/main` after the completed six-phase campaign. Do NOT redesign or reimplement the graph. Fix the concrete correctness/performance gaps below so bidirectional traversal means not only “I can see the related entity”, but also “opening it lands on that exact canonical entity”.

The existing architecture is the baseline to preserve: one canonical `personalhub.db`, N-ary Contexts, typed module adapters, dynamic Context Types, Composer, recursive Explorer and no pairwise A↔B relationship framework.

Increment `version.txt` exactly once by +1 for this goal.

## Exact starting files — verified on current PersonalHub/main
Read these in grouped passes only:
- `contracts/database/src/main/java/com/gernalix/personalhub/contracts/database/HubContextDao.kt`
- `contracts/database/src/main/java/com/gernalix/personalhub/contracts/database/HubContextEntities.kt`
- `contracts/database/src/main/java/com/gernalix/personalhub/contracts/database/HubEntityAdapter.kt`
- `core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextRepository.kt`
- `core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextRuntime.kt`
- `core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextExplorer.kt`
- `core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextComposer.kt`
- `core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextLinks.kt`
- `feature/supercontacts/src/main/java/com/supercontacts/app/hub/PeopleHubAdapter.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/hub/TimerSessionHubAdapter.kt`
- `feature/luoghi/src/main/java/com/gernalix/luoghi/hub/PlacesHubAdapter.kt`
- `feature/soldi/src/main/java/com/gernalix/personalhub/soldi/hub/SoldiTransactionHubAdapter.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/hub/SubstanceHubAdapter.kt`
- `feature/wordpulse/src/main/java/com/wordpulse/app/hub/WordSessionHubAdapter.kt`
- `app/src/main/java/com/gernalix/personalhub/PersonalHubApplication.kt`
- `app/src/androidTest/java/com/gernalix/personalhub/HubContextAllModulesDeviceTest.kt`
- `core/hub-context/src/test/java/com/gernalix/personalhub/core/hubcontext/HubContextRepositoryTest.kt`

For receiving navigation targets, open only the Activity/navigation files directly named by each adapter’s `openTarget()`. One targeted search per module is allowed if the exact detail/deep-link handler is not obvious. No module-wide scans.

## Known defects — reuse; do not rediscover broadly

### 1. “Open detail” does not yet prove exact-entity navigation
The adapters already emit entity-specific targets such as:
- Timer: `personalhub://module/timer?sessionId=...`
- Places: `personalhub://module/places?placeId=...`
- Soldi: `personalhub://module/soldi?transactionUuid=...`
- Substances: `personalhub://module/substances?substanceId=...`
- WordPulse: its session target
- People: its contact target

But several receiving Activities currently open the module root without demonstrably consuming those IDs. Fix every registered adapter so `openTarget(canonicalId)` opens the exact canonical entity/detail state, not merely the owning module.

The user-visible invariant is:
`A → related B → Open detail` must land on B itself.

### 2. N+1 in Context view resolution
`HubContextRepository.view()` currently resolves stored members with repeated single-binding lookups even though a batched `bindings(ids)` DAO method exists. Eliminate the N+1 path. Loading multiple Contexts/Explorer rows must batch bindings and summaries by entity kind as far as practical.

### 3. In-memory search in adapters
Timer currently reads all sessions and filters in Kotlin; Places reads the whole place list and filters in Kotlin. Replace large-list adapter searches with bounded DB/repository queries (`LIMIT`, stable ordering, useful indexes where needed). Review the other registered adapters only for the same concrete anti-pattern; do not rewrite already bounded SQL searches.

Search must stay responsive with years of data. Empty-query suggestions must also be bounded.

### 4. System Context Types must not be user-overwritable
`timer_activity` is a system-owned semantic template used to project Timer sessions into Places. It must not appear as an ordinary editable/deletable user template and must not be accidentally overwritten by user changes.

Implement a general distinction between system-owned/locked Context Types and user-created Context Types. Prefer an explicit persisted property + non-destructive migration if that is the cleanest invariant; do not special-case the UI only by display name.

System templates may be maintained idempotently by code. User templates remain fully editable data.

### 5. E2E must prove exact destinations
Current tests prove graph traversal and Intent construction, but acceptance for internal module links must verify actual destination state.

For every registered internal adapter:
- create/choose a known canonical entity;
- enter Explorer from a different entity;
- tap its explicit “Open detail” action;
- assert that the destination screen is showing that exact entity, not just the module root.

Do not satisfy this by intercepting internal intents with a fake Espresso handler.

For external Resources such as Workflowy, verify the emitted deep link and, when a real handler is present on the requested Pixel, verify the real handler opens. A missing external handler must remain a graceful error, never a crash.

## Architecture/safety constraints
- Preserve the N-ary graph and adapter pattern.
- No pairwise relationship tables.
- No feature implementation → feature implementation dependency.
- `app` remains composition root.
- Preserve one canonical DB and all current data.
- Keep domain-specific relations domain-specific.
- Do not redesign Composer/Explorer UX in this goal; the next roadmap task owns that.
- No broad module refactor, global search feature, graph visualization or unrelated cleanup.

## Tests / acceptance
PASS only if all of the following are demonstrated:
1. Every currently registered internal adapter opens its exact entity/detail state.
2. Internal exact-navigation E2E is proven on the safe QA package/device flow without intent interception as a substitute for destination verification.
3. Workflowy/external Resource opening remains correct and missing-handler behavior is safe.
4. Context/member resolution no longer performs one binding query per member; add a regression test or deterministic query-count/seam where practical.
5. Timer and Places adapter search are DB/repository-bounded and do not load the full history for normal search/suggestions.
6. System Context Types are persisted/identified as locked and cannot be edited/deleted by the user; user templates remain editable.
7. Any schema bump has a complete non-destructive migration and Room validation.
8. `ARCHITECTURE_BOUNDARIES=PASS`, Hub graph tests, migration tests and targeted Android E2E PASS.
9. Existing Contexts, templates, Resources and linked data survive reopen/export/import semantics.

Use the Android testing plugin/skill when applicable. Follow the PersonalHub bootstrap for final APK/install on the Pixel and notification. Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, exact-navigation fixes, N+1 fix, search changes, system-template protection, migration impact, tests/device QA, commit SHA, blocker.