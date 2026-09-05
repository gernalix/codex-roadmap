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
- MegaVault mode (FAST by default; STANDARD/STRICT only when justified);
- a narrow goal and scope;
- known decisive evidence worth reusing;
- safety/non-goals;
- acceptance criteria and stop condition;
- concise final-output fields.

Optimize prompts for total Codex resource usage: minimize repository exploration, tool calls, redundant verification, retries, reasoning, and session duration. Prefer targeted tests and stop immediately after acceptance criteria pass.

### Empirical execution discipline

Completed-session bundles show that the main avoidable cost can be repeated tool/context round-trips even when reasoning is appropriate. `PROMPT_ID 412907`, a localized PersonalHub DB-transfer hardening task with exact starting files, finished with a technically satisfactory remote diff but still used **84 tool calls** and about **3.86M API-accounted tokens**, with **96.84% of input cached**; the user-facing quota moved only **34% → 35%**. Therefore optimize execution first rather than reflexively downgrading model/reasoning.

For every task, where applicable:

- read all exact starting files in **one grouped command/pass**; if more discovery is needed, use a grouped targeted search tied to a concrete unknown instead of serial one-file/one-query probes;
- batch coherent edits in as few write/patch operations as practical; avoid iterative style-only or reassurance edits;
- batch the smallest targeted tests that prove the acceptance criteria; broaden only after a concrete failure or risk requires it;
- do not repeat `git status`, `git diff`, `git log`, the same file reads/searches, or equivalent tests/builds while repository state is unchanged; one final repository-state/diff check before commit is normally sufficient;
- for a localized task with verified starting files and no unexpected failures, use **≤50 total tool calls as a soft target**. This is not a safety cap: exceed it only when new evidence, a blocker, or a failed acceptance check genuinely requires more investigation;
- larger cross-cutting/architectural tasks have no fixed call ceiling, but every additional round-trip should answer a new question, perform implementation, or prove a distinct acceptance criterion;
- after PASS, do not perform a reassurance audit, re-open already verified files, or inspect later roadmap tasks.

## Workflow "primo task pendente"

Codex must:

1. open `roadmap.md`;
2. execute ONLY the first pending prompt in the list;
3. treat that prompt file as a self-contained task;
4. NOT execute or investigate later prompts;
5. use the model, reasoning level, MegaVault mode, and scope stated in the selected prompt;
6. not expand the task beyond what the selected prompt requests;
7. reuse MegaVault, `AGENTS.md`, and the evidence already included in the selected prompt;
8. avoid redundant exploration, tool calls, retries, and tests, following the empirical execution discipline above;
9. stop as soon as the selected prompt's acceptance criteria are verified.

## Roadmap Management After Execution

`roadmap.md` contains only pending tasks. `completed/` contains only prompts completed with PASS.

If the selected prompt ends with PASS and all acceptance criteria are truly satisfied:

1. move the related file from `prompts/` to `completed/`, preserving its semantic filename;
2. remove that entry from `roadmap.md`;
3. preserve the relative order of all remaining entries and renumber the ordered list consecutively from `1` to `N`;
4. never rename remaining prompt files because their roadmap position changed;
5. commit and push the target project's changes;
6. commit and push the `codex-roadmap` update;
7. do not automatically start the next prompt.

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
