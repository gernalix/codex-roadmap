[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=583921 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Add a top-level PersonalHub Home **Cerca** function that reconstructs an on-demand temporal context: given `from` and `to` datetimes, show in one read-only chronological screen every relevant entry from every PH module whose timestamp/interval intersects the selected range. This is an ephemeral view, not a second Hub Context graph and not an automatic persistent relationship system.

Capture the PersonalHub base version once; `target = base + 1` exactly once.

# Reuse / scope
Reuse existing module adapters/query/navigation infrastructure and the canonical time semantics already present in Timer, People, Places, Substances, Soldi, WordPulse and other registered modules. If the top-level Composer/Hub Context refactor is already present, reuse its adapters/contracts where useful; do not couple Search to Composer state or require a saved Context.

Start from Home navigation + the existing Hub Context adapter registry/query contracts. Then inspect only the directly relevant timestamped DAO/query/model for a module when its adapter cannot answer interval queries. No repo-wide/module-wide scans, no unrelated refactor, no new graph architecture.

# UX
- Home exposes a clear `Cerca` entry.
- Screen has `Da` and `A` date+time selectors and a module filter; default is all available modules.
- Results from all selected modules are merged into one chronological timeline with module identity/icon, human-readable title/details and occurrence time/range.
- No raw IDs/internal entity names.
- Empty state is explicit.
- Changing range/filter refreshes results without creating/modifying domain data or Hub Context relationships.
- Keep large ranges usable: bounded/paged queries/merge as needed; do not load whole module tables and filter in UI memory.

# Time semantics
Use one consistent half-open query interval `[from,to)`:
- point event: `from <= t < to`;
- interval/session/visit: `start < to && (end == null || end > from)`.
Running/open intervals therefore appear when they overlap the requested time. Sort deterministically by occurrence start/time, with a stable tie-break.

Every module with a meaningful timestamp/range must be included through the smallest reusable temporal-entry contract. A module with no temporal entries must not invent fake events. Preserve canonical source records; Search is read-only.

# Architecture constraints
Prefer a small shared temporal result/query contract (module, source identity, start, optional end, title/subtitle/icon metadata) implemented by adapters/providers over module-specific UI branching. Do not duplicate domain records into a new search table merely for this feature. Add schema/index changes only if a focused query/performance check proves they are necessary.

# Verification
Focused tests only:
- point event boundaries at `from`/`to`;
- overlapping interval before/inside/after range and open interval;
- merge ordering/tie-break across at least 3 modules;
- module filtering;
- read-only behavior (no Context/domain writes);
- one live Android search using a range containing entries from multiple modules, plus empty-state check.

Follow current remote PersonalHub bootstrap for final tested APK, Pixel install, Telegram APK delivery and clone cleanup if applicable.

# Stop
PASS only when Home → Cerca can select a datetime interval and show a single correct chronological view across all temporal modules, without persisting inferred relationships or doing whole-table UI filtering. Stop immediately after focused PASS; no unrelated audit/cleanup.

Final output only: `PROMPT_ID`, `RESULT`, Home/Search UX, temporal contract/modules covered, overlap semantics, performance approach, tests/device check, version, APK delivery, commit/push, blocker if any.
