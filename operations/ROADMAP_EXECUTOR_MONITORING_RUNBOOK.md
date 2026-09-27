# Roadmap Executor Monitoring Runbook

Purpose: monitor and steer the ChatGPT roadmap executor deterministically without rediscovering the browser-control path each time.

## Canonical target

- Chat URL: `https://chatgpt.com/c/6ab92890-6c94-83ed-83b8-86a8b7563734`
- Expected title seen on 2026-09-27: `Continue Issue 2330 Recovery`
- User service: `c2-roadmap-live-watch.service`
- Watcher script: `/home/daniele/.local/share/chatgpt-rdc-supervisor/bin/c2-roadmap-live-watch.py`
- Chrome bridge shim: `/home/daniele/.local/share/chatgpt-rdc-supervisor/bin/chrome_watch_bridge.py`
- Log: `/home/daniele/.local/state/chatgpt-rdc-supervisor/c2-roadmap-watch.log`
- Manual one-shot steer file: `/home/daniele/.local/state/chatgpt-rdc-supervisor/c2-roadmap-manual-steer.txt`

## Working monitoring path

1. Use Remote Desktop Commander only to run commands on Fedora.
2. Use the existing Chrome extension bridge from `chrome_watch_bridge.py`; do not start by inventing a new Playwright/Chrome setup.
3. The watcher connects with:
   - endpoint label `normal-chrome-extension`
   - target URL exact match
   - `getUserTabs` -> select the target tab
   - claim/attach that tab
   - read DOM through CDP `Runtime.evaluate`
4. Confirm success from the log. A healthy attachment produces entries such as:
   - `WATCH START`
   - `TARGET BOUND`
   - `HEARTBEAT`
   - optional `AI AUDIT`
5. Treat the watcher log as the first source of truth for whether monitoring is actually active.

## Restart/check commands

Run under the user session bus:

```bash
XDG_RUNTIME_DIR=/run/user/1000 \
DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
systemctl --user restart c2-roadmap-live-watch.service
```

Then inspect:

```bash
tail -n 80 /home/daniele/.local/state/chatgpt-rdc-supervisor/c2-roadmap-watch.log
```

Expected success: a fresh `WATCH START`, then `TARGET BOUND`, followed by heartbeats without repeating exceptions.

## Known failure: Debugger unattached

Observed 2026-09-27: the watcher remained logically attached after Chrome dropped the debugger and entered a loop of:

`RuntimeError('Debugger unattached')`

The bridge now retries by:
1. clearing its internal `_attached` flag;
2. re-claiming/re-attaching the same Chrome tab;
3. retrying the failed CDP command once.

If this error reappears repeatedly, do not redesign the whole watcher first. Verify this recovery path and whether Chrome changed the tab/debugger state.

## One-shot manual steer

When a chat is dead and a steer must be sent through the already-bound watcher:

1. Write the full steer text to:

`/home/daniele/.local/state/chatgpt-rdc-supervisor/c2-roadmap-manual-steer.txt`

2. Restart the watcher service if needed.
3. On the next loop the watcher:
   - stops an active generation if necessary;
   - sends the steer with the existing composer logic;
   - logs `MANUAL STEER SENT`;
   - deletes the one-shot file after confirmed send.

Always verify the send in the watcher log. Do not assume writing the file equals successful delivery.

## Dead/stalled generation rules

- If the visible banner says `Our systems are thinking a bit more about this request before responding.`, treat that generation as dead immediately.
- Stop it if necessary and send the configured recovery steer immediately.
- For ordinary inactivity, use watcher structural signals and visible-content age; do not declare death from a single unchanged sample.
- After every steer, verify that the composer cleared or a new user message/generation appeared.

## Preferred recovery order

1. Read the latest watcher log.
2. If the target is bound and healthy, use the existing watcher; do not switch control mechanisms.
3. If the target is missing, verify the exact URL is open in normal Chrome.
4. If `Debugger unattached` occurs, exercise the reattach recovery.
5. If `Chrome Runtime.evaluate failed` occurs, retry/rebind the target tab before attempting a new architecture.
6. Only if the extension bridge itself is unavailable should a different browser-control path be investigated.

## Operational rules

- Reuse this runbook before exploring alternative browser-control methods.
- Avoid opening extra ChatGPT tabs unnecessarily; bind to the existing exact target URL.
- Preserve PersonalHub workers/devices when recovering the roadmap supervisor.
- Any material bug, bottleneck, repeated failure mode, or fragile recovery discovered while monitoring should be captured in the C2 Inbox immediately, without pausing the main task unless it is a blocker.
- For Codex parallelization steers, maximize independent work only across non-conflicting repos/files and select the least costly sufficient model/reasoning level.

## Success criteria

Monitoring is considered restored only when all are true:

- target URL is bound;
- DOM reads succeed;
- no repeating watcher exception loop;
- heartbeats continue;
- a manual steer, when requested, is confirmed by `MANUAL STEER SENT` or equivalent delivery evidence.

Last verified: 2026-09-27.
