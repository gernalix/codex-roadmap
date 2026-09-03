# codex-roadmap

Repository of ready-to-run Codex prompts and their execution roadmap.

## Permanent prompt policy

Every file under `prompts/` MUST be self-contained and runnable in a fresh Codex session.

A prompt may assume only:

1. the contents of that prompt file;
2. context Codex can resolve from the stated `project_id` through MegaVault;
3. the target project's `AGENTS.md` and governing protocol/instructions discoverable from that context.

A prompt MUST NOT depend on:

- a previous Codex chat/session;
- phrases such as “as discussed before” unless the required facts are restated in the prompt;
- information that exists only in the conversation that produced the prompt;
- another prompt having been executed, unless that dependency is explicit, unavoidable, and the prompt verifies the required resulting state before acting.

When evidence from an earlier session is relevant, copy the minimum decisive facts/evidence into the prompt so Codex does not need to rediscover them. References such as a previous `PROMPT_ID` are provenance only and must not be required to understand or execute the task.

Each prompt should also state, when applicable:

- `PROMPT_ID`;
- `project_id`;
- recommended model and reasoning level;
- MegaVault mode (FAST by default; STANDARD/STRICT only when justified);
- a narrow goal and scope;
- known decisive evidence worth reusing;
- safety/non-goals;
- acceptance criteria and stop condition;
- concise final-output fields.

Optimize prompts for total Codex resource usage: minimize repository exploration, tool calls, redundant verification, retries, reasoning, and session duration. Prefer targeted tests and stop immediately after acceptance criteria pass.
