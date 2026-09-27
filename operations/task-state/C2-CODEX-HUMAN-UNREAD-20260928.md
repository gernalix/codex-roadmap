# TASK_ID C2-CODEX-HUMAN-UNREAD-20260928

Objective: add focus-aware unread messages to `c2-codex-human`.

Constraints:
- Reuse the existing read-only Codex session viewer; never create another Codex session.
- New messages after focus-out are unread.
- Focus-in must not clear unread immediately; require continuous focus dwell, default 20 seconds.
- Focus-out before dwell completion preserves unread state and includes subsequent messages.
- Dwell threshold must be CLI-configurable.
- Provide a manual mark-all-read shortcut.
- Preserve filtering, Codex-like colors and word-safe wrapping.

Checklist:
- [x] Canonical C2 item `wi:9f00e562bd584d1ab1d486ac02bbbf85` created through writer Issue #3248; duplicate `wi:1fb27dfe25434839aaeb2ce1a278f764` queued for CANCELLED via #3257; executor_started queued via #3259. Earlier local-only item/claim #3232 is invalid and must not be used.
- [x] Choose terminal-native focus reporting (DEC mode 1004) rather than GNOME window polling.
- [x] Implement unread state machine and focus input parser.
- [x] Implement visual unread treatment and redraw after clear.
- [x] Add `--read-after` and manual shortcut (`r`; `q` exits).
- [x] Add focused tests: 12/12 PASS; real rollout timestamps verified against wall clock.
- [x] Fix relative-time labels to age live on screen instead of freezing at `adesso`; unread countdown also refreshes.
- [ ] Commit and push final checkpoint.

Acceptance: focus-out/new-message/focus-in/dwell/focus-out-before-dwell/manual-clear/configuration all behave as requested.
Current step: implementation and canonical lifecycle repair verified.
Next action: commit and push final code/checkpoint, restart the live viewer, then submit canonical PASS when executor_started is applied.

Update 2026-09-28: removed refresh flash by switching recurring redraws from clear-then-paint to synchronized VTE/Ptyxis frame updates (HOME + frame + erase-down inside DEC synchronized-output mode). Initial draw still clears once. Added local single-instance launcher state so a new viewer terminates the previous viewer and its owning wrapper shell when identifiable. Future launches must omit `; exec bash` so terminated viewers close their Ptyxis tab instead of leaving a Signal 15 tombstone. Focused suite: 14/14 PASS.
