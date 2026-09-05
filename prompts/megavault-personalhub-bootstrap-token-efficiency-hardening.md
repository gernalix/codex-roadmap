PROMPT_ID: 506932

project_id: 23
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal

Remove the systematic MegaVault/PersonalHub bootstrap failures and the concrete token/tool-call waste patterns observed in recent PersonalHub Codex work, without weakening MegaVault validation or broadening scope beyond the PH execution path.

## Exact starting files — verified on current MegaVault/master

Read once, in one grouped pass:
- `ai/personalhubdoc.md`
- `ai/MEGAVAULT_PROTOCOL.md`
- `ai/GLOBAL_INDEX.md`
- `ai/megavault_core.py`
- `tests/test_megavault.py`

Do not scan other repositories. Open another MegaVault file only if a failing targeted test points to it.

## Work

1. Make `ai/personalhubdoc.md` a first-class allowed specialized bootstrap. `python3 megavault.py validate` must no longer reject this exact tracked file as “extra tracked markdown”. Keep the no-duplicate-Markdown policy fail-closed: arbitrary additional Markdown must still fail validation.
2. Make PH routing explicit and non-duplicative: PersonalHub/project_id 49 work should start from `ai/personalhubdoc.md`; the full global protocol/index is read only when that specialized bootstrap explicitly requires a fallback. Do not create a second source of truth.
3. Tighten `ai/personalhubdoc.md` only where the recent execution exposed real waste:
   - capture the PersonalHub `version.txt` base/target once for a development goal; target is base + 1 exactly once, and retries, rebuilds, test passes or corrective patch iterations inside that same goal must never bump it again;
   - prefer one coherent patch + targeted tests, then one contiguous device-validation phase; do not alternate repeatedly between patch/build/install/UI inspection after every small edit;
   - for Android UI QA, prefer stable test tags/semantics or a scripted focused flow. A full `uiautomator dump` may be used to resolve an unknown state, but repeated whole-tree dumps and blind coordinate retries are forbidden when no new evidence is gained;
   - discover the produced APK path from Gradle/output once; never guess an APK path and retry equivalent installs;
   - never batch a success Telegram message after an operation that can fail. `PH installato` is sent only after the final install has independently returned success;
   - prefer emulator → TCL → Pixel and the minimum sufficient target already defined by the PH bootstrap; do not enter a QA-package/SAF setup detour unless isolated-package testing is actually required by acceptance;
   - batch related ADB/logcat/state assertions so one device interaction can prove multiple acceptance criteria; stop immediately after PASS except mandatory terminal operations.
4. Add focused regression tests for the Markdown allowlist: the exact PH bootstrap is accepted, while an unrelated extra tracked `.md` remains rejected.

Do not change MegaVault database schema, project IDs, unrelated validation policy, PersonalHub source code, or any Android app.

## Verification

Run the smallest relevant MegaVault tests first, then exactly one final `python3 megavault.py validate`. `git diff --check` must pass. Do not repeat validation if the state is unchanged.

Stop immediately after PASS, commit and push `master`, and record the required MegaVault event only if the governing protocol requires it.

Final output only: `PROMPT_ID`, `RESULT`, validator fix, PH routing/token-efficiency changes, targeted tests, final validate result, commit SHA.