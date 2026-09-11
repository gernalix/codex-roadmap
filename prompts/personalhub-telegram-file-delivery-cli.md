[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=271905 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Remove the recurring Telegram delivery tool-call waste at the end of PersonalHub tasks by making file-only APK delivery a first-class canonical command.

# Starting point
The shared notifier already supports `send_file(path, caption="")`, but its CLI currently requires positional title/message arguments even when `--file` is supplied. Codex therefore tried `--file`, then empty positional strings, then inspected the package internals, and finally called `send_file()` from inline Python. This should be one stable invocation.

# Scope
Make the minimum safe change to the shared `telegram_notify` interface/workflow so Codex can send a file with no caption/text directly from the command line, then record that canonical invocation in the authoritative PersonalHub instructions that already define final APK delivery.

Required behavior:
- `python3 -m telegram_notify --file <path>` (or an equally simple existing-style command) must work without dummy title/message arguments and send the document with an empty caption;
- preserve all existing text-message and captioned-file CLI behavior/backward compatibility;
- reject a missing/non-file path clearly before network work;
- do not expose or print Telegram secrets;
- PersonalHub final delivery instructions must use this canonical file-only CLI path, not inline Python/package introspection;
- do not change Telegram destination/channel semantics already defined for PersonalHub.

Do NOT redesign the notifier, add a new Telegram service, or touch APK build logic.

# Verification
Use focused parser/unit tests or an equivalent non-destructive check proving:
- file-only CLI reaches the existing file-send path with empty caption;
- legacy text invocation still parses/works;
- invalid file path fails clearly.
If a safe existing integration test mechanism is available, use it once; otherwise do not send duplicate production APKs merely to prove parsing.

# Acceptance / stop
PASS when final PersonalHub APK delivery has one documented CLI command with no title/message placeholders or inline Python. Stop immediately after targeted verification and documentation update.

Final output concise: `PROMPT_ID`, `RESULT`, canonical command, backward-compatibility result, tests, files changed, blocker if any.