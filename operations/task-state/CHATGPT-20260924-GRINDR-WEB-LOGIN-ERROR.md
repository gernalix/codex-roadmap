# TASK_ID: CHATGPT-20260924-GRINDR-WEB-LOGIN-ERROR

## Objective
Identify why Grindr Web shows “Something went wrong / Check your internet connection and try again” immediately after login in both Chrome and Firefox, including incognito/private mode, and apply the minimum safe fix on Fedora.

## Constraints
- Use Remote Desktop Commander for Fedora/browser/runtime work.
- Preserve browser profiles, credentials, cookies and unrelated settings unless a verified fix requires a targeted change.
- Do not disable security controls broadly; prefer reversible, scoped changes.
- Avoid destructive resets until network/browser evidence identifies the failing layer.
- Persist meaningful checkpoints with commit + push.
- Do not persist authentication values, cookie contents, chat contents, or other private Grindr data in roadmap state.

## Plan / checklist
- [x] Sync codex-roadmap and read task-state protocol.
- [x] Capture Fedora network/VPN/proxy/DNS/time state.
- [x] Reproduce public Grindr Web connectivity outside the browser and inspect HTTP/TLS/DNS behavior.
- [x] Inspect current Grindr Web bundle and identify what the visible error actually represents.
- [x] Verify the core Grindr Web websocket path from Fedora.
- [x] Verify Chrome location permission for Grindr and inspect popup behavior in current Grindr bundle.
- [x] Build an isolated diagnostic Chrome profile from the existing normal profile without modifying the real profile.
- [x] Verify an existing authenticated session can fully load Grindr Web, connect its websocket, and render chats in a visible isolated Chrome process.
- [ ] Capture the exact exception/status from a fresh-login failure path, if still reproducible.
- [ ] Apply the minimum targeted fix/workaround to the real browser flow.
- [ ] Verify the real normal browser succeeds after login/reload; retest private/incognito only if still relevant.
- [ ] Record final evidence and cleanup temporary diagnostic runtime/profile.

## Current step
Use the successful session-cookie reauthentication path as a non-destructive workaround candidate, then verify whether the real post-login failure persists on a reload/new navigation.

## Verified facts
- User reports the same generic failure immediately after login in Chrome, Firefox, and private/incognito mode.
- The screenshot text is Grindr Web's global React error-boundary fallback. The “check your internet connection” wording is generic and does not establish a network failure.
- Fedora clock/NTP are correct. GNOME proxy is disabled. No proxy environment variables or Grindr hosts overrides exist.
- Wi-Fi is the default route. Tailscale is not the default route. ExpressVPN daemon exists but no ExpressVPN tunnel/default route was active during diagnosis.
- `https://web.grindr.com/` and `/chat` return HTTP 200 with valid TLS from Fedora.
- The current Grindr bundle uses `wss://grindr.mobi/v1/ws` for chat transport. A browser-like websocket handshake from Fedora returned HTTP 101 Switching Protocols.
- `chat.grindr.com` has a public CNAME whose AWS target currently returns NXDOMAIN across router, Cloudflare, Google and Quad9 DNS; current Grindr code uses `chat.grindr.com` as the XMPP/JID domain string, so this DNS fact is not evidence of the observed failure.
- Chrome explicitly allows geolocation for `https://web.grindr.com`.
- The current Grindr bundle has a dedicated popup-blocked login dialog, different from the screenshot's generic error boundary.
- An isolated headless clone of the normal Chrome profile authenticated through the existing Grindr web session and loaded `/chat`; its websocket was blocked/closed under headless mode.
- Relaunching the same isolated clone as a normal visible Wayland Chrome established the Grindr websocket, received data, and fully rendered the authenticated chat UI without the generic error.
- Therefore the account, current session, Fedora network path, TLS, core websocket path, profile data, and normal Chrome renderer are capable of working. The failure is concentrated in the fresh-login/first-post-login path or was transient and has since cleared.
- The normal-profile Grindr session cookie created before diagnosis was sufficient for the successful later session-cookie reauthentication in the isolated clone. This makes a simple reload/new navigation after the failed first post-login render a high-value workaround candidate.

## Decisions
- Do not change DNS, firewall, VPN, geolocation, browser installation, or wipe browser profiles; evidence does not support those as causes.
- Do not clear the user's real Grindr site data yet, because the existing authenticated session is valid and successfully reauthenticates.
- Do not treat the public `chat.grindr.com` DNS result as the root cause unless a real network request to that hostname is later observed.
- Prefer a reload/new navigation using the already-valid session before any destructive reset.
- A temporary diagnostic browser may be used only locally and must be removed at completion.

## Completed
- Persistent task state initialized and pushed.
- Shared system/network causes tested and largely ruled out.
- Generic error identified as app-level React exception fallback.
- Core WebSocket path verified.
- Existing authenticated account/session successfully loaded end-to-end in an isolated visible Chrome diagnostic process.

## Remaining
- Determine whether a new navigation/reload in the real normal Chrome session now succeeds.
- If it still fails, capture the exact fresh-login exception via a dedicated debug browser session; user credentials must remain user-entered and must not be logged.
- Apply only the smallest fix supported by that evidence.
- Verify and clean up the temporary diagnostic profile/process.

## Blockers
None. Exact fresh-login exception has not yet been captured because the isolated existing-session path now works.

## Evidence
- Initial screenshot supplied in ChatGPT.
- HTTP/TLS/network baseline and browser-like websocket handshake captured through Remote Desktop Commander.
- Current production bundle inspected locally from `web.grindr.com`.
- Isolated visible Chrome diagnostic process logged `WebSocket connection established` and rendered the authenticated chat UI.
- No authentication values or chat contents are stored in this state file.

## Acceptance criteria
- Root cause narrowed to a specific failing layer with reproducible evidence.
- Safe fix/workaround applied when local remediation is possible.
- Grindr Web no longer shows the generic post-login error in the user's normal browser, or a verified external/account-side blocker is documented.
- Temporary diagnostic process/profile removed.

## Next action
Verify the user's real normal Chrome session by navigating/reloading `https://web.grindr.com/chat` with the already-valid session. If it still shows the generic error, reproduce one fresh login in a dedicated visible debug browser with logging enabled and capture only exception/status metadata after login.
