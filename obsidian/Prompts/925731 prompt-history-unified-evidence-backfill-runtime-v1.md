---
prompt_id: 925731
status: pending
project_id: 92
model: GPT-5.5
reasoning: medium
tags:
  - backfill
  - chatgpt
  - codex-usage
  - evidence-store
  - prompt-history
  - roadmap/prompt
  - roadmap/status/pending
  - roadmap/project/prompt-infrastructure
---

# 925731 · Attivare storico unificato ChatGPT e Codex

- **Stato:** pending
- **Progetto:** [[../Projects/prompt-infrastructure|Prompt infrastructure]]
- **Prompt:** [[../../prompts/prompt-history-unified-evidence-backfill-runtime-v1|Apri prompt]]
- **Primo lancio:** —
- **Ultimo lancio:** —
- **Ultimo esito:** —
- **Analizzato da ChatGPT:** sì
- **Codice modificato da ChatGPT:** sì (1 interventi)
- **Fix:** —
- **Dipende da:** [[621471 post-404936-runtime-validation|621471]], [[748203 codex-usage-session-readback-reconcile-v1|748203]]
- **Sblocca:** —
- **Padri/precedenti:** —
- **Figli/follow-up:** —
- **Chat Codex:** Nuova chat Codex; attivazione/backfill Fedora del codice già implementato da ChatGPT

## Spiegazione

AUDIT 2026-09-22: gernalix/prompt-history/main corrisponde all'implementazione 95667890 e contiene schema, adapter ChatGPT/Codex/roadmap, FTS5, linker, analytics/recommender e test. Aspetta solo 621471; poi serve esclusivamente backfill/attivazione Fedora, MegaVault e timer/sync. Modello ridotto a GPT-5.5 medium.

## Esecuzioni

| Inizio | Fine | Esito | Durata s | Modello | Reasoning | Tool-call | Token totali |
| --- | --- | --- | ---: | --- | --- | ---: | ---: |
| — | — | — | — | — | — | — | — |

## Analisi ChatGPT

- 2026-09-21T23:17:20Z · colli di bottiglia: no · fix: — · Remote implementation already completed directly on gernalix/prompt-history/main: normalized rebuildable SQLite evidence store, roadmap/codex-usage/ChatGPT adapters, deterministic PROMPT_ID linking, FTS5 search, analytics/recommender, tests and CI. Remaining work is Fedora-local activation/backfill/runtime integration only; no redesign or reimplementation of the remote base is needed.

## Modifiche di codice ChatGPT

- 2026-09-21T23:17:20Z · `gernalix/prompt-history` · implementation · commit `95667890f0aebb271c755b9f99488f978840328e` · Implemented the remote base end-to-end on main: schema/provenance/idempotency, roadmap and codex-usage ingestion, ChatGPT export ingestion, deterministic ChatGPT↔Codex PROMPT_ID/parent linking, resolved_by derivation, FTS5, analytics queries, bounded recommender, tests and CI.
