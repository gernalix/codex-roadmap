[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=684731 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
In PersonalHub → Substances, replace the two technical prescription epoch-day text fields with normal calendar date selectors while preserving the existing persistence representation, and ensure a configured Substances button records its action even when the related stock is 0.

# Verified current state — reuse it
Current `PersonalHub/main` already does part of the requested behavior:
- `PrescriptionCreateDialog` computes `LocalDate.now().toEpochDay()` and passes that same `today` value as both `orderEpochDay` and `prescriptionEpochDay` when creating a prescription. The requested new-prescription default-to-today behavior therefore already exists and must be PRESERVED, not reimplemented elsewhere.
- `PrescriptionEditDialog` still exposes `orderEpochDay` and `prescriptionEpochDay` as free-form numeric text with visible labels `Order epoch day` and `Prescription epoch day`.
- persisted prescription data already uses epoch-day values, and the history screen already converts `prescriptionEpochDay` to a human date for display.

Therefore the remaining prescription defect is the create/edit UI boundary and date selection, not schema/repository/default-date logic.

# Exact scope / starting files
Start only from:
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeApp.kt` — `PrescriptionCreateDialog`, `PrescriptionEditDialog`, existing `LocalDate`/`formatDateOnly` helpers, and the configured-button tap path;
- Substances `values/strings.xml` and `values-it/strings.xml` only for user-visible date labels/actions.

Do NOT read `SostanzeViewModel`, repository, DAO, database schema or other modules unless the zero-stock tap path or a concrete compile/test failure proves they are required. Do not change the persisted epoch-day representation.

# Required behavior
- New prescription: both dates still default to the device's current local calendar date; display them as normal human-readable dates and allow tapping each to open a calendar/date picker.
- Existing prescription: each picker initializes from its stored epoch day and saving without changes preserves that exact date.
- Changing one picker changes only that field.
- No free-form epoch-day field or technical epoch-day label remains visible.
- Calendar ↔ epoch-day conversion must be based on `LocalDate` semantics so timezone conversion cannot shift the selected day by ±1.
- English and Italian user-visible text must be present.
- Tapping any configured Substances action button must create its normal record even when the related current stock is exactly 0. Zero stock must not reject, suppress or silently drop the action; use the existing successful-tap recording path and keep its normal inventory/ledger semantics. Do not add an automatic purchase, refill or unrelated stock workflow.

Prefer the smallest local reusable date-field/picker composable/helper inside the existing UI file if useful; do not create a generalized date framework.

# Verification
Use the smallest sufficient coverage:
- focused conversion/helper unit test only if new conversion logic warrants one;
- focused UI test for new-prescription today display, existing-date initialization and changing one date;
- one focused test proving that a configured-button tap at stock 0 creates exactly one normal record;
- one focused live Android create/edit check of the two date pickers and one zero-stock button check.

Do not test unrelated Substances behavior. Follow the current remote PersonalHub bootstrap for one version bump, final tested APK, Pixel install, Telegram APK delivery and clone cleanup if applicable.

# Acceptance / stop
PASS only if both date fields use calendar selectors, the already-working default-to-today behavior remains intact, existing dates round-trip exactly, raw epoch-day UI is gone, i18n is complete, a configured Substances button at stock 0 creates exactly one normal record, and targeted checks pass. Stop immediately after PASS.

Final output concise: `PROMPT_ID`, `RESULT`, preserved today default, create/edit picker behavior, zero-stock button result, tests/device check, version, Pixel install, APK delivery, commit/push, blocker if any.
