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

### Semantic filenames; roadmap order only

The execution order MUST exist only as the consecutive numeric position in the ordered list in `roadmap.md`: `1.`, `2.`, `3.`, ...

Prompt filenames/titles MUST be stable semantic names and MUST NOT contain any numeric or alphanumeric ordering prefix or suffix. Forbidden examples include `04-...`, `04b-...`, `09b1-...`, `task-12-...` or equivalent ordering codes. Use names such as `personalhub-complete-module-capsulization.md`.

Dependencies and roadmap prose must identify tasks by semantic filename/title or by their functional meaning, never by an ordering code. When tasks are inserted, removed or reordered, renumber only the ordered list in `roadmap.md`; never rename prompt files merely because their position changed.

`PROMPT_ID` is a random task identifier, not an ordering mechanism, and is unaffected by this rule.

Each prompt should also state, when applicable:

- `PROMPT_ID`;
- `project_id`;
- recommended model and reasoning level;
- MegaVault mode;
- a narrow goal and task-specific scope;
- known decisive evidence worth reusing;
- exact/pre-localized starting files or symbols when useful;
- safety/non-goals specific to the task;
- acceptance criteria and stop condition;
- concise final-output fields.

### Canonical execution discipline

`MegaVault/ai/MEGAVAULT_PROTOCOL.md` is the single authoritative source for global Codex execution discipline, including mode selection, token efficiency, exploration, batching, tool-call discipline, retries, validation, Git behavior, Android/device handling, notifications and post-PASS stopping rules.

Do **not** duplicate those global rules in this README, `roadmap.md`, or individual prompt files. Prompts may add only task-specific constraints or stricter requirements needed for that task. `codex-calibration.md` stores empirical usage evidence and model/reasoning calibration, not a competing execution protocol.

### Keep `spiegazioni.md` synchronized

`spiegazioni.md` is the plain-language companion to the pending roadmap and MUST stay synchronized with it.

Whenever `roadmap.md` is changed, or any prompt currently referenced by `roadmap.md` is added, removed, renamed, reordered, or materially changed, update `spiegazioni.md` in the same repository change.

Requirements:

- include exactly one explanation for every pending prompt in `roadmap.md`, in the same order;
- remove explanations for prompts that are no longer pending;
- keep each explanation understandable to a reader with no programming knowledge;
- explain primarily what problem the task solves and what will change for the user, avoiding implementation jargon unless indispensable;
- if a prompt's behavior or scope changes materially, update its explanation even if its filename and roadmap position do not change.

A roadmap/prompt maintenance change is incomplete until this synchronization has been checked.

## Workflow "primo task pendente"

Codex must:

1. open `roadmap.md`;
2. execute ONLY the first pending prompt in the list;
3. treat that prompt file as a self-contained task;
4. NOT execute or investigate later prompts;
5. use the model, reasoning level, MegaVault mode, and scope stated in the selected prompt;
6. not expand the task beyond what the selected prompt requests;
7. reuse MegaVault, `AGENTS.md`, and the evidence already included in the selected prompt;
8. follow the authoritative execution discipline in `MegaVault/ai/MEGAVAULT_PROTOCOL.md` plus only the selected prompt's task-specific constraints;
9. stop as soon as the selected prompt's acceptance criteria are verified.

## Roadmap Management After Execution

`roadmap.md` contains only pending tasks. `completed/` contains only prompts completed with PASS.

If the selected prompt ends with PASS and all acceptance criteria are truly satisfied:

1. move the related file from `prompts/` to `completed/`, preserving its semantic filename;
2. remove that entry from `roadmap.md`;
3. preserve the relative order of all remaining entries and renumber the ordered list consecutively from `1` to `N`;
4. never rename remaining prompt files because their roadmap position changed;
5. update `spiegazioni.md` so it again contains exactly the pending prompts in `roadmap.md`, in the same order;
6. commit and push the target project's changes;
7. commit and push the `codex-roadmap` update;
8. do not automatically start the next prompt.

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
