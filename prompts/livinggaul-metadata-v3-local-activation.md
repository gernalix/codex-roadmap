PROMPT_ID=996524
PROJECT=livinggaul-x-downloader
MODEL=GPT-5.6 Terra
REASONING=medium
MegaVault=STRICT

GOAL
Activate livinggaul-x-downloader v0.3.0 on the real Fedora host, migrate the existing local SQLite state safely to schema v3, and verify the installed metadata-catalog behavior. Remote implementation is already complete and CI PASS at commit 20fb722b98b81590e70d12b22844796ed6aec08e.

STARTING POINT
- Repo: ~/projects/livinggaul-x-downloader
- Installed CLI: ~/.local/bin/livinggaul-x-downloader
- DB: ~/.local/state/livinggaul-x-downloader/download_history.sqlite
- Videos: ~/Videos/LivingGaul_X
- Required commit or descendant: 20fb722b98b81590e70d12b22844796ed6aec08e
- Previous local check reported downloaded=0, but trust current state over this historical observation.

SCOPE
Do only the local activation/migration/verification required below. Do not redesign the feature, scan unrelated repos, refresh social counters, or download new X videos.

EXECUTION
1. Claim this prompt with the canonical roadmap_start.py command and continue only if state becomes running.
2. Bring only this repo checkout to current master safely, preserving any unrelated local work.
3. Before the first schema-changing invocation, if the DB exists, create one consistent timestamped SQLite backup using the SQLite backup API/CLI (not a raw copy of a live WAL database). Record its path.
4. Install/update the repository script at ~/.local/bin/livinggaul-x-downloader and keep it executable.
5. Run the installed CLI --status to trigger the idempotent migration.
6. Verify on the real DB:
   - PRAGMA user_version = 3;
   - metadata_snapshots exists;
   - all v3 columns exist in downloads: uploader,uploader_id,tweet_text,title,upload_timestamp,downloaded_at,view_count,like_count,repost_count,comment_count,width,height,fps_num,fps_den,video_codec,audio_codec,video_bitrate,audio_bitrate,container_format,pixel_format,audio_sample_rate,audio_channels plus the existing dedupe columns;
   - expected v3 indexes exist.
7. Run installed CLI --reindex-content. Require failed=0. Missing historical files may be reported but are non-blocking.
8. Run a bounded deterministic smoke test against a temporary DB using the installed production module/functions: insert sample yt-dlp metadata plus sample final-file metadata through upsert_status; verify normalized fields persist, social counters remain the first static snapshot after a second upsert with changed counts, metadata_snapshots contains exactly one valid JSON snapshot, and schema version remains 3. Delete the temporary DB afterward.
9. Run final installed CLI --status. Do not perform --run and do not download anything from X.
10. If a defect in the in-scope migration/runtime code blocks these criteria, fix the smallest necessary code in this repo, run targeted tests, push the fix, reinstall, and repeat the failed gate. No unrelated cleanup/refactor.

ACCEPTANCE CRITERIA
- Installed CLI reports version 0.3.0 and is executable.
- Local checkout contains 20fb722 or a descendant.
- Existing DB was backed up consistently before migration when it existed.
- Real DB is schema v3 with all required columns/table/indexes.
- --reindex-content finishes with failed=0.
- Temporary installed-code smoke proves normalized metadata + static social counters + one raw yt-dlp JSON snapshot.
- No new X video is downloaded.
- Final report first line exactly PROMPT_ID=996524, then concise RESULT, installed version/checkout, backup path or DB_NOT_PRESENT, schema result, reindex counts, metadata smoke result, and any fix commit.
- Finalize the roadmap prompt PASS only after all mandatory criteria pass; otherwise BLOCKED/FAIL with the concrete blocker. Stop immediately after finalization.
