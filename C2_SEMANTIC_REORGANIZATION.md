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
0. Ensure this executor has an `executor_started` receipt before semantic work. C2-managed runs do this automatically; a manual executor uses `tools/c2_executor_start.py` with the existing task identity.
1. Let deterministic C2 mechanisms reconcile factual state first; do not reproduce that work with model reasoning.
2. Read canonical active work and existing structured evidence.
3. For each item needing semantic judgment, inspect only the minimum relevant repo/context.
4. Decide obsolete/satisfied/duplicate/merge/split/reprioritize/dependency/acceptance changes.
5. Submit only those semantic mutations through the writer.
6. Verify writer receipts/projection and stop. Do not start executing the reorganized tasks.

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
