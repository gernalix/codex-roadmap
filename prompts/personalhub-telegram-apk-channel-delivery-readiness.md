PROMPT_ID: 593214

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal
Make the shared cross-project `telegram_notify` facility ready for PersonalHub final-APK delivery to Telegram channel `chat_id=-1004474036791` before any further PersonalHub feature work.

This is an infrastructure/readiness task, not an app feature. Verify with a real Telegram send that the shared notifier can post to that channel. Also verify the exact document-upload capability now required by `MegaVault/ai/personalhubdoc.md`: future final PersonalHub APKs must be sent to this channel as a Telegram document named `<PersonalHub version>.apk`, with no caption and no additional text.

If either channel posting or document delivery does not work, diagnose only the directly relevant shared notifier/config/Telegram permission path and attempt the minimum safe fix that can be completed locally. Do not proceed to later roadmap tasks until this is proven or a genuine external blocker is identified.

# Authoritative notifier — do not use the wrong helper
Use the shared cross-project notifier described by the current PersonalHub bootstrap, not any project-local Telegram helper.

Known authoritative runtime facts from `MegaVault/ai/personalhubdoc.md`:
- shared package: top-level `telegram_notify`;
- canonical installed path: `/usr/local/lib/python3.14/site-packages/telegram_notify`;
- normal invocation: `python3 -m telegram_notify`;
- config: `/home/daniele/.config/codex/secrets/telegram.env`;
- secrets must never be printed, logged, committed, copied into prompts, or included in reports.

Explicitly forbidden:
- do NOT use, modify, copy from, or fall back to the Telegram helper belonging to `amici_fb` / MegaVault `project_id=1`;
- do NOT inspect unrelated projects or Telegram integrations;
- do NOT expose bot tokens or other secret values.

# Narrow starting procedure
1. Read the current `MegaVault/ai/personalhubdoc.md` once and use only the Telegram-related rules relevant to this goal.
2. Inspect the shared `telegram_notify` package entry point/API narrowly (`python3 -m telegram_notify --help`, package metadata, and only the directly relevant source files).
3. Resolve the current shared notifier implementation/source location from the installed package or task-relevant MegaVault facts if modification is actually needed. Do not scan repositories generally.
4. Confirm that the configured shared bot can address `chat_id=-1004474036791` by performing a real send through the shared notifier.

# Real channel verification
Use at most the minimum necessary channel posts and avoid duplicate retries.

A. Text/channel permission check:
- send one harmless test message through the shared notifier to `chat_id=-1004474036791`;
- exact text: `PersonalHub Telegram delivery test`;
- success must come from the Telegram API/shared notifier result, not merely process exit if the helper can mask API errors.

B. Document capability check required for future APK delivery:
- create a tiny temporary local text file outside any repository;
- send it through the same shared notifier/bot to the same chat as a Telegram document;
- Telegram-visible filename must be exactly `telegram-notify-test.txt`;
- caption must be absent;
- no additional companion text message;
- remove the temporary local file afterwards.

If the shared notifier already supports this cleanly, do not change code.

# If it fails
Classify the failure from concrete evidence and fix only the relevant cause.

Allowed local fixes include, when actually required:
- a minimal correction to the shared notifier's chat targeting/config parsing;
- adding the smallest reusable document/file-send path to the shared `telegram_notify` facility, including filename override and optional/no caption behavior;
- correcting the shared notifier installation/source linkage if it points to a broken shared implementation;
- correcting non-secret configuration metadata when the intended channel id is missing or malformed.

Requirements for any notifier code change:
- preserve existing text-notification behavior and existing callers;
- keep the interface reusable across projects rather than hard-coding PersonalHub into general logic;
- never hard-code bot secrets;
- add the smallest focused automated test for the changed behavior when a testable code path exists;
- if there is an authoritative tracked source repo, modify that source, test it, commit/push it, and refresh the installed shared package only as needed; do not treat an untracked site-packages edit as the durable fix when a canonical source exists.

If Telegram reports that the bot is not a member/admin, lacks permission to post, the channel id is inaccessible, or another required action can only be performed by the user/channel administrator, stop as `BLOCKED` after proving the exact external action needed. Do not attempt unrelated workarounds or use another bot/helper.

# PersonalHub scope
Do not modify PersonalHub application code and do not increment `PersonalHub/version.txt` for this readiness task. The PersonalHub bootstrap has already been updated to require final APK Telegram delivery; this task only proves/fixes the shared transport needed to satisfy that rule.

Do not build or install a PersonalHub APK for this task.

# Acceptance criteria
PASS only if all are true:
- the helper used is the shared top-level `telegram_notify`, not the `amici_fb`/project_id=1 helper;
- a real text message reaches `chat_id=-1004474036791` through that shared notifier;
- a real test document reaches the same channel through the same shared notifier;
- the document can be given an explicit Telegram filename and can be sent with no caption/additional text;
- any required shared-notifier fix is durable in its authoritative source and preserves existing text notification behavior;
- no secret value was exposed or committed.

Stop immediately after these checks pass. Do not start the next roadmap task.

Final output only: `PROMPT_ID`, `RESULT`, shared notifier used, text send, document send, filename/no-caption support, fix made (if any), tests, repo/commit (if any), blocker (if any).
