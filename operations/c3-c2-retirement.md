> FROZEN C3 ARCHIVE (2026-10-05). Historical reference only. Do not execute these operating instructions. Current task flow: /home/daniele/MegaVault/ai/META_INFRASTRUCTURE.md.

# C3 control-plane retirement

This is a host action after the reviewed branch is merged. Do not run it in a
Symphony task workspace. The C3 services use the canonical roadmap snapshot and
single writer; they do not write `roadmap.sqlite` directly.

1. Install the merged code into the guarded supervisor runtime worktree and
   verify its source matches main. Run `python3 tools/c3_control_install.py` to
   stage the C3 units without starting them.
2. Verify the pinned Symphony artifact SHA-256, the explicit production tracker,
   and the exact canary run/tracker identity. Test
   `python3 tools/c3_symphony_backend.py status` and `stop`, then restart
   `c3-symphony.service` and confirm a healthy status for retirement preflight.
3. Ensure canonical roadmap runs are quiescent. Run
   `python3 tools/c3_retirement.py --execute` from the merged runtime tree. It
   refreshes the writer-backed snapshot, requires a healthy production Symphony
   backend and staged C3 units, and checks that ChatGPT/RDC remains installed.
4. Read `~/.local/state/c3-control/c2-retired.json` and
   `c2-retirement-audit.json`. Check that every listed C2 unit is inactive and
   masked, all C3 timers/path are enabled, C3 runtime and Inbox services have
   successful executions, no `c2-run-*.service` is active, and the backend
   remains healthy. Rerunning the retirement command checks masks and starts
   C3 units again if an activation was interrupted.

The C3 runtime retains dependency-aware scheduling/publication, fenced
single-writer operations, and repository integration readback. It routes coding
only to healthy production Symphony; a legacy Codex executor is never selected
or launched. Its worker still supports ChatGPT/RDC and native non-coding lanes.
The C3 Inbox timer ensures a bounded semantic triage item (up to 25 pending
observations per batch) through the writer, then ChatGPT/RDC handles its
dispositions. `chatgpt-rdc-supervisor.service` remains installed for this
lane; the retired C2 supervisor recovery daemons do not manage it.

The retirement marker blocks legacy installers and direct C2 runtime starts.
Historical C2 unit files are archived outside the repo with hashes in the
audit manifest. Canonical roadmap data, Inbox provenance, worktrees, Git history,
and repository integration history are preserved. Returning to C2 after the
marker requires a separate manual unretire procedure; normal runtime has no
automatic C2 fallback.
