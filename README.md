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

## Workflow "primo task pendente"

Codex must:

1. open `roadmap.md`;
2. execute ONLY the first pending prompt in the list;
3. treat that prompt file as a self-contained task;
4. NOT execute or investigate later prompts;
5. use the model, reasoning level, MegaVault mode, and scope stated in the selected prompt;
6. not expand the task beyond what the selected prompt requests;
7. reuse MegaVault, `AGENTS.md`, and the evidence already included in the selected prompt;
8. avoid redundant exploration, tool calls, retries, and tests;
9. stop as soon as the selected prompt's acceptance criteria are verified.

## Roadmap Management After Execution

`roadmap.md` contains only pending tasks. `completed/` contains only prompts completed with PASS.

If the selected prompt ends with PASS and all acceptance criteria are truly satisfied:

1. move the related file from `prompts/` to `completed/`, preserving its filename;
2. remove that entry from `roadmap.md`;
3. do not change the order of the other entries;
4. commit and push the target project's changes;
5. commit and push the `codex-roadmap` update;
6. do not automatically start the next prompt.

If the task fails, remains blocked, or the acceptance criteria are not satisfied:

- do NOT move the prompt;
- do NOT remove it from `roadmap.md`;
- do NOT advance to the next task;
- stop and report the blocker concisely.

## Canonical Launcher

Use this minimal launcher in a new Codex session:

```text
Esegui il primo task pendente di gernalix/codex-roadmap seguendo integralmente il workflow definito nel README. Esegui un solo task e fermati.
```
