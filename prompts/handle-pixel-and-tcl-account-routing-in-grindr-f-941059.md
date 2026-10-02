PROMPT_ID=941059

Resolve work item wi:73bd99da6da94ce9857ace787929977b in gernalix/grindr-favorites-monitor.

C2 launch contract: this task is dispatched by the canonical C2 worker after writer-owned claim/executor_started verification. Do NOT call roadmap_start.py or c2_executor_start.py again; do not create another work item or prompt.

Goal: the monitor is coupled to one dedicated Grindr Web session/account. When the requested profile belongs to the TCL account but the monitored browser is authenticated as Pixel, Favorites scanning can target the wrong account or cannot import the profile. Make account/session routing explicit and safe.

Scope:
- Inspect existing session/profile/account identification and monitor configuration first; preserve current working single-account behavior.
- Design the minimum deterministic account identity/routing mechanism needed to distinguish Pixel vs TCL monitor sessions and prevent scraping under the wrong authenticated account.
- Prefer explicit configured/account-observed identity with fail-closed mismatch over heuristic switching.
- Add focused tests for correct-account route and wrong/unknown-account fail-closed behavior.
- Do not automate credential extraction/login or broaden into unrelated Grindr scraping changes.
- Commit and push useful verified work; capture unrelated material findings to C2 Inbox.

Acceptance:
1. Monitor can represent/identify the active Grindr account/session explicitly.
2. A requested profile/account is never scraped through a mismatched session.
3. Pixel and TCL routing is deterministic and test-covered.
4. Existing single-account behavior remains compatible where account is configured correctly.
5. Verified changes are committed and pushed.