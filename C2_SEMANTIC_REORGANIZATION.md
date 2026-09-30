# C2 semantic roadmap contract

This is the canonical boundary between deterministic C2 automation and AI semantic work.

## Authority
- `roadmap.sqlite`: canonical work-item state.
- deterministic control plane: facts, lifecycle, locks, receipts, sync, reconciliation, projections.
- AI semantic executor: interpretation and roadmap design only.
- single writer: only authority allowed to make canonical roadmap mutations.

Rule: **if structured facts imply one valid result, use code; if multiple reasonable interpretations/decisions remain, use AI.**

## Deterministic control plane
May:
- reconcile run/work-item lifecycle from authoritative receipts and repo/PR/CI/merge state;
- bind task/run/executor/chat/PROMPT_ID/repo identities;
- enforce state-machine, locks, fencing, idempotency and invariants;
- derive explicit dependency readiness and exact structured duplicates;
- project canonical state to Workflowy/other views;
- detect anomalies and enqueue semantic-review events.

Must not:
- infer intent or meaning from free text/code;
- decide semantic equivalence, obsolescence, scope, priority, merge/split, or acceptance changes;
- encode semantic judgment as heuristics merely to avoid AI.

Input: structured DB/runtime/Git/integration/tool facts.
Output: deterministic mutation/receipt, projection, anomaly/event, or no-op.

## AI semantic executor
May:
- decide whether work is obsolete, already satisfied, duplicated or overlapping;
- merge/split/rewrite pending work items;
- revise priority/order, dependencies, scope and acceptance criteria;
- interpret repository evidence when task meaning cannot be resolved mechanically;
- triage Inbox items semantically and decide promotion/merge/discard;
- choose the smallest roadmap change that best reflects current reality.

Must not:
- manually redo lifecycle sync/reconciliation already owned by scripts;
- poll CI/processes or spend model turns waiting;
- directly edit canonical DB/generated roadmap state;
- execute the application tasks while performing a roadmap-only reorganization;
- mutate semantics/metadata of running work unless the existing lifecycle contract explicitly permits it.

Input: canonical C2 snapshot + already-known evidence; inspect a target repo only when semantic judgment requires it.
Output: minimal structured mutation proposal(s) through the single writer, then writer acknowledgment.

## Writer
The writer validates identity/schema/authority, enforces invariants and running-task immutability,
applies accepted mutations atomically/idempotently, records evidence/audit and returns the canonical receipt.
It never invents semantic decisions or silently repairs an invalid AI proposal.

## Semantic reorganization flow
0. Apply [the common executor contract](C2_EXECUTOR_CONTRACT.md) before semantic work.
1. Let deterministic C2 mechanisms reconcile factual state first; do not reproduce that work with model reasoning.
2. Read canonical active work and existing structured evidence.
3. For each item needing semantic judgment, inspect only the minimum relevant repo/context.
4. Decide obsolete/satisfied/duplicate/merge/split/reprioritize/dependency/acceptance changes.
5. Submit only those semantic mutations through the writer.
6. Verify writer receipts/projection and stop. Do not start executing the reorganized tasks.

## Inbox promotion contract

Inbox records raw observations and evidence. `work_items` records canonical roadmap work decisions. Their provenance is many-to-many in `issue_work_item_links`; the old scalar Inbox columns remain for compatibility. Capture does not create an execution lifecycle, and pending observations do not gate roadmap scheduling or unrelated reconciliation.

The independent `tools/c2_inbox_codex_executor.py --db <snapshot> --batch 25` runner reads up to 25 ordered pending observations and submits one fenced `c2_reconcile_issue_batch` operation through `tools/c2_control.py`. The operation takes a stable `batch_id`, `triaged_by`, `decisions` (`issue_id`, concrete `reason`, `work_item_ids`), and optional `new_items` with local aliases referenced as `@alias`. An empty target list records no work; multiple targets split an observation; multiple observations may share one target. Cluster and deduplicate within this batch. Ambiguous observations may remain pending. The writer applies the whole batch atomically and replays an identical batch without making duplicate work items. There is no required global post-drain pass or automatic triage work item.

Legacy `promote_issue` and `discard_issue` remain available for compatibility. Every disposition needs a concrete `reason` and `triaged_by`; the single writer owns the state transition and evidence.

For `promote_issue`, choose `matched_work_item_id` from canonical work-item evidence, or leave it empty when no existing item matches:

| Match at writer application | Canonical effect |
| --- | --- |
| Pending, running, waiting, blocked, needs_fix, or unknown | Attach the observation to that work item. Preserve its lifecycle and execution metadata. |
| Completed | Create a new regression work item with a `regression_of` relation to the completed item; never reopen or discard the completed history. |
| Cancelled, superseded, or waived | Create a new work item. The old terminal item is evidence, not an active owner. |
| No match | Create a new work item from the observation. |

For a newly created item, the triager supplies a useful title/objective and the explicit parent, dependencies, tags, order, executor policy, project and repository when verified. The writer may inherit fields from a matched item and records `source:issue-inbox`; it does not infer semantic priority or dependencies. Review priority relative to the current queue and dependencies in both directions before promotion. If the match is active, promotion adds evidence only; use a separate allowed roadmap mutation for any metadata change. `discard_issue` is for an irrelevant or obsolete observation with a concrete reason; a fresh observation of completed work requires regression promotion, and a relevant active match requires promotion into that item.

## Standard prompt
Use this prompt when the goal is to **update + optimize the C2 roadmap**, not execute its tasks:

> Riorganizza semanticamente la roadmap C2.
>
> Applica il contratto canonico `C2_SEMANTIC_REORGANIZATION.md`.
> Lascia a script/control plane tutte le operazioni deterministiche: lifecycle, sync, receipt, run/executor binding, dipendenze esplicite, CI/PR/merge, reconciliation e proiezioni. Non rifarle manualmente con ragionamento.
>
> Tu occupati solo delle decisioni che richiedono giudizio semantico. Parti dallo stato canonico già riconciliato e, per ogni work item attivo, consulta il repo/contesto pertinente solo quanto serve a stabilire se il task è ancora attuale, già soddisfatto, duplicato/sovrapposto, mal definito o prioritizzato male.
>
> Ottimizza la roadmap quando giustificato: chiudi/supersedi task semanticamente obsoleti o già soddisfatti; accorpa duplicati/sovrapposti; dividi task troppo eterogenei; correggi scope/acceptance/dependencies; riordina le priorità per minimizzare tempo, rischio, conflitti e lavoro duplicato.
>
> Non eseguire i task applicativi della roadmap. Non modificare task running oltre quanto consente il lifecycle contract. Non fare polling o verifiche meccaniche che C2 può fare senza AI. Non creare euristiche per sostituire giudizi semantici.
>
> Applica ogni cambiamento canonico soltanto tramite il single writer C2 e verifica le receipt. Se durante il ragionamento emerge incidentalmente un bug/collo di bottiglia/miglioria, invia subito solo la descrizione alla C2 Inbox senza ricerca, deduplica o triage e continua.
>
> Fermati quando la roadmap rappresenta correttamente lo stato reale ed è semanticamente ottimizzata. Riporta solo: cambiamenti semantici applicati, elementi lasciati invariati perché ancora validi, eventuali blocker reali.
