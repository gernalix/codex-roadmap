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
- [x] Attempt a fresh-login capture in a dedicated visible debug browser and determine whether the failure remains reproducible.
- [ ] Apply the minimum targeted fix/workaround to the real browser flow.
- [ ] Verify the real normal browser succeeds after login/reload; retest private/incognito only if still relevant.
- [ ] Record final evidence and cleanup temporary diagnostic runtime/profile.

## Current step
A real default-profile Chrome window has been navigated to `https://web.grindr.com/chat`. Obtain one visual confirmation of whether that window shows the normal Grindr interface or the original generic error before making any destructive or browser-restart change.

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
- A dedicated visible Chrome profile with DevTools Protocol logging was used for a fresh user-entered login. It reached `https://web.grindr.com/chat` successfully and the original generic error did not reproduce.
- During an instrumented reload, the Grindr websocket was created. The only observed aborted request was `/api/v3/me/location` during navigation; the same endpoint then returned HTTP 200.
- In the authenticated debug session, geolocation permission is granted and the recorded Grindr API resource set contained 42 API requests with zero HTTP >=400 responses.
- Closing and relaunching the dedicated debug Chrome preserved authentication and reopened `/chat`; the subsequent resource set again showed 42 API calls with zero HTTP >=400 responses.
- The exact fresh-login failure is therefore currently non-reproducible in the clean dedicated browser path.
- Remote Desktop Commander opened `https://web.grindr.com/chat` in the already-running real default-profile Chrome process; AT-SPI confirmed a Grindr Web top-level window in that default-profile Chrome application.
- The real default-profile Chrome process was not started with remote debugging, and this RDC integration exposes terminal/filesystem operations rather than browser pixels; it cannot safely inspect that already-running window's page body directly.
- Restarting the real Chrome solely to add remote debugging is not currently justified: the profile reports `restore_on_startup` unset and `exit_type="Crashed"`, so an autonomous restart could risk the user's open-window state.

## Decisions
- Do not change DNS, firewall, VPN, geolocation, browser installation, or wipe browser profiles; evidence does not support those as causes.
- Do not clear the user's real Grindr site data yet, because the existing authenticated session is valid and successfully reauthenticates.
- Do not treat the public `chat.grindr.com` DNS result as the root cause unless a real network request to that hostname is later observed.
- Prefer a reload/new navigation using the already-valid session before any destructive reset.
- A temporary diagnostic browser may be used only locally and must be removed at completion.
- Do not restart the user's real Chrome merely to enable CDP, and do not scrape/copy the full Grindr page contents to infer the error; prefer a minimal human visual confirmation.

## Completed
- Persistent task state initialized and pushed.
- Shared system/network causes tested and largely ruled out.
- Generic error identified as app-level React exception fallback.
- Core WebSocket path verified.
- Existing authenticated account/session successfully loaded end-to-end in an isolated visible Chrome diagnostic process.
- Fresh user-entered login in the dedicated visible debug browser succeeded without the generic error.
- Instrumented reload and full diagnostic-browser restart both succeeded with no Grindr API HTTP errors.
- Opened `/chat` in the actual default-profile Chrome process without changing its profile or settings.

## Remaining
- Get one visual confirmation of whether the newly opened real default-profile Chrome Grindr window succeeds or still shows the generic error.
- If it still fails in the real browser, choose the least disruptive way to instrument that specific profile before changing site data or browser settings.
- Apply only the smallest fix supported by that evidence.
- Verify and clean up the temporary diagnostic profile/process.

## Blockers
One user-visible confirmation is required for the already-open real default-profile Chrome window. RDC can verify that the window exists but cannot read its rendered page safely, and restarting the user's active Chrome just to add debugging would be unnecessarily disruptive.

## Evidence
- Initial screenshot supplied in ChatGPT.
- HTTP/TLS/network baseline and browser-like websocket handshake captured through Remote Desktop Commander.
- Current production bundle inspected locally from `web.grindr.com`.
- Isolated visible Chrome diagnostic process logged `WebSocket connection established` and rendered the authenticated chat UI.
- Dedicated fresh-login diagnostic reached `/chat`; instrumented resource inspection showed geolocation granted, 42 Grindr API requests and zero HTTP >=400 responses.
- Diagnostic-browser restart preserved the session and again loaded `/chat` with zero failing Grindr API responses.
- Real default-profile Chrome navigation was issued successfully; AT-SPI exposed a top-level `Grindr Web ... - Google Chrome` frame in the default-profile Chrome application.
- No authentication values or chat contents are stored in this state file.

## Acceptance criteria
- Root cause narrowed to a specific failing layer with reproducible evidence.
- Safe fix/workaround applied when local remediation is possible.
- Grindr Web no longer shows the generic post-login error in the user's normal browser, or a verified external/account-side blocker is documented.
- Temporary diagnostic process/profile removed.

## Next action
Ask the user whether the newly opened Grindr window in their normal Chrome shows the normal Grindr interface or the same `Something went wrong` error.
