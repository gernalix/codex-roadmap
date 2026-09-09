[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=640217 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Add Home → **Random timer** to measure perceived passage of time. The user starts one hidden-duration timer; PH later asks how many minutes they think passed, reveals the real elapsed time only after the answer, computes `perceived_minutes / actual_minutes`, and persists the attempt.

Capture the PersonalHub base version once; `target = base + 1` exactly once.

# Scope / starting point
Start from Home navigation/cards, current app settings storage, and the existing Timer/notification scheduling/deep-link path. Reuse existing notification/scheduler infrastructure where appropriate. Inspect only the directly relevant persistence layer needed for Random timer attempts. No Timer redesign, no general notification refactor, no unrelated settings cleanup.

# Required UX and behavior
- Home exposes `Random timer` with an obvious Start control using an emoji-style icon plus accessible text.
- Only one Random timer may be active at once; prevent ambiguous concurrent hidden timers.
- Setting: maximum random duration in minutes, default `60`, persisted. It must be >0.
- On Start, choose a random hidden target with `0 < target <= configured max`; do not show target/remaining/elapsed/ETA anywhere in user-visible UI before the user submits their estimate.
- Persist enough active-run state that process death does not silently lose the run; reuse existing reboot/reschedule handling if available rather than inventing a parallel scheduler.
- When the hidden timer fires, show an Android notification asking exactly `Quanto tempo è passato?` (localized normally if the app supports IT/EN). The notification must still not reveal the answer.
- Tapping it opens Random timer directly with the numeric minutes field focused and numeric keyboard requested immediately.
- User enters perceived minutes and presses Enter/IME Done.
- Only after valid submission reveal: actual elapsed minutes and `perceived / actual` ratio. Do not reveal either beforehand.
- Persist at minimum actual elapsed minutes and perceived minutes for every completed attempt; also persist stable identifiers/timestamps needed to reconstruct/audit the attempt.

# Measurement correctness
The comparison denominator is the real elapsed time from Start until the alert actually becomes due/delivered according to the scheduler, not merely a displayed planned duration. Keep internal timing precision higher than the displayed minutes so scheduling delay/rounding does not corrupt the ratio. Because division by zero is invalid, never generate a zero-duration run.

Do not auto-submit on notification tap, do not expose the hidden value through Home state, notification text, accessibility text or another user-visible screen before submission.

# Verification
Focused tests only:
- configured max default/persistence and random target always `>0 && <=max`;
- hidden value is absent from all pre-answer UI state;
- one-active-run rule;
- notification content/deep link;
- notification tap focuses numeric input and submission via Enter/Done;
- ratio uses persisted real elapsed time and handles rounding safely;
- completed attempt stores real + perceived minutes;
- process recreation during active run does not reveal/lose it.

One concise Pixel smoke: start a short test run via test-injected/controlled duration, receive notification, open it, enter estimate, verify reveal + persistence. Do not wait a real long random duration in QA.

Follow current remote PersonalHub bootstrap for final tested APK, Pixel install, Telegram APK delivery and clone cleanup if applicable.

# Stop
PASS only when the hidden duration stays hidden until estimate submission, the notification/deep link flow works, ratio is correct/nonzero and completed values persist. Stop immediately; no unrelated audit/cleanup.

Final output only: `PROMPT_ID`, `RESULT`, Home/setting, hidden-run semantics, notification/deep link/input, reveal/ratio, persistence, tests/Pixel smoke, version, APK delivery, commit/push, blocker if any.
