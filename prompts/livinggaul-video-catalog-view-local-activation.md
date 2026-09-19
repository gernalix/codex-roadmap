PROMPT_ID=316628
PROJECT=livinggaul-x-downloader
MODEL=GPT-5.6 Terra
REASONING=medium
MegaVault=STRICT

GOAL
Activate livinggaul-x-downloader v0.3.1 on the real Fedora host, safely migrate/refresh the local SQLite DB, and verify the new readable video_catalog view including daily MB aggregation. Remote implementation is complete and CI PASS at commit e79ed465017129bf2944b3edf0fea7f5ec16e050.

STARTING POINT
- Repo: ~/projects/livinggaul-x-downloader
- Installed CLI: ~/.local/bin/livinggaul-x-downloader
- DB: ~/.local/state/livinggaul-x-downloader/download_history.sqlite
- Videos: ~/Videos/LivingGaul_X
- Required commit or descendant: e79ed465017129bf2944b3edf0fea7f5ec16e050
- Previous local state may already be schema v3; trust current state.

SCOPE
Do only local activation/migration/verification. Do not download new X videos, refresh social counters, scan unrelated repos, or refactor unrelated code.

EXECUTION
1. Claim this prompt with roadmap_start.py and continue only if state becomes running.
2. Bring only this repo checkout to current master safely, preserving unrelated local work.
3. If the DB exists, create one consistent timestamped SQLite backup before the first schema/view-changing invocation using the SQLite backup API/CLI, not a raw live WAL copy.
4. Install/update the repo script to ~/.local/bin/livinggaul-x-downloader and keep it executable.
5. Run installed CLI --status to apply the idempotent schema/view refresh.
6. Verify installed version is 0.3.1 and real DB has PRAGMA user_version=3.
7. Verify view video_catalog exists and exposes at least:
   download_date,published_date,size_mb,size_mib,duration_seconds,duration_minutes,resolution,fps,video_bitrate_kbps,audio_bitrate_kbps,yt_dlp_metadata_json plus the underlying normalized metadata columns.
8. Run installed CLI --reindex-content; require failed=0. Missing historical files are non-blocking.
9. Run a bounded temporary-DB smoke test with installed production functions:
   - insert at least 3 downloaded rows spanning 2 download dates with known size_bytes;
   - query video_catalog grouped by download_date using SUM(size_mb);
   - require counts and totals to match the inserted values exactly within normal floating-point tolerance;
   - verify size_mb uses decimal MB and size_mib uses binary MiB;
   - delete temporary DB afterward.
10. Run a read-only example query against the real DB:
    SELECT download_date, COUNT(*) AS videos, ROUND(SUM(size_mb),2) AS downloaded_mb
    FROM video_catalog
    WHERE status='downloaded'
    GROUP BY download_date
    ORDER BY download_date;
    Empty result is acceptable if there are no downloaded rows.
11. Run final --status. Do not run --run and do not download anything from X.
12. If an in-scope migration/view/runtime defect blocks acceptance, make the smallest necessary fix in this repo, run targeted tests, push, reinstall, and repeat the failed gate.

ACCEPTANCE CRITERIA
- Installed CLI version 0.3.1 and executable.
- Checkout contains e79ed46 or descendant.
- Consistent DB backup created if DB existed.
- Real DB schema v3 and video_catalog view present with required derived columns.
- --reindex-content failed=0.
- Temporary DB GROUP BY download_date proves daily MB aggregation works.
- Real DB example query executes successfully, even if it returns zero rows.
- No new X video downloaded.
- Final report first line exactly PROMPT_ID=316628, then concise RESULT, installed version/checkout, backup path or DB_NOT_PRESENT, schema/view result, reindex counts, daily-MB smoke result, real query row count, and any fix commit.
- Finalize PASS only after all mandatory criteria pass; otherwise BLOCKED/FAIL with concrete blocker. Stop immediately after finalization.
