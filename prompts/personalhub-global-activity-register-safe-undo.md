[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=835204 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Build one canonical PersonalHub `Registro attività` end-to-end:
1. semantic append-only audit capture with bounded/paged reads;
2. safe compensating undo with stale/conflict detection and grouping;
3. home entry + paged/filterable history/undo UI over that SAME model.

This is one feature and should remain one Codex goal so backend/read-model/UI are designed once. Capture base app version once; `target = base + 1` exactly once. One final build/install/device QA only.

# Verified current state — reuse, do not rediscover
Current `PersonalHub/main` does NOT yet have a global activity-register entity/service or a `Registro attività` home destination.

Existing partial audit/history mechanisms must be treated as inputs to rationalize, not as proof the goal is done:
- Timer already has `TimerAuditEvents` in the global Room DB and `feature/multitimetracker/.../AuditLogSqlite.kt`; QuickEvents and other Timer paths already call semantic `logUserEvent(...)` APIs.
- Places already has Room entities `HistoryAuditLogEntity` / `HistoryActionEntity` for its own history/undo domain.
- these are module-specific mechanisms; there is no one app-wide semantic journal/read model/undo surface yet.
- `app/MainActivity.kt` currently renders only normal `HubModule` tiles/settings/version; no activity-register card exists.

Do not re-audit whether those mechanisms exist. Inspect their exact shape only when designing the bridge/canonical migration path.

Use the canonical database-migration framework from the earlier roadmap task if completed; do not build another migration system here.

# Narrow starting boundaries
Grouped reads only as needed:
- `core/database/.../PersonalHubDatabase.kt`, `DatabaseGate.kt`, `DatabaseVault.kt`, sync `SyncJournal.kt`;
- authoritative write boundaries: FinanceCapsule, ContactsRepository, SessionRepository + Timer AuditLogSqlite, PlaceRepository, SostanzeRepository, WordRepository, HubSettings;
- only the concrete Places history/audit definitions referenced by `PlaceRepository` when needed;
- final shell integration: `app/MainActivity.kt` and `LauncherShortcutsCapsule.kt` only.

Follow direct command collaborators only. No module-tree scan, repeated mutation inventory, or second UI-specific persistence model.

# A. Canonical semantic audit
Add the minimum global append-only persistence/read model. Each event/group supports as applicable:
- stable ID + timestamp;
- module/category/action;
- entity type/stable identity + readable label/description snapshot;
- source/origin;
- versioned structured before/after data sufficient for readable detail + safe inverse checks;
- group/parent relation for one logical action;
- reversibility/status metadata;
- app version + payload/schema version.

Never store tokens/credentials/secrets or large opaque blobs.

Capture semantic persistent mutations at authoritative domain/repository boundaries, not generic SQLite triggers. Audit + domain mutation should be atomic where architecture permits; never recursively audit audit rows. Cover representative meaningful INSERT/UPDATE/DELETE/settings plus applicable import/sync/background/lifecycle semantics, excluding bookkeeping noise.

Bridge/retire/adapt existing Timer and Places audit/history only as necessary to provide ONE canonical user-visible source without double logging. Do not throw away working domain undo/history semantics if they can be reused safely.

Expose bounded/paged read APIs directly suitable for the final UI; never eager-load the full journal.

# B. Safe compensating undo
Undo creates a new authoritative domain mutation + linked audit event; it never deletes/rewrites history.

For meaningful reversible operations:
- verify current semantic state against the original after-state/version/hash before inversion;
- fail closed on stale/conflicting/FK/dependency conditions;
- use authoritative module commands, not generic raw-row replay when domain invariants exist;
- grouped undo validates all members first and is all-or-nothing where possible;
- double/retry undo is idempotent;
- lifecycle/system/non-reversible events remain immutable;
- expose concise current rejection reason/status for UI;
- one undo action must not recurse into duplicate audit/export storms.

Representative tests must cover INSERT/UPDATE/DELETE/settings undo, stale update, dependency conflict, grouped all-or-nothing, double undo and non-reversible events.

# C. Registro attività UI over SAME model
Add a compact PersonalHub home destination `Registro attività`; tapping opens a full screen, no preview list required on home.

History must be lazy/paged with no arbitrary historical cap. Each row shows readable time, module/category, human semantic description, group expansion/detail, current reverted/conflict/non-reversible status and `↩︎` undo only when currently allowed. Do not expose raw snapshot JSON/IDs as normal UI.

Add compact `🎛️` multi-select filters with Apply/Reset, at minimum: Tutti, People, Timer, Places, Substances, WordPulse, Soldi, Impostazioni, Sistema. Persist display filter across restarts; unknown/future categories remain visible by default. Preserve relevant scroll/filter/expanded state across recreation using existing PH patterns.

# Export/sync invariants
Audit rows associated with a domain mutation should participate in the same semantic transaction/generation where practical. No recursive logging, idle loops, duplicate Timer/Places journal entries or export storms. Do not redesign Datasette/SAF.

# Verification
Use representative coverage rather than exhaustive module-by-module repetition:
- one coherent semantic event/group from each mutable module/settings path;
- readable deleted identity; secret redaction;
- Timer/Places do not double-log;
- safe inverse cases/conflicts above;
- paged UI, grouping, filter persistence/new-category visibility, reversible/non-reversible state;
- focused device flow: home → register → filter → expand group → one disposable reversible action → compensating history.

After targeted checks, run the minimum end-to-end regression set, ONE final APK build and ONE final safe device/emulator QA. Use disposable data only. Follow current remote PersonalHub bootstrap for Pixel install, Telegram APK delivery and clone cleanup if applicable.

# Non-goals / stop
No event-sourcing rewrite, generic rollback engine, raw-row replay framework, analytics, theme overhaul, module business redesign, Datasette/SAF redesign. PASS only when one canonical model powers capture + safe undo + register UI without duplicate/recursive audit. Stop immediately.

Final output only: `PROMPT_ID`, `RESULT`, audit schema/migration/coverage, Timer/Places bridge, grouping/redaction, undo/conflict semantics, paging/filter UI, no-recursion/export checks, tests/device QA, version, APK delivery, commit/push, blocker if any.
