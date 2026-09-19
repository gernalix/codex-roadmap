---
prompt_id: 637985
status: running
project_id: 49
model: GPT-5.6 Terra
reasoning: medium
tags:
  - pr-21
  - single-canonical-db
  - roadmap/prompt
  - roadmap/status/running
  - roadmap/project/personalhub
---

# 637985 · Mantenere un solo DB auto-esportato PersonalHub

- **Stato:** running
- **Progetto:** [[../Projects/personalhub|PersonalHub]]
- **Prompt:** [[../../prompts/personalhub-single-canonical-db-export|Apri prompt]]
- **Primo lancio:** 2026-09-19T14:04:52Z
- **Ultimo lancio:** 2026-09-19T14:04:52Z
- **Ultimo esito:** UNKNOWN
- **Analizzato da ChatGPT:** no
- **Codice modificato da ChatGPT:** no (0 interventi)
- **Fix:** —
- **Dipende da:** [[914263 personalhub-schema-persistence-all-tables-p0|914263]]
- **Sblocca:** [[462279 personalhub-health-canonical-e2e-v4|462279]]
- **Padri/precedenti:** [[618338 personalhub-pixel-sqlite-bloat-remediation|618338]]
- **Figli/follow-up:** —
- **Chat Codex:** Nuova chat dopo 914263

## Spiegazione

Fa sì che a regime esista un solo `personalhub.db` auto-esportato: durante la sostituzione può usare solo file temporanei che vengono recuperati o eliminati automaticamente dopo un crash. Elimina i 38 vecchi backup locali e i rollback di startup ormai conclusi, ma conserva le copie necessarie mentre un import o una migrazione è ancora in corso. Richiede Codex per verificare tutto sul Pixel e integrare in sicurezza la PR #21.

## Esecuzioni

| Inizio | Fine | Esito | Durata s | Modello | Reasoning | Tool-call | Token totali |
| --- | --- | --- | ---: | --- | --- | ---: | ---: |
| 2026-09-19T14:04:52Z | 2026-09-19T14:35:46Z | UNKNOWN | 1854.529 | gpt-5.6-terra | medium | 86 | 124157 |

## Analisi ChatGPT

- Non ancora analizzato.

## Modifiche di codice ChatGPT

- Nessuna modifica di codice registrata.
