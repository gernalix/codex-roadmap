PROMPT_ID=734140
PROJECT=livinggaul-x-downloader
MODEL=GPT-5.6 Luna
REASONING=low
MegaVault=FAST

GOAL
Activate livinggaul-x-downloader v0.4.2 on the real Fedora host and verify the real SQLite video_catalog view exposes the derived duplicate_count for each canonical downloaded video. Remote implementation and CI are already PASS at commit 7b3b263ce9aa52359c46106a6beeba58851e7700.

STARTING POINT
- Repo: ~/projects/livinggaul-x-downloader
- Installed CLI: ~/.local/bin/livinggaul-x-downloader
- DB: ~/.local/state/livinggaul-x-downloader/download_history.sqlite
- Required commit or descendant: 7b3b263ce9aa52359c46106a6beeba58851e7700
- Existing hourly systemd service/timer must remain enabled and unchanged.

SCOPE
Do only checkout/install/view-refresh/verification. Do not download X videos, rerun broad audits, change systemd units, or modify unrelated code.

EXECUTION
1. Claim this prompt with roadmap_start.py and continue only if state becomes running.
2. Safely update only this repo checkout to current master.
3. Install/update the CLI at ~/.local/bin/livinggaul-x-downloader; require executable and version 0.4.2.
4. Run installed CLI --status once to recreate the idempotent views.
5. Verify real DB still has PRAGMA user_version=4 and video_catalog includes duplicate_count.
6. Verify the column is derived from persistent history by checking the view definition references skipped_duplicate and duplicate_of_id.
7. Run a bounded temporary-DB smoke using installed production functions:
   - create one downloaded canonical row;
   - create two skipped_duplicate rows linked to it through duplicate_of_id;
   - require video_catalog.duplicate_count for the canonical row = 2;
   - require duplicate rows themselves report 0;
   - delete the temporary DB.
8. Run a read-only real DB query:
   SELECT id, final_filename, duplicate_count
   FROM video_catalog
   WHERE status='downloaded'
   ORDER BY duplicate_count DESC, id;
   Empty result is acceptable if the DB still has no downloaded rows.
9. Verify livinggaul-x-source-availability.timer remains enabled+active and its installed units are unchanged.
10. If an in-scope defect blocks acceptance, make the smallest fix, run targeted tests, push, reinstall, and repeat the failed gate.

ACCEPTANCE CRITERIA
- Installed CLI version 0.4.2.
- Checkout contains 7b3b263 or descendant.
- DB remains schema v4.
- video_catalog exposes duplicate_count derived from skipped_duplicate rows linked by duplicate_of_id.
- Temporary smoke returns canonical duplicate_count=2 and duplicate rows=0.
- Real DB query executes successfully.
- Existing hourly timer remains enabled+active and unchanged.
- Final report first line exactly PROMPT_ID=734140, then RESULT, installed version/checkout, schema/view result, smoke result, real query row count, timer state, and any fix commit.
- Finalize PASS only after all mandatory criteria pass; otherwise BLOCKED/FAIL with concrete blocker. Stop immediately after finalization.
