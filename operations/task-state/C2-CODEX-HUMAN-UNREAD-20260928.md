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
- [ ] Canonical C2 lifecycle identity is being reimported by the active Codex supervisor; the earlier local-only work item/claim #3232 was invalid and must not be used.
- [x] Choose terminal-native focus reporting (DEC mode 1004) rather than GNOME window polling.
- [x] Implement unread state machine and focus input parser.
- [x] Implement visual unread treatment and redraw after clear.
- [x] Add `--read-after` and manual shortcut (`r`; `q` exits).
- [x] Add focused tests: 12/12 PASS; real rollout timestamps verified against wall clock.
- [ ] Commit and push checkpoint.

Acceptance: focus-out/new-message/focus-in/dwell/focus-out-before-dwell/manual-clear/configuration all behave as requested.
Current step: implementation verified; canonical C2 lifecycle reimport remains external to this branch.
Next action: commit and push code/checkpoint; do not create any local roadmap lifecycle records.
