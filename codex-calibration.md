# Codex prompt calibration — empirical evidence

This file stores empirical completed-session evidence used to choose the cheapest sufficient **model and reasoning level** for current and future prompts in this repository.

Global execution discipline is defined only by `MegaVault/ai/MEGAVAULT_PROTOCOL.md`. Do not duplicate its exploration, batching, tool-call, retry, validation, Git, device or stop rules here; empirical findings below may explain why those protocol rules exist.

## Model / reasoning baseline

Default to **GPT-5.5**. Use the cheapest reasoning level sufficient for the task:

- **Low**: localized/mechanical changes with an obvious implementation and narrow verification.
- **Medium**: debugging with multiple plausible failure modes, lifecycle/concurrency/persistence issues, Gradle/build-system behavior, safety guardrails, or changes where proving the root cause matters.
- **GPT-5.6 Sol** only when materially needed for difficult ambiguity, cross-cutting architecture, high-risk changes, or when GPT-5.5 evidence shows it is insufficient. Terra/Luna only if their additional capability is concretely justified.
- Avoid High/Ultra unless a specific task clearly requires them.

Use the MegaVault mode selected under the authoritative protocol; this file does not redefine FAST/STANDARD/STRICT.

## Usage-diagnosis priority

When judging whether a completed Codex task consumed too much, prioritize evidence in this order:

1. observed user-facing quota movement / usage-monitor result;
2. tool-call count and duration, especially repeated `exec_command` / patch round-trips;
3. retries, duplicated probes, unnecessary validation and post-PASS work;
4. uncached input and output/reasoning only when they are materially large.

A high cached-input ratio is **descriptive, not itself a bottleneck**. Do not repeatedly recommend “reduce cached context” merely because total input tokens are large. If quota movement is high while uncached input/reasoning is small, diagnose the repeated tool/context round-trips and session duration first.

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
- Reasoning/output tokens were not the dominant cost; repeated tool/context round-trips were the strongest avoidable cost signal.
- Cached-input API totals are not directly equivalent to the user's quota/usage-monitor figure; use the user-facing metric for practical cross-session quota comparisons when available.

## Empirical benchmark: PROMPT_ID 736205

Completed task: PersonalHub durable SAF auto-export diagnosis/fix.

- Model: **GPT-5.5**
- Reasoning: **Medium**
- Duration from rollout: **~9m57s**.
- Rollout/API accounting: **4,061,251 total tokens** = 4,041,417 input, 3,919,360 cached input (~97.0% of input), 19,834 output, 2,669 reasoning output.
- Tool calls: **80 `exec_command`** calls.
- User-facing usage-monitor figure was not supplied with this archive, so do not compare quota consumption directly against 428619 until that metric is available.

Interpretation:

- Medium remained justified because the task required proving a persistence/process-death failure mode and changing mutation/WorkManager durability semantics.
- API-token volume was about twice the 428619 benchmark while reasoning remained tiny, again pointing to execution round-trips/context reprocessing rather than reasoning depth as the main efficiency lever.

## Empirical benchmark: PROMPT_ID 412907

Completed task: PersonalHub canonical DB import/export recovery hardening (`personalhub-database-vault-transfer-hardening.md`).

- Model: **GPT-5.5**
- Reasoning: **Medium**
- MegaVault mode used: **STRICT**
- Duration: **637.6 s (~10m38s)**.
- Rollout/API accounting: **3,861,535 total tokens** = **3,841,683 input**, of which **3,720,448 cached (~96.84%)** and **121,235 non-cached**, plus **19,852 output**; reasoning output observed: **3,091**.
- Tool calls: **84 total**.
- User-facing quota moved **34% → 35%** during the session.
- Independent remote review verified commit `e4f05d4fef76975a567b3c83a46496138c8250b2`: the requested atomic/fail-safe import-marker handling and SAF rollback hardening are present on `PersonalHub/main`, with targeted durability tests. GitHub exposes no CI status for that commit, so test execution remains supported by the Codex session report rather than GitHub Actions.

Interpretation:

- GPT-5.5 Medium remained appropriate because the task involved process-death durability, filesystem atomicity/fsync semantics and failure-safe recovery. The good technical result is evidence against lowering reasoning merely to save quota.
- **84 tool calls were excessive for this localized, pre-localized task** despite the satisfactory implementation.
- The large API-token total was mostly cached context and translated into only a one-point user-facing quota movement, so raw API accounting alone can overstate practical quota cost.
- This benchmark directly motivated the centralized execution-efficiency additions now owned by `MegaVault/ai/MEGAVAULT_PROTOCOL.md`; the normative rules are intentionally not repeated here.

## Empirical benchmark: PROMPT_ID 416738

Completed task: Timer alert notification correction (`personalhub-timer-alerts.md`).

- Model: **GPT-5.5**
- Reasoning: **Medium**
- MegaVault mode: **STANDARD**
- Duration: **747.2 s (~12m27s)**.
- Tool calls: **119 total** = **102 `exec_command` + 17 patch calls**.
- Input: **138,761**, of which **137,600 cached** and only **1,161 uncached**; output **829**; reasoning output **405**.
- Observed weekly quota: **62% → 60% remaining-equivalent movement of 2 percentage points used in that cycle's monitor accounting**.
- The implementation correctly changed the direct `TimeFenceNotifier.notify()` path to a normal Android notification, but the task produced a false-positive PASS for the real installed-data scenario: persisted legacy `PREFENCE` rules were not migrated, and the acceptance check did not fire a pre-existing real alert on the installed Pixel. A newly created notification alert was later observed to fire, but with a material timing delay that the original tests also did not measure.

Interpretation:

- **119 calls are excessive** for a pre-localized task and are the primary efficiency failure. The 99% cache ratio is not the remediation target.
- More tool calls did not buy better correctness: despite 119 calls, a user-visible legacy-data path and real Android delivery timing were not verified.
- Future Android notification/alarm tasks must prefer one focused live-platform acceptance check over additional static/reassurance probes when platform behavior is part of the acceptance criteria.
- For similar localized debugging, keep GPT-5.5 Medium; reduce tool round-trips rather than lowering reasoning merely to save quota.

## How to calibrate future prompts

Before saving a new prompt, choose model/reasoning from task characteristics and the measured evidence above. Encode only task-specific scope, decisive known evidence, pre-localized starting files/symbols, safety/non-goals, acceptance criteria and concise output requirements. Let the governing MegaVault/PersonalHub bootstrap supply global execution behavior.

When a new completed-session bundle is available, compare model/reasoning, measured user-facing usage when present, tool calls, duration, retries and verified technical outcome against these benchmarks. Treat cached-input volume as secondary diagnostic context, not as an optimization goal. Prefer measured evidence over generic assumptions.
