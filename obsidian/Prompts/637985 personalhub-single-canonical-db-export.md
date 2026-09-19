---
prompt_id: 637985
status: pending
project_id: 49
model: GPT-5.6 Terra
reasoning: medium
tags:
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

Fa sì che PersonalHub tenga un solo database esportato invece di accumulare decine di copie. Serve perché 38 backup locali occupavano circa 609 MB mentre il DB vero era solo ~15 MB. Richiede Codex per provarlo sul Pixel e integrare in sicurezza la PR già preparata.

## Esecuzioni

| Inizio | Fine | Esito | Durata s | Modello | Reasoning | Tool-call | Token totali |
| --- | --- | --- | ---: | --- | --- | ---: | ---: |
| — | — | — | — | — | — | — | — |

## Analisi ChatGPT

- Non ancora analizzato.

## Modifiche di codice ChatGPT

- Nessuna modifica di codice registrata.
