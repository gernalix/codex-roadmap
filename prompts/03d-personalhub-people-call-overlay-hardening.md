PROMPT_ID: 925471

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Fix the three concrete People/SuperContacts call-overlay defects without redesigning the feature.

## Known evidence
Start from:
- `feature/supercontacts/.../CallSystemOverlayController.kt`
- `CallStateReceiver.kt`
- `MainActivity.kt`
- `data/repository/ContactModels.kt` (`ContactDeepLink`)
- app/module manifests and only directly relevant tests.

Current defects:
1. `openContact()` builds `supercontacts://contact/<publicId>` and launches an implicit `ACTION_VIEW`, but PH declares no intent-filter that resolves that URI. The overlay button can therefore throw `ActivityNotFoundException`.
2. `show()` suspends for contact lookup on IO. `dismiss()` only removes an already-created view. If call state becomes IDLE while lookup is pending, the stale lookup can later call `showResolved()` and create an overlay after the call ended.
3. successful overlay logging includes the full phone number at INFO level.

## Work
- Make Open contact use an explicit in-app intent to `com.supercontacts.app.MainActivity` while preserving the existing deep-link `data` contract consumed by the UI. Do not export a public Activity solely to fix this.
- Add the smallest generation/request/call-state invalidation so a pending `show()` result cannot render after `dismiss()` or after a newer call request supersedes it.
- Remove/redact phone-number PII from logs. Keep only non-sensitive diagnostic metadata that is genuinely useful.
- Preserve overlay permission behavior and existing receiver/listener compatibility.

## Tests
Cover:
- generated Open-contact intent resolves explicitly and carries the correct publicId URI;
- delayed lookup + show→dismiss before lookup completion produces no overlay;
- two successive show requests cannot let the older result overwrite the newer one;
- no log message built by this path contains the raw phone number where testable.

No general People audit. Stop after PASS.

Final output only: `PROMPT_ID`, `RESULT`, deep-link fix, race fix, privacy fix, tests, commit SHA.
