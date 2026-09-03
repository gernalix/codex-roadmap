# Codex prompt calibration — empirical rules

This file is persistent guidance for writing and updating **all current and future prompts** in this repository. Update it when new completed-session usage evidence is available.

## Baseline

Default to **GPT-5.5**. Use the cheapest reasoning level sufficient for the task:

- **Low**: localized/mechanical changes with an obvious implementation and narrow verification.
- **Medium**: debugging with multiple plausible failure modes, lifecycle/concurrency/persistence issues, Gradle/build-system behavior, safety guardrails, or changes where proving the root cause matters.
- **GPT-5.6 Sol** only when materially needed for difficult ambiguity, cross-cutting architecture, high-risk changes, or when GPT-5.5 evidence shows it is insufficient. Terra/Luna only if their additional capability is concretely justified.
- Avoid High/Ultra unless a specific task clearly requires them.

MegaVault: **FAST by default** for localized low-risk work; STANDARD only when broader verification is genuinely needed; STRICT only for genuinely high-risk/destructive/security/critical-infrastructure/migration work.

## Primary optimization target

Optimize **total Codex work**, not prompt character count. Token/quota consumption is driven mainly by context/tool round-trips and session work. Therefore every prompt should, where applicable:

1. Start from `project_id`, MegaVault and `AGENTS.md`/governing protocol; reuse already verified evidence.
2. Begin with directly relevant files/components; **no general repository exploration** unless evidence requires expansion.
3. Use the smallest sufficient set of inspections/commands. Do not run equivalent/redundant checks.
4. Never retry an identical failed command without new evidence or a changed condition.
5. Prefer targeted tests for changed behavior; broaden only when risk or a failing result justifies it.
6. No unrelated refactor, cleanup, modernization, optimization, documentation sweep, or collateral bug investigation.
7. Report collateral issues without investigating them unless they block the requested goal.
8. Stop immediately once acceptance criteria are evidenced. **No post-PASS audit/exploration.**
9. Keep progress narration minimal and final output concise.
10. For directly related changes to the same feature, one coherent task can reduce duplicated bootstrap/exploration. Keep independent objectives separate; use a fresh session when carrying a long unrelated context would cost more.
11. Treat **tool-call count as an explicit budget**. For a narrowly scoped task, each additional shell/tool round-trip should be justified by new evidence, implementation, or a distinct acceptance criterion. Prefer one batched inspection over many serial reads and one targeted verification command over multiple overlapping checks.

## Empirical benchmark: PROMPT_ID 428619

Completed task: PersonalHub protection of the live app from destructive benchmark/profile tests.

- Model: **GPT-5.5**
- Reasoning: **Medium**
- User-facing usage monitor: **157,946 tokens**
- Duration: **~7m27s**
- Rollout/API accounting observed from archived session: **~1.996M total API tokens**, **~1.835M cached input (~92%)**, **~13k output**, **~2.6k reasoning tokens**.
- Tool calls observed: **73 total**, including **67 exec_command** calls.

Interpretation:

- GPT-5.5 Medium was appropriate because the task required proving a Gradle/AGP lifecycle root cause, isolating an Android package, adding fail-closed destructive-operation guardrails, and validating negative safety behavior.
- Reasoning/output tokens were not the dominant cost. The strongest optimization opportunity is reducing tool calls, repeated context processing, redundant inspection and verification.
- Do **not** downgrade comparable safety/debugging tasks to Low merely to save tokens; instead constrain exploration and command count.
- Cached-input API token totals are not directly equivalent to the user's quota/usage-monitor token figure. Track both when available, but use the user's usage metric for practical cross-session quota comparisons.

## Empirical benchmark: PROMPT_ID 736205

Completed task: PersonalHub durable SAF auto-export diagnosis/fix.

- Model: **GPT-5.5**
- Reasoning: **Medium**
- Duration from rollout: **~9m57s**.
- Rollout/API accounting: **4,061,251 total tokens** = 4,041,417 input, 3,919,360 cached input (~97.0% of input), 19,834 output, 2,669 reasoning output.
- Tool calls: **80 `exec_command`** calls.
- User-facing usage-monitor figure was not supplied with this archive, so do not compare quota consumption directly against 428619 until that metric is available.

Interpretation:

- Medium remained justified: the task required proving a persistence/process-death failure mode and changing mutation/WorkManager durability semantics.
- Despite an explicitly optimized prompt, API-token volume was about twice the 428619 benchmark while reasoning remained tiny. This strengthens the conclusion that lowering reasoning is not the main optimization lever for this class of task.
- 80 shell round-trips caused repeated large cached-context processing. Future prompts should be more aggressive about **batched reads/searches and command budgets**, and should avoid serial one-file/one-query exploration when a single grouped command can answer the same question.
- Acceptance criteria should distinguish **must-prove** from optional robustness checks. Once the must-prove criteria pass, stop; do not spend calls on additional reassurance.
- When a task already names likely components/failure modes, instruct Codex to inspect those in a small number of grouped commands before branching into additional hypotheses.

## How to calibrate future prompts

Before saving a new prompt, assign model/reasoning from task characteristics and available empirical evidence. Then explicitly encode scope, known evidence, minimal starting files/components, targeted verification, forbidden redundant work, a practical tool-call discipline, and a hard stop condition.

After a task completes, when usage/session evidence is supplied, compare it with these benchmarks and update these rules if it supports a better calibration. Prefer measured evidence over generic assumptions.