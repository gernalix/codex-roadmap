# codex-roadmap

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

Repository di prompt Codex pronti all'uso, con indice operativo e spiegazioni separate.

## Separazione canonica dei contenuti

- `roadmap.md` contiene **solo** la lista numerata e ordinata dei prompt pendenti: una riga per prompt, senza titolo, introduzioni, audit, spiegazioni, dipendenze, raccomandazioni, regole o note.
- `spiegazioni.md` contiene **solo** le spiegazioni in linguaggio umano dei prompt pendenti, nello stesso ordine e una per prompt. Qui va spiegato il problema e il cambiamento percepibile dall'utente; non vi si duplicano istruzioni operative dettagliate.
- `prompts/*.md` contiene le sole istruzioni eseguibili da Codex, in formato compatto e AI-friendly: metadati brevi, goal, evidenza già verificata, scope/starting point, requisiti, verifiche, acceptance/stop e output. Eliminare narrazione, motivazioni ripetute, riepiloghi da audit e regole globali già definite dal protocollo MegaVault; conservare però ogni fatto e vincolo necessario a rendere il prompt autosufficiente.
- Le regole di manutenzione e di esecuzione appartengono a questo `README.md`, non a `roadmap.md` o `spiegazioni.md`.

Ogni modifica deve preservare questa separazione. Se un'informazione non serve a eseguire il task ma serve a capirne il motivo, va soltanto in `spiegazioni.md`; se serve a governare tutti i task, va soltanto nel README.

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

### Obsidian navigation is mandatory

The repository MUST remain directly navigable as an Obsidian vault using wikilinks.

Requirements:

- every pending prompt listed in `roadmap.md` MUST be a clickable Obsidian wikilink to its file under `prompts/`;
- every corresponding heading in `spiegazioni.md` MUST link to the same prompt;
- every pending prompt MUST contain explicit links back to both `[[roadmap|Roadmap]]` and `[[spiegazioni|Spiegazioni]]`, so navigation is bidirectional even outside Obsidian's Backlinks view;
- `README.md` and `spiegazioni.md` SHOULD link to each other; `roadmap.md` links only to prompts, while every pending prompt links back to roadmap and explanations;
- use stable path-based links such as `[[prompts/personalhub-example|personalhub-example]]`; do not use ordering numbers as link targets;
- when a prompt is renamed, moved to `completed/`, added or removed, update all affected wikilinks in the same repository change;
- do not leave dangling wikilinks to removed pending prompts.

A roadmap/prompt maintenance change is incomplete until Obsidian navigation and automatic backlink resolution have been checked together with roadmap/spiegazioni synchronization.

### Canonical execution discipline

`MegaVault/ai/MEGAVAULT_PROTOCOL.md` is the single authoritative source for global Codex execution discipline, including mode selection, token efficiency, exploration, batching, tool-call discipline, retries, validation, Git behavior, Android/device handling, notifications and post-PASS stopping rules.

Do **not** duplicate those global rules in this README, `roadmap.md`, or individual prompt files. Prompts may add only task-specific constraints or stricter requirements needed for that task. `codex-calibration.md` stores empirical usage evidence and model/reasoning calibration, not a competing execution protocol.

### Consolidation-first roadmap policy

The roadmap SHOULD prefer a smaller number of substantial, coherent prompts over many micro-prompts when doing so reduces total Codex work.

Before adding a new pending prompt, compare it against the existing pending work and merge it into an existing/new consolidated goal when most of the following are true:

- same target project/module or tightly coupled feature area;
- overlapping authoritative starting files/symbols or domain model;
- the later work directly consumes state/contracts created by the earlier work;
- compatible recommended model, reasoning level and MegaVault risk mode;
- meaningful opportunity to reuse bootstrap, exploration, build/install, device setup or QA;
- the combined task can remain bounded with explicit internal phases and acceptance criteria.

A consolidated prompt MUST:

- preserve every material requirement and acceptance criterion from the absorbed prompts;
- organize distinct concerns as explicit internal phases rather than mixing them into an unstructured mega-task;
- read phase-local files only when needed and reuse already verified context across phases;
- capture the PersonalHub base version once and increment once for the whole goal;
- run narrow phase checks as needed but perform one explicit final APK build/install/end-to-end QA unless a safety requirement genuinely demands otherwise;
- stop immediately after the consolidated acceptance criteria pass.

Keep prompts separate when consolidation would force materially more expensive model/reasoning over unrelated work, mix incompatible risk modes, combine unrelated repositories/domains, make rollback/diagnosis substantially harder, or carry a large irrelevant context into a later independent task. Fewer prompt files is not itself the objective; lower total reasoning/tool-call/build/QA cost is.

Do not restructure, rename, reorder or absorb a prompt that is actively being executed by Codex. Treat active work as immutable until that execution has finished/published its result.

If two tasks are too large to merge safely but would still save substantial quota by sharing one session, prefer an explicitly marked continuous campaign instead of keeping fully independent sessions.

### Keep `spiegazioni.md` synchronized

`spiegazioni.md` is the plain-language companion to the pending roadmap and MUST stay synchronized with it.

Whenever `roadmap.md` is changed, or any prompt currently referenced by `roadmap.md` is added, removed, renamed, reordered, or materially changed, update `spiegazioni.md` in the same repository change.

Requirements:

- include exactly one explanation for every pending prompt in `roadmap.md`, in the same order;
- remove explanations for prompts that are no longer pending;
- keep each explanation understandable to a reader with no programming knowledge;
- explain primarily what problem the task solves and what will change for the user, avoiding implementation jargon unless indispensable;
- if a prompt's behavior or scope changes materially, update its explanation even if its filename and roadmap position do not change.
- never copy audit evidence, model/risk metadata, execution constraints or acceptance criteria into `spiegazioni.md`; those belong to the prompt.

A roadmap/prompt maintenance change is incomplete until this synchronization has been checked.

## Continuous roadmap campaigns

The default remains one pending prompt per Codex session. A consecutive set may form a **continuous campaign** when every participating prompt declares the same `campaign_id` plus its `phase`/`phases` metadata. Campaign metadata belongs only in prompt files; `roadmap.md` remains a plain list.

Campaign rules:

1. The individual prompt files remain self-contained and independently runnable in a fresh session. Campaign mode changes orchestration only; it does not merge their scopes into an unbounded mega-task.
2. If the first pending roadmap item belongs to a campaign, Codex executes the campaign phases sequentially in the **same session**, opening the next phase only after the current phase's targeted acceptance checks pass. Carry forward already verified files, symbols and facts; do not re-bootstrap or rediscover them unless evidence changed.
3. A phase-local `PASS` before the final campaign phase is an internal checkpoint, not a final task completion. In campaign mode, phase-local instructions such as `stop immediately after PASS`, final-output-only fields, per-phase commit SHA requirements and automatic roadmap movement are deferred until the final campaign phase. `BLOCKED` or `FAIL` still stops the campaign immediately.
4. Versioning is campaign-wide: capture the PersonalHub base version once at campaign start and set `target = base + 1`. Any later phase instruction to increment `version.txt` again is ignored in campaign mode. Resume of the same unfinished campaign reuses the already chosen target and never increments it again.
5. Phases before the final campaign phase run only the narrow targeted tests/checks needed to validate their own contracts. Do not perform a standalone final PersonalHub APK assemble/install or full Pixel/TCL end-to-end pass in those phases. Test commands may still trigger the minimum incremental compilation required by the targeted tests; “one final build” means one explicit final full APK build/install pass, not zero compilation by Gradle during tests.
6. The final campaign phase performs the single final main APK build, safe install/update on the required devices and the campaign's consolidated end-to-end QA.
7. Avoid intermediate roadmap churn. If the whole campaign passes, commit/push the target project as appropriate, move all campaign prompt files to `completed/`, remove all campaign entries from `roadmap.md`, renumber once, update `spiegazioni.md` once, and commit/push the roadmap repository. If the campaign stops early, leave roadmap membership unchanged and report the last completed phase plus the blocker; a later run must verify and reuse already implemented state rather than redo it.
8. Campaign model/reasoning is declared consistently in the participating prompt metadata; phase-specific MegaVault modes and scope constraints still apply.

This section is the only exception to the normal one-task-per-session and post-PASS stop rules below.

## Workflow "primo task pendente"

Codex must:

1. open `roadmap.md`;
2. execute ONLY the first pending prompt in the list, **unless it belongs to an explicitly marked continuous campaign**; in that case execute that entire campaign according to the rules above;
3. treat a normal prompt file as a self-contained task, and each campaign prompt as a self-contained phase whose scope remains bounded by that file;
4. NOT execute or investigate later prompts outside the selected task/campaign;
5. use the model, reasoning level, MegaVault mode, scope and any campaign metadata stated in the selected prompt;
6. not expand the task/campaign beyond what the selected prompt(s) request;
7. reuse MegaVault, `AGENTS.md`, and the evidence already included in the selected prompt, and within a campaign reuse verified context from earlier phases rather than rediscover it;
8. follow the authoritative execution discipline in `MegaVault/ai/MEGAVAULT_PROTOCOL.md` plus only the selected prompt's/task campaign's specific constraints;
9. stop as soon as the selected normal prompt's acceptance criteria are verified, or after the final campaign phase passes; stop earlier on `BLOCKED`/`FAIL`.

## Roadmap Management After Execution

`roadmap.md` contains only pending tasks. `completed/` contains only prompts completed with PASS.

For an explicitly marked continuous campaign, the campaign rules above override per-prompt movement until the campaign reaches its final phase.

If the selected normal prompt ends with PASS and all acceptance criteria are truly satisfied:

1. move the related file from `prompts/` to `completed/`, preserving its semantic filename;
2. remove that entry from `roadmap.md`;
3. preserve the relative order of all remaining entries and renumber the ordered list consecutively from `1` to `N`;
4. never rename remaining prompt files because their roadmap position changed;
5. update `spiegazioni.md` so it again contains exactly the pending prompts in `roadmap.md`, in the same order;
6. update Obsidian wikilinks so no pending navigation link points to the moved prompt; reverse navigation remains provided automatically by Obsidian backlinks;
7. commit and push the target project's changes;
8. commit and push the `codex-roadmap` update;
9. do not automatically start the next prompt.

If the task fails, remains blocked, or the acceptance criteria are not satisfied:

- do NOT move the prompt;
- do NOT remove it from `roadmap.md`;
- do NOT advance to the next task;
- stop and report the blocker concisely.

## Canonical Launcher

Use this minimal launcher in a new Codex session:

```text
Esegui il primo task pendente di gernalix/codex-roadmap seguendo integralmente il workflow definito nel README. Se il primo prompt dichiara una campagna continua, esegui nello stesso ordine tutte le sue fasi consecutive con lo stesso `campaign_id` e fermati al termine; altrimenti esegui un solo task e fermati.
```
