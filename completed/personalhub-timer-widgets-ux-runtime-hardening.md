PROMPT_ID: 573842

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Complete the remaining bounded Timer maintenance in one substantial pass so Codex pays the Timer bootstrap/build/device cost once instead of multiple times:

1. fix the already-built Timer `Events` widget configuration picker so long button lists are actually scrollable and searchable;
2. make the existing Quick Session widget report success only after the canonical session write actually commits;
3. fix new/edit-session tag-selection UX and exact-name creation;
4. remove the remaining legacy MultiTimeTracker host-version, AutoConsistency and Timer-owned DB backup/restore assumptions.

The configurable Timer `Events` widget itself was completed separately in `completed/personalhub-timer-quick-event-widget.md` with `PROMPT_ID: 314857`; do NOT rebuild or redesign that feature. A concrete usability regression is now known in its configuration Activity: with a long list of Event buttons the list cannot be scrolled, and there is no search/filter field. Fix only that picker plus the three previously pending Timer phases below.

These are four internal phases of ONE Timer goal. Do not turn them back into independent sessions. Capture the PersonalHub base version once and set `target = base + 1`; increment `version.txt` exactly once for the entire goal. Run narrow checks after each phase, but perform only one explicit final APK build/install/device QA after all phases pass.

# Token/work discipline
- Read phase-local starting files only when entering that phase; do not front-load every file in this prompt.
- Reuse verified symbols/files/results from earlier phases. Never repeat bootstrap, repository discovery, equivalent searches, or equivalent tests.
- If a listed symbol moved, allow one targeted search for that exact symbol; no Timer-wide or repo-wide exploration.
- Do not refactor, clean up, modernize or audit unrelated Timer code.
- A collateral problem is reported but not investigated unless it blocks an acceptance criterion.
- Stop immediately after consolidated PASS.

# Phase A — Events widget configuration picker usability

## Exact starting file — verified on PersonalHub/main
Read first and only:
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/widget/QuickEventWidgetConfigureActivity.kt`

Open only directly referenced string resources or the exact target model if compilation requires it. Do not inspect the rest of the Events widget implementation unless a targeted regression test fails and proves it necessary.

## Known evidence — do not rediscover broadly
Current `QuickEventWidgetConfigureActivity` builds all active templates/macros into a plain vertical `RadioGroup` inside a weighted `LinearLayout`. It has no `ScrollView`/scrolling container and no search control. On a real long list (roughly 60+ buttons in the supplied screenshot), lower items cannot be reached and there is no way to filter by name.

## Required behavior
- Keep the configuration screen simple and native; no widget redesign.
- Add a clearly visible search field immediately above the Event-button list. Use localized resources; placeholder/label equivalent to `Cerca` / `Search`.
- Filter live as the user types, across both active templates and active macros shown by this picker.
- Matching is case-insensitive and based on the human-visible title after trimming the query. A straightforward substring match is sufficient; no fuzzy-search framework.
- Empty query restores the full active list in the same deterministic order used today.
- Show a concise empty-result state when no button matches; do not confuse it with the separate “no Events exist at all” state.
- The Event-button results area must be vertically scrollable and consume the available space between search/header and the Save action. With dozens or hundreds of buttons, the user must be able to reach and select the last result.
- Keep `SAVE WIDGET` reachable outside the scrolling results area instead of forcing the user to scroll to the bottom to save.
- The software keyboard/search field must not make the list or Save action unusable on the Pixel 8a-sized viewport.
- Filtering must never silently save a hidden/different target. If the currently selected target becomes hidden by the filter, either keep that selection visibly surfaced or clear it/disable Save until a visible choice is made; never let Save commit an invisible unintended target.
- Do not auto-select a different Event merely because filtering changes the visible first row.
- Preserve the existing canonical target identity, per-widget persistence, template/macro semantics and widget update behavior.

## Targeted proof
Use the smallest deterministic UI/state coverage sufficient to prove:
- a synthetic/fixture list of at least 60 items can scroll to and select the final item;
- search for a substring returns the correct template/macro matches case-insensitively;
- clearing search restores the complete ordered list;
- no-result state is distinct from globally empty state;
- changing a filter cannot cause Save to persist a hidden/unintended target;
- Save still stores the selected target and completes widget configuration normally.

One focused device/emulator check must reproduce the screenshot-like long-list case and verify both real finger/gesture scrolling and search before leaving this phase.

# Phase B — Quick Session widget real result contract

## Starting files
Read in grouped passes only as needed:
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/widget/QuickTaskRunner.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/widget/QuickTaskWidgetClickActivity.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/widget/QuickTaskWidgetProvider.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/core/session/DefaultSessionCore.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/SessionRepository.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/AuditLogSqlite.kt`

Open one exact session collaborator only if the listed files directly require it. Do not redesign the Quick Session widget beyond the persistence-result fix below.

## Existing Quick Session widget: real result contract
Known current defect: the widget can vibrate/show “started” before persistence and `QuickSessionRunner` can swallow the canonical session-row failure, then still audit/broadcast success.

Required behavior:
- Give the runner an explicit success/failure result and propagate real persistence failures.
- Success haptic/toast, SESSION_START audit, snapshot/widget broadcast and app-opening success path happen only after the canonical session row is committed.
- Failure gives concise failure feedback and must not fabricate audit/broadcast/open-as-success behavior.
- If `#temp` creation needs a preceding persistent write, keep the operation internally consistent without redesigning Timer persistence.
- Preserve idempotency and existing auto-export/sync mutation tracking.

Targeted proof: deterministic forced session-write failure produces no success feedback/audit/success broadcast; normal path creates exactly one session and corresponding audit event.

# Phase C — session tag-picker UX

## Starting files
Read only:
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/now/ui/NowScreen.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/ui/components/SessionEditDialog.kt`

Resolve a directly referenced shared tag-chip/`TagSelectionFlow` symbol once only if needed.

Known current evidence:
- `SessionEditDialog` renders selected tags as faint comma-separated text instead of distinct selected chips/cards.
- The picker already computes an exact-name predicate but suppresses `+ create <q>` whenever broader search results exist.

Required behavior:
- Every selected tag stays individually visible as a clearly selected chip/card, with readable contrast and wrapping for multiple/long names; no comma-separated plain-text degradation.
- Preserve toggle/removal, timed-tag restrictions, hierarchy closure/exclusion semantics and existing session persistence.
- Let `q = query.trim()` and compare full names case-insensitively after trimming.
- Show `+ create <q>` whenever q is non-empty and no available existing tag has exactly that normalized full name. Prefix/substring/fuzzy matches must not suppress it.
- Examples: `shopping` + `shop` => show `shopping` and `+ create shop`; existing `shop` or `SHOP` + ` shop ` => no duplicate create action; blank => none.
- Creating the new tag continues to select it automatically. Do not change suggestion ordering beyond showing the create action alongside broader matches.

Targeted proof covers exact predicate, broader matches plus create-exact, case/trim duplicate suppression, selected-chip rendering after query changes, multiple-tag wrapping and unchanged timed/hierarchy behavior.

# Phase D — legacy Timer runtime/backup cleanup

## Starting files
Read in grouped passes only:
- `feature/multitimetracker/build.gradle.kts`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/MainViewModel.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/AutoConsistencyEngine.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/AppPatchVersion.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/core/session/AutoConsistencyCore.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/MainActivity.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/FirstRunRestoreContract.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/export/BackupFolderStore.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/SqliteVault.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/system/ImportExportCapsule.kt`
- `core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseNavigation.kt`
- `app/src/main/java/com/gernalix/personalhub/DatabaseActivity.kt`
- `app/build.gradle.kts`

Open a directly referenced patch-version asset or `ImportExportCapsuleViewModel.kt` only if required.

Required behavior:
- User-facing install/update audit uses the actual PersonalHub host package version/versionCode, never Timer's old library BuildConfig version.
- AutoConsistency uses a dedicated monotonic repair/algorithm revision, unrelated to PH release number or old Timer version.
- Mark repair revision complete only after success, proven already-consistent/no-data no-op, or another explicitly safe terminal state. Transient failure remains retryable.
- Opening Timer never blocks on legacy MultiTimer SAF setup.
- DB backup/import/restore entry points route to PersonalHub's global Database & Backup contract, not a Timer-specific folder preference or fake/stub restore path.
- Preserve genuinely separate manual CSV/JSON export only if clearly non-authoritative.
- Retire dead first-run state only as needed; preserve data, session authority, auto-export and sync semantics.

Targeted proof: host version differs from old Timer version yet audit records host version; failed consistency repair does not advance revision and retries; success/no-op does not rerun unnecessarily; fresh PH state opens Timer without legacy SAF prompt; existing-data startup remains normal; Timer DB/backup action opens global PH database UI; no Timer-specific path can claim DB restore success through stub behavior.

# Consolidated final verification
After A+B+C+D targeted checks pass:
- run the minimum combined regression tests covering the touched Timer paths;
- perform ONE explicit final PersonalHub APK build;
- safely install/update that final APK on the project-required Android targets per the governing PersonalHub protocol;
- perform ONE concise integrated QA pass covering: Events widget configuration with long scrollable list + live search/filter, Events widget execution smoke, Quick Session success/failure, new-session selected tags/create-exact behavior, Timer startup without legacy SAF gate, and global DB/backup navigation;
- do not repeat tests already proven unless the final integration exposes contradictory evidence.

# Non-goals
No general Timer redesign, Quick Events redesign, persistence rewrite, tag hierarchy redesign, alert redesign, broad import/export refactor, general legacy cleanup, theme work or unrelated module changes.

# Acceptance / stop
PASS only when the Events widget picker is scrollable/searchable on a long real list and all three previously pending Timer goals are also satisfied, with consolidated final verification passing. Stop immediately after PASS; do not audit later roadmap tasks.

Final output only: `PROMPT_ID`, `RESULT`, Events picker scroll/search behavior, Events widget regression, Quick Session result contract, tag UX/exact-create rule, host-version/AutoConsistency/backup cleanup, targeted tests, final device QA, version, commit SHA.
