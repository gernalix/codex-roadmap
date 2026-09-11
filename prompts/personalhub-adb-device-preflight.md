[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=308941 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Make PersonalHub Android target selection/preflight deterministic so Codex does not waste tool calls rediscovering whether Pixel, TCL, or the Pixel_8a AVD is available or repeatedly retrying ADB without new evidence.

# Starting point
Recent QA started with `adb devices` seeing no target, then an AVD had to be discovered/started, while the physical Pixel appeared later. Future tasks need a single bounded preflight that reports usable targets and selects the right one according to existing PersonalHub test rules.

# Scope
Implement the smallest reusable preflight command/script and minimal canonical documentation needed by future PersonalHub Codex sessions.

Required behavior:
- inspect ADB once and classify available physical devices/emulators clearly;
- identify the known Pixel 8a, TCL, and Pixel_8a AVD when resolvable from existing config/MegaVault rather than hard-coding unstable transport IDs;
- perform only safe, bounded recovery steps for offline/unavailable ADB state (for example server/reconnect actions when justified), with no unbounded polling;
- reuse an already-running eligible target when possible;
- start the existing Pixel_8a AVD only when emulator fallback is allowed and no suitable target is already available;
- distinguish "physical Pixel required but absent" from "emulator fallback allowed" instead of silently substituting one for the other;
- expose a concise machine/human-readable result that future prompts can consume without additional exploration.

Do NOT change app functionality, Android device settings unrelated to ADB, pair unknown devices automatically, or create new AVDs unless the existing one is genuinely missing and that blocks the stated goal. Do not add background daemons.

# Verification
Test the preflight against the targets currently available. Verify deterministic output and bounded behavior for at least the current available-device case and one fallback/absence case that can be simulated safely without disrupting the user's real device.

Do not bump PersonalHub version or build/deliver an APK for this infrastructure-only task.

# Acceptance / stop
PASS when future PersonalHub tasks can run one canonical preflight command and immediately know which Android target to use, whether emulator fallback is valid, or whether a real-device gate is blocked. Stop after targeted verification; do not audit unrelated Android tooling.

Final output concise: `PROMPT_ID`, `RESULT`, preflight command/path, selection rules implemented, verification evidence, files changed, blocker if any.