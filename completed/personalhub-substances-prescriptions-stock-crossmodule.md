PROMPT_ID: 529184

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Substances v2 — phase 3. Rebuild the Prescriptions tab around a normalized rule: one row = one prescription for one medicine/substance, while one substance may have many prescription rows. Integrate current package doses with intake, doctor lookup from People and cost selection from Soldi without creating duplicate substances or duplicate authoritative data.

## Prerequisite
Verify narrowly that phase 1 provides canonical unique substance identity and authoritative mutation/stock commands, and phase 2 provides authoritative intake outcomes. If materially absent, stop BLOCKED; do not recreate them.

## Exact starting files — verified on PersonalHub/main
Read in grouped passes only:
- `feature/sostanze/src/main/java/com/gernalix/sostanze/data/SostanzeRepository.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/domain/SostanzeEngine.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeViewModel.kt`
- `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeApp.kt`
- `core/database/src/main/java/com/gernalix/sostanze/data/Entities.kt`
- `core/database/src/main/java/com/gernalix/sostanze/data/SostanzeDao.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/PersonalHubDatabase.kt`
- `core/database/src/main/java/com/supercontacts/app/data/local/ContactsDao.kt`
- `core/database/src/main/java/com/supercontacts/app/data/local/ContactEntity.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceDao.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceEntities.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceCapsule.kt`

Follow only the exact People/Soldi relations needed by the queries below; no audit of those modules. Increment `version.txt` exactly once by +1.

## Canonical prescription model
1. Completely replace the current Prescriptions semantics:
   - one Prescriptions entry = one prescription of one medicine/substance;
   - one substance may have zero, one or many prescription entries;
   - Home still has exactly one button/card per canonical substance, never one per prescription.
2. Creating a prescription:
   - if its name matches an existing canonical substance, link to that substance;
   - if the name has never existed, create exactly one new canonical substance through the phase-1 command and therefore one corresponding Home button/card;
   - if an archived same-name substance exists, use the phase-1 restore/reuse outcome rather than creating a duplicate.
3. Existing prescription history must remain distinct. Editing one prescription must not overwrite another same-name prescription.

## Prescriptions fields and behavior
The create/edit/read surface must support exactly these user-facing fields:

1. **Nome**
   - text input with autosuggestions from existing prescription/substance names;
   - selecting an autosuggestion for an existing name pre-fills fields 2, 3, 4, 8 and 9 from the most recent prescription with that same canonical substance/name;
   - fields 5 and 6 remain fresh/default to today; field 7 is always recalculated, never copied.

2. **Numero dosi per pacchetto / dosi residue**
   - positive integer initialized from the entered package dose count;
   - for a substance with multiple prescriptions, the current package is the most recent prescription with remaining doses > 0, ordered deterministically by ordering date, then prescription date, then id;
   - every successful Home intake for that substance decrements the current package by exactly 1;
   - blocked, duplicate, failed or insufficient-stock intakes do not decrement it;
   - undo/delete of that same intake restores exactly 1 to the same prescription/package that was decremented, so history and stock cannot drift.

3. **Dose mg**
   - positive numeric mg value for one dose.

4. **Frequenza**
   - tapping opens a picker/dialog with only `ogni giorno` or `ogni settimana`, plus a positive integer X;
   - persisted/displayed semantics are only `X al giorno` or `X a settimana`; no other recurrence form belongs to this field.

5. **Data ordinamento prescrizione**
   - tapping opens a calendar picker;
   - default is today's local date for a new entry.

6. **Data prescrizione**
   - tapping opens a calendar picker;
   - default is today's local date for a new entry.

7. **Data esaurimento stimato farmaco**
   - calculated/read-only;
   - once fields 2 and 4 are valid, calculate the projected depletion date from today's local date using current remaining doses and frequency;
   - recompute after successful intake/undo or edits affecting fields 2/4.

8. **Dottore prescrivente**
   - People-backed autosuggestion/query;
   - persist the stable People contact id, not a duplicated free-text doctor record;
   - display the current contact name. If the referenced contact is later renamed, the prescription should resolve the new name.

9. **Costo**
   - on tap, query the five most recent Soldi entries whose canonical saved name/title matches field 1;
   - each option shows the Soldi saved name/title and, on the line below, that Soldi entry's date;
   - selecting an option persists a stable reference to the selected Soldi entry/transaction using a nullable, non-destructive relationship; do not copy a second authoritative Soldi transaction into Substances;
   - in normal read mode show only the resolved cost amount, not the dropdown metadata;
   - if no matching Soldi entry exists, show a clear empty state and allow the prescription to remain without cost.

## CRUD + FAB for this tab
- Prescriptions supports create, edit and delete of individual prescription rows without deleting the substance or other prescriptions.
- The `+` FAB while Prescriptions is active creates a new prescription using the same autosuggestion/prefill logic; it must never create a duplicate substance for an existing name.
- Dialogs close only after the write succeeds; validation/write failures remain visible.

## Schema / cross-module safety
Implement the minimum non-destructive schema needed for the nine fields, remaining-dose linkage to intake undo, People contact reference and Soldi entry reference. Keep the single `personalhub.db`. Do not introduce a second database, duplicate People/Soldi rows, or broad cross-module refactors. Any migration must preserve current prescriptions and pass Room validation plus `foreign_key_check`.

## Tests / acceptance
Targeted tests must prove:
- two prescriptions with the same medicine coexist while Home still has one substance;
- unseen name creates exactly one substance; existing/archived names do not create duplicates;
- autosuggestion selection pre-fills only fields 2/3/4/8/9 from the newest matching prescription while fields 5/6 default fresh and 7 recalculates;
- daily/weekly frequency validation and depletion-date math;
- successful intake decrements exactly one current package, failure does not, and undo restores the same package;
- prescription edit/delete affects only the selected row;
- People autocomplete stores stable contact id and reflects later rename;
- Soldi picker is limited to five most recent matching entries, shows name+date while choosing, stores the selected reference, and read mode shows cost only;
- migration preserves representative existing prescriptions and database integrity.

No broad People/Soldi UI changes, no History project, no global DB import/export changes, no whole-module redesign. Stop immediately after PASS.

Final output only: `PROMPT_ID`, `RESULT`, prescription schema/model, fields/prefill, intake-dose linkage, People link, Soldi link, migration, tests, commit SHA.
