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

## Empirical benchmark: PROMPT_ID 184639

Completed task: `codex-usage-monitor` full-quota metadata NO-OP fix + local Fedora runtime verification.

- Model: **GPT-5.5**
- Reasoning: **Medium**
- MegaVault mode: **FAST**
- Duration: **81.6 s**.
- Rollout/API accounting: **39,661 total tokens** = **39,105 input**, of which **38,272 cached (~97.9%)** and only **833 uncached**, plus **556 output**; reasoning output **324**.
- Tool calls: **18 total** = **17 `exec_command` + 1 patch**.
- Observed weekly quota movement: **0 pp** (`100% → 100%`).
- Result: PASS; two-line behavioral change, targeted tests 34/34, push and Fedora systemd/timer verification succeeded without Telegram delivery.

Interpretation:

- Practical quota cost was negligible: this is a useful lower-bound benchmark showing that high cache ratio / tens of thousands of API tokens need not imply visible weekly-quota movement.
- The remaining inefficiency was tool orchestration: **18 calls are still high for a fully pre-localized two-file change**. The transcript shows an unnecessary initial grep of `~/.codex/memories/MEMORY.md`, producing a large irrelevant output despite the prompt already containing the authoritative starting point.
- For comparable self-contained maintenance tasks, skip memory/document discovery, batch independent status/runtime checks, reuse outputs and target roughly **≤10 tool calls** unless a concrete failure appears.
- Medium was harmless here, but a purely mechanical variant without systemd/runtime judgment would be a candidate for GPT-5.5 Low. Do not lower reasoning when lifecycle/runtime decisions are still part of acceptance.

## Empirical benchmark: PROMPT_ID 814627

Completed diagnostic attempt: intermittent Fedora switch from `Performance` to `Power Saver`.

- Model: **GPT-5.5**
- Reasoning: **Medium**
- Duration: **223.991 s (~3m44s)**.
- Prompt accounting: **92,133 total tokens** = **91,346 input**, of which **90,496 cached (~99.07%)** and only **850 uncached**, plus **787 output**; reasoning output **386**.
- Tool calls: **35 total** = **32 `exec_command` + 3 patch calls**, about **9.38 calls/minute**.
- Observed weekly quota movement: **0 pp** (`82% → 82%`).
- Outcome: `WAITING_FOR_EVENT`. The run proved that `tuned-ppd` applied TuneD `powersave`, but did not prove the exact caller/trigger for the 2026-09-16 transition.

Interpretation:

- GPT-5.5 Medium was appropriate: several plausible mechanisms existed (D-Bus profile request/hold, GNOME power policy, ACPI/platform-profile monitoring), and the task required separating the component applying the profile from the component triggering it. Lowering reasoning is not the relevant optimization.
- The main waste was orchestration/output: an unnecessary `MEMORY.md` grep produced thousands of tokens; a broad boot-journal scan produced **13,705 tool-output tokens and was truncated**; a later TuneD log read produced another **6,834**. Once `tuned-ppd` was identified, dedicated logs and a narrow event-time window should have replaced full-boot scans.
- The run created an ad-hoc user `power-profile-watch` even though `fedora-system-monitor` already had a root D-Bus power-profile watcher. The new watcher then hit system-bus monitor authorization fallback and needed follow-up patch/restart churn because its first change detector included the observation timestamp. Future diagnostics should do one targeted canonical-monitor lookup before creating a persistent watcher and should compare timestamp-free semantic snapshots.
- Historical `tuned-ppd` evidence on the same host showed prior `power-saver` holds by `org.gnome.SettingsDaemon.Power`; that is relevant prior evidence, but it does **not** prove the 2026-09-16 trigger. Reports should surface such evidence without promoting it to root cause.
- The publisher stored this run as `UNKNOWN` even though the final report explicitly said `STATUS: WAITING_FOR_EVENT`; efficiency/report tooling should treat that as a status-parsing mismatch rather than a task result.

## Empirical benchmark: PROMPT_ID 815306

Completed task: deterministic PersonalHub Pixel-install + Perfetto-helper runtime validation.

- Model: **GPT-5.5**
- Reasoning: **Low**
- Duration: **74.673 s**.
- Tool calls: **12**, all `exec_command`.
- Input **41,009**, cached **40,320 (~98.32%)**, uncached **689**; output **177**; reasoning **75**.
- Weekly quota movement: **0 pp** (`80% → 80%`).
- Result: PASS.

Interpretation:

- GPT-5.5 Low is a good fit for a truly narrow helper/runtime smoke with known commands and deterministic acceptance.
- Even here, small discovery around artifact/Perfetto paths was avoidable; canonical helpers should absorb that lookup.
- This is the benchmark for tasks that should remain Low: few decisions, one runtime target, no cross-module design or iterative UI debugging.

## Empirical benchmark: PROMPT_ID 838979

Completed host-side PersonalHub Hub/episodes usability phase.

- Model: **GPT-5.5**
- Reasoning: **Medium**
- Duration: **653.545 s (~10m54s)**.
- Tool calls: **93** = 78 `exec_command`, 14 patch, 1 wait.
- Input **168,478**, cached **167,296 (~99.30%)**, uncached **1,182**; output **295**; reasoning **115**.
- Weekly quota movement: **1 pp**.

Interpretation:

- Medium was sufficient for a 16-file cross-module UI/repository change; GPT-5.6 was not needed.
- The main failures were wrong initial workdir, unnecessary MEMORY/MegaVault reads, wide grep, repeated Gradle sets and a remote-advance/rebase cycle.
- Cross-module scope alone does not justify GPT-5.6 when boundaries, desired behavior and tests are already specified.

## Empirical benchmark: PROMPT_ID 314719

Completed Timer Now implementation + emulator QA attempt.

- Model: **GPT-5.5**
- Reasoning: **Low**
- Duration: **1,589.003 s (~26m29s)**.
- Tool calls: **139** = 109 `exec_command`, 19 patch, 11 waits.
- Input **182,121**, cached **181,632 (~99.73%)**, uncached **489**; output **314**; reasoning **141**.
- Weekly quota movement: **2 pp** (`79% → 77%`).
- Timer Now implementation/QA succeeded; roadmap bookkeeping was blocked and inherited Hub QA was not actually proven by the intended focused emulator test.

Interpretation:

- Low was too aggressive for a task combining Compose implementation, Gradle multi-module instrumentation, emulator state and inherited acceptance from another phase. **Use GPT-5.5 Medium for this class of task.**
- The 2-point quota movement tracks 26 minutes / 139 tool calls far more plausibly than the tiny 489 uncached input or 141 reasoning tokens.
- Wrong workdir, task-name discovery, 30-second polling, manual UI navigation, first-run gate setup, repeated instrumentation runs and post-PASS cosmetic patching created most of the avoidable churn.
- A physical-device test guard must never be weakened merely to reuse it on the emulator; create one dedicated emulator-safe test instead.
- Known Gradle module/task, exact test class, canonical helper and delivery command should be encoded directly into the prompt.

## How to calibrate future prompts

Before saving a new prompt, choose model/reasoning from task characteristics and the measured evidence above. Encode only task-specific scope, decisive known evidence, pre-localized starting files/symbols, safety/non-goals, acceptance criteria and concise output requirements. Let the governing MegaVault/PersonalHub bootstrap supply global execution behavior.

When a new completed-session bundle is available, compare model/reasoning, measured user-facing usage when present, tool calls, duration, retries and verified technical outcome against these benchmarks. Treat cached-input volume as secondary diagnostic context, not as an optimization goal. Prefer measured evidence over generic assumptions.
