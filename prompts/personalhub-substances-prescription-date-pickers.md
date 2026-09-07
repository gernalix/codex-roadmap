PROMPT_ID: 684731

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal
In PersonalHub → Substances → Prescriptions, replace the raw numeric/epoch-day editing of the two prescription date fields with normal calendar date pickers.

The two affected fields are:
- prescription order date (`orderEpochDay` / current `Order epoch day` UI);
- prescription date (`prescriptionEpochDay` / current `Prescription epoch day` UI).

For a **new prescription**, both date fields must default to the device's current local calendar date. Tapping either field opens a calendar/date selector. The user must never need to type or understand an epoch-day number.

For an **existing prescription**, editing must initialize each picker from the date already stored for that field and preserve it unless the user changes it.

# Scope
This is a localized Substances UI/data-boundary fix. Do not redesign Prescriptions or change unrelated fields, persistence, schema, scheduling, People/Soldi links, stock logic, or dosage behavior.

Keep the existing persisted representation unless a change is strictly required; the preferred solution is UI conversion between the existing epoch-day representation and a local calendar date. Respect the PersonalHub datetime rule: user-facing date is local; persisted/exported semantics must remain compatible with the existing model.

All user-visible strings must exist in English and Italian. Do not leave technical labels such as `Order epoch day` or `Prescription epoch day` visible.

# Remote source rule
When MegaVault or codex-roadmap context is needed, consult only the current remote repositories, never local MegaVault/codex-roadmap checkouts, per the current remote `MegaVault/ai/personalhubdoc.md`.

# Pre-localized starting files
Start only from these current PersonalHub files; expand only if a referenced symbol forces one narrow lookup:
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeApp.kt` — `PrescriptionCreateDialog`, `PrescriptionEditDialog`, and current raw date fields;
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeViewModel.kt` — only if new-prescription defaults are constructed there;
- `feature/sostanze/src/main/java/com/gernalix/sostanze/data/SostanzeRepository.kt` — only if needed to confirm existing epoch-day persistence semantics;
- Substances `values/strings.xml` and `values-it/strings.xml` for the two date labels/actions.

Do not scan the repository generally.

# Required behavior
1. New prescription:
   - order date defaults to today in the device local timezone;
   - prescription date defaults to today in the device local timezone;
   - each field displays a normal localized human-readable date, not an epoch number;
   - tapping it opens a calendar/date picker.
2. Edit prescription:
   - each picker opens on and displays the currently stored date;
   - saving without changing the dates preserves the exact existing dates;
   - changing one date updates only that date.
3. Validation:
   - no free-form epoch-day input remains for these two fields;
   - locale/timezone conversion must not shift the selected calendar date by ±1 day;
   - persistence remains compatible with current prescription records.

Prefer a small reusable date-picker boundary/helper if that makes timezone/date conversion directly unit-testable; do not create a generalized date framework.

# Validation
Use the smallest sufficient tests first:
- focused unit test for today/local-date ↔ stored epoch-day conversion if conversion logic is extracted;
- focused Compose/UI or equivalent test proving default-today, existing-date initialization, and one changed date persists correctly;
- one focused live Android check of the Prescriptions create/edit flow because the calendar interaction is user-facing platform/UI behavior.

Follow the current PersonalHub bootstrap for version bump, build/device QA, final Pixel installation, clone cleanup if a QA clone is used, and final APK Telegram artifact delivery. Do not send Telegram progress/test/install status messages.

# Acceptance criteria
PASS only if:
- both Prescriptions date fields use calendar selectors;
- both default to today's local date when creating a new prescription;
- existing stored dates initialize correctly when editing;
- save/reopen preserves the selected calendar dates without timezone off-by-one errors;
- raw epoch-day numbers/labels are gone from the user-facing form;
- English and Italian UI text are present;
- focused automated tests pass;
- focused live Android validation passes;
- all mandatory final PersonalHub delivery steps from the current bootstrap pass.

Stop immediately after acceptance passes. Do not start the next roadmap task.

Final output concise: `PROMPT_ID`, `RESULT`, date-picker behavior, tests/device verification, version, Pixel install, APK delivery, commit/push, blocker if any.
