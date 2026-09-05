PROMPT_ID: 937214

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal

Fix only the Timer session tag-selection UX used when creating a new session:

1. tags that the user selects must remain clearly visible as distinct selected chips/cards in the creation dialog instead of collapsing into faint grey comma-separated text;
2. when the user types a prospective tag name, the action to create exactly that tag must remain available whenever no existing tag has that exact normalized name, even if one or more existing tags contain the typed text.

Do not change Timer data semantics, tag hierarchy semantics, session persistence, global tag matching, or unrelated screens.

## Known current evidence — reuse, do not rediscover broadly

Current `PersonalHub/main` already shows:

- `NowScreen.kt` opens a new-session draft and delegates the editor to `SessionEditDialog`;
- `SessionEditDialog.kt` contains the shared session editor and the private `SessionTagPickerDialog` used for tag search/selection;
- inside the main session dialog, selected tags are currently rendered as a single comma-separated `Text` using `onSurfaceVariant`, which explains why selected tags lose the prominent card/chip appearance;
- `SessionTagPickerDialog` already calculates `canAddTagFromQuery = q.isNotEmpty() && tags.none { it.name.equals(q, ignoreCase = true) }`, but then additionally requires `ordered.isEmpty()` before showing the create action;
- therefore typing `shop` while an existing tag `shopping` matches the search suppresses `+ create shop`, even though `shop` itself does not exist;
- the picker already uses the existing tag-selection visual component for available tags, so reuse the current visual language instead of inventing a parallel tag UI.

## Exact starting files — verified on PersonalHub/main

Read these in one grouped pass only:

- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/now/ui/NowScreen.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/ui/components/SessionEditDialog.kt`
- `version.txt`

If `SessionEditDialog.kt` directly references a shared `TagSelectionFlow`/tag-chip implementation that must be adjusted to preserve the same selected appearance, resolve that exact symbol with one targeted search only. Do not scan Timer or the repository generally.

Before code changes, increment `version.txt` exactly once by +1.

# Required behavior

## A. Selected tags stay visually distinct

In the new-session creation dialog:

- every selected tag must remain individually visible as a chip/card-like element;
- selected tags must have clear contrast between background, border/state and text and must remain obviously selected;
- do not replace them with a comma-separated plain-text summary;
- do not use a pale/disabled-looking treatment for an active selected tag;
- keep the layout usable with multiple selected tags and long names by wrapping/flowing as needed rather than hiding the selection state;
- removing/toggling a selected tag must continue to use the existing tag-selection semantics;
- preserve timed-tag restrictions and tag-parent closure/exclusion behavior.

Prefer the existing Timer tag-chip/card component and styling so the selected representation is consistent with the picker itself.

If the same `SessionEditDialog` is also used when editing an existing session, keep the visual representation consistent there unless doing so would require unrelated behavior changes.

## B. Exact typed tag can always be created unless it already exists exactly

Let `q = query.trim()` and compare names case-insensitively after trimming.

Show the action `+ create <q>` whenever:

- `q` is non-empty; and
- there is no existing non-deleted/available tag whose normalized full name equals `q`.

Existing prefix/substring/fuzzy matches must NOT suppress this action.

Required examples:

- existing tag `shopping`, query `shop` → show existing suggestion `shopping` AND show `+ create shop`;
- existing tags `shop online`, `workshop`, query `shop` → show matching existing suggestions AND show `+ create shop`;
- existing tag `shop`, query `shop` → do NOT offer a duplicate `shop`;
- existing tag `SHOP`, query ` shop ` → do NOT offer a duplicate after trim/case normalization;
- blank query → no create action.

Creating the new tag must continue to select it automatically in the session as the current `pendingSelectTagName` flow intends.

Do not alter the ordering/filtering of existing tag suggestions except as required to display the create action alongside them.

# Tests / verification

Use the smallest targeted coverage sufficient to prove:

- the create-action predicate is based on exact normalized equality, not on whether search results exist;
- `shopping` + query `shop` shows both the existing result and the create-exact action;
- exact case/trim-equivalent existing name suppresses duplicate creation;
- selected tags remain individually rendered with a selected visual state after selection and after query changes;
- multiple selected tags remain readable/wrapped rather than degrading to plain text;
- timed-tag and hierarchy selection behavior is unchanged.

Use a focused emulator UI check only if needed to prove the visual state; do not broaden into Timer-wide QA.

# Acceptance

PASS only when a new Timer session visibly keeps selected tags as distinct selected chips/cards, and typing a non-existing exact name always offers creation of that exact name even while broader existing matches are displayed. Existing exact names still cannot be duplicated, and session/tag semantics are unchanged.

Stop immediately after targeted PASS.

Final output only: `PROMPT_ID`, `RESULT`, selected-tag UI, exact-create suggestion rule, tests/device check, version, commit SHA.
