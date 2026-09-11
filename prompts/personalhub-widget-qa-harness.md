[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=742615 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Create one canonical, reusable PersonalHub Android widget QA path so future widget fixes do not repeatedly rediscover how to trigger widget taps, prepare test data, select the QA build type, or verify success/error feedback.

# Starting point
Recent Timer Event widget work exposed four recurring costs: direct launches of non-exported widget activities fail, UIAutomator toast detection is unreliable on current devices/API levels, the QA Gradle invocation is non-obvious, and shell-created SQLite/SharedPreferences fixtures are fragile because of quoting. Reuse the already-working instrumentation approach instead of exploring these dead ends again.

# Scope
Keep this to reusable Android/widget test infrastructure plus the smallest production-code seam needed for testability. Start from the existing widget instrumentation test, widget tap runner/executor, Gradle Android-test configuration, and current test helpers.

Implement the minimum coherent solution that provides:
- a canonical instrumentation helper/harness for exercising widget tap behavior inside the app package, including non-exported click activities;
- reusable Kotlin test fixtures/helpers for widget targets and domain data, without shell SQL/XML setup;
- feedback verification at a testable boundary: success/failure result and exact user-facing message/title must be unit/instrumentation-testable without depending on UIAutomator seeing a system Toast;
- one canonical Gradle command/task or tiny wrapper for the QA instrumentation path so future Codex sessions do not have to rediscover `connectedAndroidTest` + `personalhub.testBuildType=qa`;
- concise discoverability in the existing canonical developer instructions only where necessary, so future widget tasks know which command/helper to use.

Do NOT redesign widgets, change normal user-visible widget behavior, refactor unrelated Timer code, add a general testing framework, or broaden into other modules unless a shared helper is genuinely necessary.

# Verification
Use only targeted tests for the new harness/helpers and one representative widget flow. Prove at minimum:
- one widget tap records exactly one expected entry;
- failure does not produce a success result/message;
- two distinct widget targets can be exercised through the reusable path;
- the canonical QA command actually runs successfully on an available Android test target.

Do not require UIAutomator toast visibility as an acceptance condition. Do not use manual shell SQLite or SharedPreferences fixture creation as the canonical path.

If changes are test/build infrastructure only, do not bump the app version or produce/deliver a release APK solely for this task. Expand verification only if targeted evidence fails.

# Acceptance / stop
PASS when a future widget task can use one documented/canonical QA entrypoint plus reusable fixtures, with feedback correctness testable without system-toast scraping. Stop immediately after the targeted path is proven.

Final output concise: `PROMPT_ID`, `RESULT`, canonical QA command/entrypoint, reusable helpers added, representative test result, files changed, blocker if any.