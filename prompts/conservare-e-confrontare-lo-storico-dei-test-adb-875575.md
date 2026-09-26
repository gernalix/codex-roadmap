PROMPT_ID=875575

# Goal
Aggiungere a C2 un registro strutturato e rapidamente interrogabile dei test Android/ADB, con risultati, contesto di build/device e metriche numeriche storiche; integrare PersonalHub Macrobenchmark per conservare e confrontare nel tempo i tempi di avvio di app e moduli.

# Canonical starting point
- C2 work item: wi:a299a4c1a72049b88f594587dc786768
- Repository: https://github.com/gernalix/codex-roadmap
- The work item scope and acceptance below are authoritative. Inspect only files needed to satisfy them.
- Use the assigned isolated worktree and the repository single-writer/integration path. Do not edit canonical branches directly.
- Do not broaden scope into unrelated cleanup, refactors or audits.
- Existing verified evidence:
  - codex-roadmap main a5873827 c2_scheduler.configure_auto requires structured execution.worktree and materialized prompt/exact metadata for Codex; this intake has no work_item_execution_specs row.
  - codex-roadmap main a5873827 lacks structured ADB test metrics/ingest/query; PersonalHub main c9a574cf contains PersonalHubShortcutBenchmarks.kt.

# First bounded action
Implement C2 metric schema and ingest/query first; coordinate PH benchmark adapter with PH owner.

# Acceptance
- Ogni run registrata conserva timestamp, progetto/repo, commit/build, device, tipo test, outcome e riferimenti all'evidenza grezza.
- Le metriche numeriche sono normalizzate e interrogabili come serie storica per progetto, device, scenario e metrica.
- PersonalHub Macrobenchmark può importare i tempi di cold startup per modulo senza parsing manuale.
- Esistono query/CLI concise per latest, history e confronto con il run precedente.
- Schema e ingestione sono idempotenti e coperti da test; nessun DB live viene modificato fuori dal writer C2.

# Execution rules
- Fix only failures necessary for this goal; preserve unrelated local/runtime state.
- Use targeted tests first and widen only if evidence requires it.
- On incidental C2 bugs/bottlenecks, capture only the description to the C2 Inbox and continue.
- Stop immediately when acceptance is verified; do not wait on CI/merge in a model turn.
