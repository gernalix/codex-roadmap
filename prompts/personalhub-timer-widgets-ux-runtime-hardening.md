PROMPT_ID: 573842

project_id: 49
Recommended model: GPT-5.5
Reasoning: medium
MegaVault: FAST

# Goal
Complete the remaining bounded Timer maintenance in one substantial pass so Codex pays the Timer bootstrap/build/device cost once instead of four times:

1. add a configurable Android home widget for one preselected Timer `Events` button;
2. make the existing Quick Session widget report success only after the canonical session write actually commits;
3. fix new/edit-session tag-selection UX and exact-name creation;
4. remove the remaining legacy MultiTimeTracker host-version, AutoConsistency and Timer-owned DB backup/restore assumptions.

These are four internal phases of ONE Timer goal. Do not turn them back into independent sessions. Capture the PersonalHub base version once and set `target = base + 1`; increment `version.txt` exactly once for the entire goal. Run narrow checks after each phase, but perform only one explicit final APK build/install/device QA after all phases pass.

# Token/work discipline
- Read phase-local starting files only when entering that phase; do not front-load every file in this prompt.
- Reuse verified symbols/files/results from earlier phases. Never repeat bootstrap, repository discovery, equivalent searches, or equivalent tests.
- If a listed symbol moved, allow one targeted search for that exact symbol; no Timer-wide or repo-wide exploration.
- Do not refactor, clean up, modernize or audit unrelated Timer code.
- A collateral problem is reported but not investigated unless it blocks an acceptance criterion.
- Stop immediately after consolidated PASS.

# Phase A — widgets and canonical write results

## Starting files
Read in grouped passes only as needed:
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/quickevents/ui/QuickEventsScreen.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/capsules/quickevents/controller/QuickEventsCapsuleViewModel.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/QuickEventRepository.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/widget/QuickTaskRunner.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/widget/QuickTaskWidgetClickActivity.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/widget/QuickTaskWidgetProvider.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/core/session/DefaultSessionCore.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/SessionRepository.kt`
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/AuditLogSqlite.kt`
- `feature/multitimetracker/src/main/res/xml/quick_task_widget_info.xml`
- `app/src/main/AndroidManifest.xml`

Open one exact Quick Events core/executor collaborator only if the listed files directly require it. Use the existing Quick Session widget only as the Android widget/configuration pattern for the new Events widget; do not redesign it beyond the persistence-result fix below.

## A1. Existing Quick Session widget: real result contract
Known current defect: the widget can vibrate/show “started” before persistence and `QuickSessionRunner` can swallow the canonical session-row failure, then still audit/broadcast success.

Required behavior:
- Give the runner an explicit success/failure result and propagate real persistence failures.
- Success haptic/toast, SESSION_START audit, snapshot/widget broadcast and app-opening success path happen only after the canonical session row is committed.
- Failure gives concise failure feedback and must not fabricate audit/broadcast/open-as-success behavior.
- If `#temp` creation needs a preceding persistent write, keep the operation internally consistent without redesigning Timer persistence.
- Preserve idempotency and existing auto-export/sync mutation tracking.

Targeted proof: deterministic forced session-write failure produces no success feedback/audit/success broadcast; normal path creates exactly one session and corresponding audit event.

## A2. New configurable `Events` widget
Known current behavior:
- `QuickEventsScreen` renders reusable template and macro buttons.
- A normal template tap uses the canonical Quick Events flow; a macro executes its ordered actions.
- Some templates/macros require user-supplied fields/customization.

Required behavior:
- Add a separate configurable home-screen widget dedicated to Timer `Events`.
- On add/configure, show currently active Quick Event buttons and select exactly one target. Support both template and macro buttons when both exist in normal `Events` UI.
- Persist target per `appWidgetId`; multiple widget instances may target different buttons.
- Widget label reflects the selected button's current title.
- One-tap-safe targets execute the SAME canonical domain action as the in-app button, including audit/autobackup/mutation semantics. Do not create a second write implementation and do not instantiate a UI ViewModel from the widget; extract/reuse the minimum canonical executor if needed.
- Targets requiring user input open Timer directly into the corresponding preselected completion/customization flow and perform no write before user completion.
- Success feedback only after canonical write success. Persistence failure produces no false success.
- Rename refreshes the widget label. Archived/deleted/unavailable target cannot write and shows a concise unavailable/reconfigure state.
- Clean per-widget configuration on widget deletion.

Targeted proof: configure one widget; two instances target different buttons; one-tap template creates exactly one entry; macro produces the same ordered entries as in-app; required-input target opens preselected flow without premature write; rename refreshes label; deleted/archived target cannot write; forced failure has no false success; existing Quick Session behavior remains intact except for corrected success timing.

# Phase B — session tag-picker UX

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

# Phase C — legacy Timer runtime/backup cleanup

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
After A+B+C targeted checks pass:
- run the minimum combined regression tests covering the touched Timer paths;
- perform ONE explicit final PersonalHub APK build;
- safely install/update that final APK on the project-required Android targets per the governing PersonalHub protocol;
- perform ONE concise integrated QA pass covering: Quick Session success/failure, configured Events widget one-tap + required-input flow, new-session selected tags/create-exact behavior, Timer startup without legacy SAF gate, and global DB/backup navigation;
- do not repeat tests already proven unless the final integration exposes contradictory evidence.

# Non-goals
No general Timer redesign, Quick Events redesign, persistence rewrite, tag hierarchy redesign, alert redesign, broad import/export refactor, general legacy cleanup, theme work or unrelated module changes.

# Acceptance / stop
PASS only when all four original user-visible goals are satisfied together and consolidated final verification passes. Stop immediately after PASS; do not audit later roadmap tasks.

Final output only: `PROMPT_ID`, `RESULT`, Quick Session result contract, Events widget behavior, tag UX/exact-create rule, host-version/AutoConsistency/backup cleanup, targeted tests, final device QA, version, commit SHA.