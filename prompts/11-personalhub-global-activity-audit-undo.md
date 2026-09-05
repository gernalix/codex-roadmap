PROMPT_ID: 584213

project_id: 49
Recommended model: GPT-5.6 Sol
Reasoning: medium
MegaVault: STRICT

# Goal
Implement in PersonalHub a global, human-readable activity/audit register that automatically records every semantic persistent modification to PH user data and settings across all current modules, plus relevant app/system lifecycle events, and allows safe undo wherever the change is actually reversible.

This is a cross-cutting persistence feature, not a passive UI logger. Implement the minimum central infrastructure needed so current write paths emit complete semantic audit data without raw/mysterious IDs in the normal UI.

Known decisive state to reuse instead of rediscovering broadly:
- PH home currently renders module cards from `HubModule.entries` in `MainActivity`; `HubModule` also participates in launcher-shortcut settings.
- MultiTimeTracker already contains a module-local audit-log implementation under `feature/multitimetracker/.../capsules/auditlog`; inspect/reuse it only as prior art where useful, but do not make it the global source of truth blindly and do not create duplicate Timer events.
- PH has a unified Room database and central/shared mutation/export infrastructure. Preserve the already-fixed generation-based SAF auto-export semantics and the no-idle-loop guarantee.
- Current modules include at least People, Timer, Places, Substances, WordPulse and Soldi; also cover Settings and System events.

## 1. Global audit model
Add an append-only global audit/event journal in PH core persistence. Adapt naming to the existing architecture, but it must support at least the equivalent of:

- stable event id;
- timestamp;
- module/category;
- semantic action;
- entity type + internal entity identity;
- `entity_label_snapshot` or equivalent human-readable label captured at event time, so deleted entities remain understandable later;
- source/origin such as user, import, sync, worker, system, undo;
- before snapshot when needed;
- after snapshot when needed;
- grouping id for one semantic user action that causes multiple low-level changes;
- undo/reversibility metadata/status;
- link from an original event/group to the compensating event that reverted it;
- app version/versionCode at event time where relevant;
- payload/schema version for stored snapshots so future migrations remain possible.

Internal IDs are allowed in persistence, but the normal UI must never present unexplained UUIDs/row IDs/foreign keys to the user. Resolve/display names and capture label snapshots at mutation time.

Do NOT use raw SQLite triggers as the primary audit source. They lack semantic context, do not cover settings/app lifecycle cleanly, and tend to expose low-level IDs. Prefer a centralized semantic mutation/audit boundary integrated with the current repositories/DAOs/coordinators. A defensive low-level mechanism is acceptable only if it cannot duplicate semantic events and is justified by a real uncovered write path.

## 2. Coverage: log every meaningful persistent change
Systematically cover all current PH paths that can persist user-facing data or settings, including INSERT/UPDATE/DELETE equivalents, imports, sync-applied user-data mutations, workers/background actions that modify user data, and settings stored outside Room.

Examples of expected visible text:
- `Soldi · Aggiunta transazione “Netto — 42,50 DKK” al conto Revolut`
- `People · “Mario Rossi”: telefono cambiato da … a …`
- `Places · Eliminato luogo “Netto, Valby”`
- `Impostazioni · Tema cambiato da Chiaro a Scuro`
- `Sistema · PersonalHub aggiornata da v16 a v17`

“Ogni modifica” means every semantic persistent user-data/settings modification, including changes arriving through import/sync/background paths. Do NOT flood the register with internal bookkeeping writes such as sync cursors, export generations, audit-table writes, temporary/cache state, or equivalent infrastructure metadata. If infrastructure behavior itself matters to the user, represent it as one meaningful `Sistema` event instead.

Audit writes must never recursively audit themselves.

When mutation and audit event live in the same database, make them atomic in the same transaction where practical: either both persist or neither does. For settings/external stores, implement the safest equivalent ordering/compensation possible.

## 3. Group low-level changes without losing completeness
One user action may produce many DB writes. Preserve complete detail, but group them semantically with a `group_id` or equivalent.

Example: importing one receipt that causes 34 persistent changes should appear as one top-level row such as:
`Soldi · Importato scontrino Netto — 34 modifiche`
with an expandable detail view containing all underlying changes.

Do not discard or summarize away the underlying events: every audited change must remain inspectable in the full register. Avoid duplicate top-level + child logging of the same semantic fact.

## 4. Safe undo as compensating operations
For every event/group that can safely be reversed, show an undo affordance. Prefer a `↩︎` icon rather than an `X`, because `X` implies deleting the log entry. If current design constraints require `X`, its accessibility/action label must clearly mean `Annulla modifica`, not “delete audit event”.

Undo MUST NOT delete or rewrite history. The audit journal remains append-only. Executing undo creates a new compensating mutation and a new audit event linked to the original; mark/reference the original as reverted through status/link metadata.

Expected inverse semantics:
- original INSERT -> remove the created entity if still safe;
- original UPDATE -> restore the previous snapshot;
- original DELETE -> recreate the previous snapshot;
- setting change -> restore the previous value;
- bulk/import group -> reverse the reversible group atomically;
- app install/update lifecycle events -> not undoable.

Implement conflict-aware undo. Never blindly overwrite newer state. Example: if event A changes 100→120 and a later event B changes 120→150, undoing A must NOT restore 100 over the later value. Require an appropriate current-state/version/hash precondition before applying the inverse. If the precondition fails, do not mutate data and show a concise human-readable reason that the event can no longer be safely undone.

For grouped actions, prefer all-or-nothing reversal: validate all inverse preconditions first, then apply the whole reversible group atomically. Never leave a partially reverted group. Individual child undo is allowed only when it is independently safe and cannot violate group/domain invariants.

Foreign-key/dependency integrity must be respected; if restoring/removing an entity would violate current relationships or overwrite newer data, fail closed instead of forcing the undo.

## 5. App install/update + DB migration events
On app startup, compare the current app version/versionCode with the last version recorded by this mechanism and emit at most the appropriate semantic event:
- first known run/new install: `Sistema · PersonalHub installata — vX`;
- update: `Sistema · PersonalHub aggiornata — vX → vY`.

Do not emit the same startup/version event repeatedly. Store versionCode internally even if versionName is what the UI primarily shows.

An app cannot reliably record its own uninstall after removal; do not fake support for that.

For Room/schema migrations, do NOT log every SQL statement. Emit one semantic system event such as:
`Sistema · Database migrato dallo schema N allo schema N+1`
when an actual migration occurred.

## 6. Privacy and snapshot safety
Do not indiscriminately serialize secrets, auth tokens, API keys, credentials, encryption material, large opaque blobs, or other non-displayable sensitive infrastructure fields into audit payloads. Each domain should expose only the minimum fields needed for human-readable history and safe undo. Redact/omit non-auditable secret fields.

Use versioned structured snapshots rather than fragile display strings as the source for undo. Display text is presentation only.

## 7. Registro attività UI
Expose the feature from the PH home as a card/module named `Registro attività`, visually consistent with the existing module cards. The home card itself must NOT embed a 5–8 item preview list. It is a compact module tile; tapping it opens the register.

Because PH home currently derives cards from `HubModule.entries` and that enum also powers shortcut settings, integrate the new module without breaking launcher-shortcut behavior. If the standard module-registration path necessarily implies a launcher shortcut, provide a valid minimal shortcut/activity alias; do not leave a broken/special-case HubModule entry merely to get a home card.

The full `Registro attività` screen must expose ALL stored events with no arbitrary historical limit. Use lazy loading/paging/virtualized Compose lists so a large history remains performant; “show all” does not mean loading the entire table into memory at once.

Each row should show at least:
- timestamp/date in a readable form;
- module/category;
- concise human-readable event description;
- undo affordance only when currently reversible;
- reverted/conflict/non-reversible status where applicable.

Grouped events are expandable to inspect their child changes.

No normal row should expose mysterious technical IDs.

## 8. Module filter
Add a compact filter button using the emoji `🎛️` in the register UI. Tapping it opens a modal/dialog with multi-select checkboxes to select/deselect which categories are visible.

At minimum support:
- Tutti
- People
- Timer
- Places
- Substances
- WordPulse
- Soldi
- Impostazioni
- Sistema

Provide `Reimposta` and `Applica` actions or equivalent clear semantics. Persist the selected filter across app restarts.

The filter affects DISPLAY ONLY. It must never disable, skip, delete, or alter audit capture.

Prefer deriving available module/category choices from the registered/current audit categories where practical so future modules can appear without silently becoming unfilterable. New/unknown categories must default to visible rather than disappearing due to an old saved filter.

## 9. Preserve existing infrastructure behavior
Audit integration must not reintroduce the prior auto-export idle loop or create export storms. Audit writes that accompany a user mutation should participate in the same semantic mutation/transaction/generation where the current architecture allows, rather than independently scheduling redundant exports. Internal sync/export bookkeeping remains excluded from audit recursion.

Preserve local-first sync, backup/export/recovery, existing migrations and real-user data. Do not redesign Datasette sync, SAF export, backup, or unrelated module architecture.

## 10. Existing Timer audit
Inspect the existing MultiTimeTracker audit implementation only enough to decide whether to reuse, bridge, migrate, or retire its local presentation/storage. The final behavior must have one coherent PH-wide register and must not double-log Timer mutations. Preserve any Timer-specific functionality that is still materially useful unless superseded by the global implementation.

## Scope / resource discipline
This task is intentionally cross-cutting, but do not perform a generic repository audit. Start from MegaVault project 49, `AGENTS.md`, the unified DB/mutation infrastructure, current module repositories/DAOs that actually write persistent user data, Hub settings stores, `MainActivity`/`HubModule`, and the existing Timer audit implementation. Expand only to concrete write paths needed to prove complete coverage.

No unrelated refactors, cleanup, visual redesign, event-sourcing rewrite, sync redesign, backup redesign, or speculative analytics.

Respect all existing guardrails protecting the real installed PH app and user data. Never test undo destructively against irreplaceable live data; use unit/integration fixtures or approved disposable test data.

## Acceptance
PASS only if all of the following are verified:
1. A safe Room migration adds the global audit persistence without losing existing PH data.
2. Representative INSERT, UPDATE and DELETE mutations from every current module that has persistent mutable user data produce correct semantic audit events, including representative import/sync/background-originated mutations where such paths exist.
3. Persistent Settings changes are audited semantically.
4. First-run/install, app-version update and actual DB migration events follow the one-event semantics above and do not repeat on every launch.
5. Audit events are human-readable and deleted entities retain meaningful labels without DB-ID-only output.
6. Multi-write actions can be grouped while every underlying change remains inspectable.
7. Undo works for representative INSERT/UPDATE/DELETE/setting/group cases, creates compensating audit history, and does not erase the original event.
8. A stale/conflicting undo is rejected without overwriting newer state; grouped undo cannot partially apply.
9. Secrets/tokens are absent from persisted audit snapshots and normal UI.
10. Audit logging does not recursively log itself and does not cause an idle auto-export loop or redundant export storm.
11. PH home contains the compact `Registro attività` module card; tapping it opens the full history.
12. Full history has no arbitrary event-count limit and remains lazy/paged rather than eagerly loading all rows.
13. `🎛️` opens the persisted multi-select category filter; filtering changes only visibility, not capture; new/unknown categories remain visible by default.
14. Existing Timer audit behavior is integrated without duplicate Timer events.
15. Targeted build/tests pass. Perform only the narrowest safe device/emulator checks needed for the new home card, register UI, filter, and a disposable reversible event. Do not use live irreplaceable data to test destructive undo.

Stop immediately after all acceptance criteria PASS. If any current persistent mutation path cannot be safely covered, do not claim PASS: report the exact uncovered path/blocker and stop.

Final output only: `PROMPT_ID`, `RESULT`, audit architecture, covered modules/write sources, schema/migration, grouping behavior, undo/conflict behavior, install/update/migration behavior, Timer-audit integration, privacy/redaction, UI/filter behavior, auto-export/no-recursion verification, targeted tests/device checks, commit SHA.