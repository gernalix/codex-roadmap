[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=731864 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Add configurable **Random alerts** to every user-configurable Events button in Timer and every configured action button in Substances. Each button owns its own enabled state and frequency; one global master switch can suspend/resume all Random alerts without overwriting any per-button configuration.

Capture the PersonalHub base version once; `target = base + 1` exactly once.

# Scope / starting point
Start from the existing Timer Quick Events target/config/options model + notification path and the configured Substances button model/options. Reuse current notification/deep-link/scheduler infrastructure and app settings. Use one targeted lookup per missing exact symbol/file; no Timer-wide/Substances-wide/repo-wide exploration.

Prefer one shared Random-alert scheduling/config contract used by both modules over duplicated engines. Do not redesign button execution, stock semantics, normal alerts or widgets.

# Per-button configuration
Every eligible Timer Event/Quick Event button and configured Substances button has an option `Random alerts` with:
- independent enabled/disabled state;
- frequency count `N` as a positive integer;
- unit: `per hour` or `per day`.

Interpret `N` per button, not as an aggregate across all buttons. Persist configuration by stable button identity so reorder/rename does not silently attach settings to the wrong button. Deleting a button cancels/removes its pending Random alerts safely.

# Global master switch
Add one app-level Random alerts ON/OFF switch:
- OFF suspends/cancels delivery for all buttons;
- it MUST NOT overwrite each button's own enabled flag, count or unit;
- ON restores the previously configured per-button states automatically.

Do not catch up missed alerts in a burst after a global/per-button disabled period. On re-enable, begin a fresh future schedule from that moment while preserving the stored configuration.

# Scheduling semantics
For each enabled button, deliver exactly `N` alerts at random instants within each active frequency window:
- hourly = successive 60-minute windows;
- daily = successive 24-hour windows;
- anchor/re-anchor the active window when that button's Random alerts become active again, avoiding ambiguous partial calendar buckets and catch-up behavior.

Precompute/persist future instants or equivalent deterministic pending state; do not implement continuous GPS/polling or a frequent wake loop. Prefer one shared scheduler/dispatcher for the nearest pending Random alert across buttons where compatible with existing infrastructure. Survive process death and reuse existing reboot/reschedule handling. Config changes must cancel stale pending work and schedule the new plan exactly once; prevent duplicate alerts.

Notification must clearly identify the originating button/module. Delivery or tapping the notification must NOT itself record/execute the Timer/Substances action unless an existing explicit user action does so. Tapping should deep-link to the relevant module/button context using existing navigation semantics where available.

# Verification
Focused tests only:
- per-button state/count/unit persist independently across multiple Timer + Substances buttons;
- global OFF suppresses all delivery but preserves per-button configs; ON restores them;
- exactly N unique scheduled instants are generated per active hourly/daily window and stay within bounds;
- two buttons can use different counts/units concurrently;
- disable/delete/config-change cancels stale pending alerts and causes no duplicates;
- re-enable produces future alerts only, no catch-up burst;
- process recreation/reschedule retains valid pending configuration;
- notification identifies the correct button and does not auto-record the action.

Use test-controlled clock/random source so verification is deterministic and does not wait real hours/days. One concise Pixel smoke: configure one Timer and one Substances button, verify master OFF/ON preservation and one forced/due notification path. No broad QA.

Follow current remote PersonalHub bootstrap for final tested APK, Pixel install, Telegram APK delivery and clone cleanup if applicable.

# Stop
PASS only when Timer and Substances share correct per-button Random alerts, the master switch is non-destructive, scheduling delivers the configured total without duplicates/catch-up and notifications identify the correct button. Stop immediately after focused PASS; no unrelated cleanup/audit.

Final output only: `PROMPT_ID`, `RESULT`, Timer/Substances config, global switch semantics, scheduler/window behavior, notification behavior, persistence, tests/Pixel smoke, version, APK delivery, commit/push, blocker if any.
