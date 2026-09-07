PROMPT_ID: 593214

project_id: 49
Recommended model: GPT-5.5
Reasoning: low
MegaVault: FAST

# Goal
Make the shared cross-project `telegram_notify` facility ready for PersonalHub final-APK delivery to the **same Telegram destination that the shared notifier previously used for Codex progress/status notifications** before any further PersonalHub feature work.

This is an infrastructure/readiness task, not an app feature. Telegram must no longer be used for PersonalHub progress/test/install status messages. The only PersonalHub Telegram use governed here is final APK artifact delivery. Verify with a real send that the shared notifier can post to its existing default/former-progress destination, and verify the exact document-upload capability required by the current remote `MegaVault/ai/personalhubdoc.md`: future final PersonalHub APKs must be sent there as a Telegram document named `<PersonalHub version>.apk`, with no caption and no additional text.

Do **not** assume or hard-code `chat_id=-1004474036791`. Resolve the shared notifier's already-configured default destination at runtime from its authoritative configuration/API without printing secrets or sensitive configuration. Use exactly that destination. If the configured destination cannot be resolved safely, stop with concrete evidence rather than guessing.

If either destination posting or document delivery does not work, diagnose only the directly relevant shared notifier/config/Telegram permission path and attempt the minimum safe fix that can be completed locally. Do not proceed to later roadmap tasks until this is proven or a genuine external blocker is identified.

# Authoritative sources and notifier
Consult MegaVault and codex-roadmap only from their current remote repositories, never from local checkouts, per the current PersonalHub bootstrap.

Use the shared cross-project notifier described by the current **remote** PersonalHub bootstrap, not any project-local Telegram helper.

Known authoritative runtime facts from `MegaVault/ai/personalhubdoc.md`:
- shared package: top-level `telegram_notify`;
- canonical installed path: `/usr/local/lib/python3.14/site-packages/telegram_notify`;
- config: `/home/daniele/.config/codex/secrets/telegram.env`;
- destination: the notifier's existing default destination formerly used for Codex progress/status notifications;
- secrets and sensitive config values must never be printed, logged, committed, copied into prompts, or included in reports.

Explicitly forbidden:
- do NOT use, modify, copy from, or fall back to the Telegram helper belonging to `amici_fb` / MegaVault `project_id=1`;
- do NOT inspect unrelated projects or Telegram integrations;
- do NOT expose bot tokens or other secret values;
- do NOT redirect delivery to `-1004474036791` merely because an older prompt mentioned it;
- do NOT send PersonalHub progress/test/install status notifications.

# Narrow starting procedure
1. Fetch/read the current remote `gernalix/MegaVault` `ai/personalhubdoc.md` once and use only the Telegram/source rules relevant to this goal.
2. Inspect the shared `telegram_notify` package entry point/API narrowly (`python3 -m telegram_notify --help`, package metadata, and only directly relevant source files).
3. Resolve the notifier's configured default/former-progress destination without echoing its secret/config value. Do not substitute a guessed destination.
4. Resolve the current shared notifier implementation/source location only if modification is actually needed. Do not scan repositories generally.
5. Confirm that the configured shared bot can address that exact destination with one real verification send.

# Real destination verification
Use at most the minimum necessary posts and avoid duplicate retries.

A. Text/permission check:
- send one harmless test message through the shared notifier to its configured default/former-progress destination;
- exact text: `PersonalHub Telegram delivery test`;
- success must come from the Telegram API/shared notifier result, not merely process exit if the helper can mask API errors.

B. Document capability check required for future APK delivery:
- create a tiny temporary local text file outside any repository;
- send it through the same shared notifier/bot to the same destination as a Telegram document;
- Telegram-visible filename must be exactly `telegram-notify-test.txt`;
- caption must be absent;
- no additional companion text message;
- remove the temporary local file afterwards.

If the shared notifier already supports this cleanly, do not change code.

# If it fails
Classify the failure from concrete evidence and fix only the relevant cause.

Allowed local/runtime fixes include, when actually required:
- a minimal correction to shared notifier destination/config parsing;
- adding the smallest reusable document/file-send path to the shared `telegram_notify` facility, including filename override and optional/no-caption behavior;
- correcting the shared notifier installation/source linkage if it points to a broken shared implementation;
- correcting non-secret configuration metadata when malformed.

Requirements for any notifier code change:
- preserve existing text-notification behavior for non-PersonalHub callers;
- keep the interface reusable across projects rather than hard-coding PersonalHub;
- never hard-code bot secrets;
- add the smallest focused automated test for changed behavior when a testable code path exists;
- if there is an authoritative tracked source repo, modify that source, test it, commit/push it, and refresh the installed shared package only as needed; do not treat an untracked site-packages edit as the durable fix when a canonical source exists.

If Telegram reports that the bot is not a member/admin, lacks permission to post, the destination is inaccessible, or another required action can only be performed by the user/channel administrator, stop as `BLOCKED` after proving the exact external action needed. Do not attempt unrelated workarounds or use another bot/helper.

# PersonalHub scope
Do not modify PersonalHub application code and do not increment `PersonalHub/version.txt` for this readiness task. Do not build or install a PersonalHub APK. The task only proves/fixes the shared transport and confirms the correct final-APK destination.

# Acceptance criteria
PASS only if all are true:
- the helper used is the shared top-level `telegram_notify`, not the `amici_fb`/project_id=1 helper;
- the destination used is exactly the shared notifier's configured default/former-progress destination, not a guessed/hard-coded replacement;
- a real text test reaches that destination through the shared notifier;
- a real test document reaches the same destination through the same shared notifier;
- the document can be given an explicit Telegram filename and sent with no caption/additional text;
- current PersonalHub rules no longer require/send Telegram progress/test/install status messages;
- any required shared-notifier fix is durable in its authoritative source and preserves existing text behavior for other callers;
- no secret or sensitive configuration value was exposed or committed.

Stop immediately after these checks pass. Do not start the next roadmap task.

Final output only: `PROMPT_ID`, `RESULT`, shared notifier used, destination match (yes/no; do not print sensitive destination if config treats it as sensitive), text send, document send, filename/no-caption support, fix made (if any), tests, repo/commit (if any), blocker (if any).
