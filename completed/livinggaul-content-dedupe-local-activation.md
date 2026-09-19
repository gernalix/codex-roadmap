PROMPT_ID=240438
PROJECT=livinggaul-x-downloader
MODEL=GPT-5.5
REASONING=low
MegaVault=FAST

GOAL
Activate and validate the new cross-post video-content deduplication on the real Fedora host state. Remote code is already implemented on master at commit b0cf9bdecf2e5174fec9a529ea0bc7d07863c860; do not redesign or refactor it unless a local/runtime defect blocks the goal.

STARTING POINT
- Repo: ~/projects/livinggaul-x-downloader (if the checkout path differs, locate only this repo; do not scan unrelated repos).
- Remote: https://github.com/gernalix/livinggaul-x-downloader
- Installed CLI: ~/.local/bin/livinggaul-x-downloader
- Existing state: ~/.local/state/livinggaul-x-downloader/download_history.sqlite
- Existing videos: ~/Videos/LivingGaul_X
- Required remote commit or newer: b0cf9bdecf2e5174fec9a529ea0bc7d07863c860

EXECUTION
1. Run the canonical roadmap start command for PROMPT_ID 240438 and continue only if it becomes running.
2. Bring only this repo checkout to current master safely. Preserve unrelated local work; if local changes conflict, reconcile them instead of discarding them.
3. Run the repo's targeted tests only if needed locally; GitHub CI for b0cf9bd already passed.
4. Install/update the repo script to ~/.local/bin/livinggaul-x-downloader with executable permissions.
5. Verify `livinggaul-x-downloader --status` reports version 0.2.0.
6. Run `livinggaul-x-downloader --reindex-content` against the existing real DB/videos. Missing historical files may be reported but are not a failure; any actual reindex exception must be fixed in-scope and rerun.
7. Verify existing present downloads are indexed: when downloaded>0, content_fingerprint_indexed must be >0. Inspect a small bounded DB sample to confirm the new columns are populated for present files.
8. Exercise the perceptual path with a bounded temporary local test using ffmpeg: generate one short synthetic video and a separately re-encoded copy, compute both fingerprints through the production code, and require fingerprints_match(...) == True. Clean up temporary files.
9. Run a final `--status` and ensure normal CLI operation is intact.

ACCEPTANCE CRITERIA
- Local checkout contains b0cf9bd or a descendant.
- Installed CLI is version 0.2.0 and executable.
- Reindex completes with reindex failed: 0.
- If at least one downloaded file exists, at least one content fingerprint is indexed.
- The local ffmpeg re-encode test proves the production perceptual matcher recognizes the same video after re-encoding.
- No unrelated repo changes, refactors, or cleanup.
- Final report first line is exactly `PROMPT_ID=240438`, followed by concise RESULT, installed version, reindex counts, fingerprint test result, and any non-blocking missing-file count.
- Finalize the roadmap prompt with PASS only after all mandatory criteria pass; otherwise use BLOCKED/FAIL with the concrete external blocker. Stop immediately after finalization.
