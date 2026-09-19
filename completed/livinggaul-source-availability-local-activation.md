PROMPT_ID=560584
PROJECT=livinggaul-x-downloader
MODEL=GPT-5.6 Terra
REASONING=medium
MegaVault=STRICT

GOAL
Activate livinggaul-x-downloader v0.4.0 on the real Fedora host, safely migrate/refresh the local SQLite DB to schema v4, verify both SQL views, and perform a real no-download availability probe of every already-downloaded video's original X link. Remote implementation is complete and CI PASS at commit 13d490d7c9a20e25f66ec79a8b86c9587b733277.

STARTING POINT
- Repo: ~/projects/livinggaul-x-downloader
- Installed CLI: ~/.local/bin/livinggaul-x-downloader
- DB: ~/.local/state/livinggaul-x-downloader/download_history.sqlite
- Videos: ~/Videos/LivingGaul_X
- Required commit or descendant: 13d490d7c9a20e25f66ec79a8b86c9587b733277
- Prior pending task 316628 is superseded by this task; do not run it separately.
- Current local DB may already have earlier schema/view migrations; trust current state.

SCOPE
Do only local activation/migration/verification and the explicit source-availability probe. Do not download new X videos, refresh social counters beyond the existing static snapshots, scan unrelated repos, or refactor unrelated code.

EXECUTION
1. Claim this prompt with the canonical roadmap_start.py command and continue only if state becomes running.
2. Bring only this repo checkout to current master safely, preserving unrelated local work.
3. If the DB exists, create one consistent timestamped SQLite backup before the first schema/view-changing invocation using the SQLite backup API/CLI, not a raw copy of a live WAL DB.
4. Install/update the repo script at ~/.local/bin/livinggaul-x-downloader and keep it executable.
5. Run installed CLI --status to apply the idempotent schema/view refresh.
6. Verify installed version is 0.4.0 and real DB has PRAGMA user_version=4.
7. Verify real DB:
   - downloads has source_availability, source_checked_at, source_check_error;
   - video_catalog exists and exposes the readable fields including size_mb/size_mib/download_date plus source availability fields;
   - source_unavailable_percentage exists and returns exactly one row with exactly one column named unavailable_percentage;
   - if there are zero downloaded rows, that value is NULL.
8. Run installed CLI --reindex-content; require failed=0. Missing historical files are non-blocking.
9. Run a bounded temporary-DB smoke test with installed production functions:
   - insert 4 downloaded rows with source_availability values available, unavailable, unknown, available;
   - require SELECT unavailable_percentage FROM source_unavailable_percentage to return 25.0;
   - require the view cursor to expose exactly one column;
   - delete temporary DB afterward.
10. Run the real network probe:
    livinggaul-x-downloader --check-source-availability --cookies-mode auto
    This command must not download media. Let production logic classify success as available, recognized permanent/deleted/404 cases as unavailable, and transient/auth/rate-limit failures as unknown.
11. After the probe, verify on the real DB:
    - every downloaded row that was processed has a non-null source_checked_at and source_availability in available/unavailable/unknown;
    - source_unavailable_percentage equals ROUND(100.0 * unavailable_downloaded / total_downloaded, 2), or NULL when total_downloaded=0;
    - capture counts of total/available/unavailable/unknown and the resulting percentage.
12. Run final --status. Do not run --run.
13. If an in-scope migration/view/runtime defect blocks acceptance, make the smallest necessary fix in this repo, run targeted tests, push, reinstall, and repeat the failed gate. Do not broaden scope.

ACCEPTANCE CRITERIA
- Installed CLI version 0.4.0 and executable.
- Checkout contains 13d490d or descendant.
- Consistent DB backup created if DB existed.
- Real DB schema v4 and both views present.
- source_unavailable_percentage is exactly one row/one column and formula is correct.
- --reindex-content failed=0.
- Temporary DB smoke returns exactly 25.0 for 1 unavailable out of 4 downloaded rows.
- Real --check-source-availability completes without downloading media and persists current availability results.
- Unknown results are reported but must never be coerced to unavailable.
- Final report first line exactly PROMPT_ID=560584, then concise RESULT, installed version/checkout, backup path or DB_NOT_PRESENT, schema/view result, reindex counts, real availability counts, unavailable percentage, unknown count, and any fix commit.
- Finalize PASS only after all mandatory criteria pass; otherwise BLOCKED/FAIL with concrete blocker. Stop immediately after finalization.
