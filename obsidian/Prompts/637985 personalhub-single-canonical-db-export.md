---
prompt_id: 637985
status: pending
project_id: 49
model: GPT-5.6 Terra
reasoning: medium
tags:
  - pr-21
  - single-canonical-db
  - roadmap/prompt
  - roadmap/status/pending
  - roadmap/project/personalhub
---

# 637985 · Mantenere un solo DB auto-esportato PersonalHub

- **Stato:** pending
- **Progetto:** [[../Projects/personalhub|PersonalHub]]
- **Prompt:** [[../../prompts/personalhub-single-canonical-db-export|Apri prompt]]
- **Primo lancio:** —
- **Ultimo lancio:** —
- **Ultimo esito:** —
- **Analizzato da ChatGPT:** no
- **Codice modificato da ChatGPT:** no (0 interventi)
- **Fix:** —
- **Dipende da:** [[914263 personalhub-schema-persistence-all-tables-p0|914263]]
- **Sblocca:** —
- **Padri/precedenti:** [[618338 personalhub-pixel-sqlite-bloat-remediation|618338]]
- **Figli/follow-up:** —
- **Chat Codex:** Nuova chat dopo 914263

## Spiegazione

Fa sì che a regime esista un solo `personalhub.db` auto-esportato: durante la sostituzione può usare solo file temporanei che vengono recuperati o eliminati automaticamente dopo un crash. Elimina i 38 vecchi backup locali e i rollback di startup ormai conclusi, ma conserva le copie necessarie mentre un import o una migrazione è ancora in corso. Richiede Codex per verificare tutto sul Pixel e integrare in sicurezza la PR #21.

## Esecuzioni

| Inizio | Fine | Esito | Durata s | Modello | Reasoning | Tool-call | Token totali |
| --- | --- | --- | ---: | --- | --- | ---: | ---: |
| — | — | — | — | — | — | — | — |

## Analisi ChatGPT

- Non ancora analizzato.

## Modifiche di codice ChatGPT

- Nessuna modifica di codice registrata.
