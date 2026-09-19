---
prompt_id: 825147
status: pending
project_id: 49
model: GPT-5.6 Terra
reasoning: medium
tags:
  - roadmap/prompt
  - roadmap/status/pending
  - roadmap/project/personalhub
---

# 825147 · Chiudere i residui zombie PersonalHub sul single writer corrente

- **Stato:** pending
- **Progetto:** [[../Projects/personalhub|PersonalHub]]
- **Prompt:** [[../../prompts/personalhub-zombie-function-cleanup-single-writer-v2|Apri prompt]]
- **Primo lancio:** —
- **Ultimo lancio:** —
- **Ultimo esito:** —
- **Analizzato da ChatGPT:** no
- **Codice modificato da ChatGPT:** no (0 interventi)
- **Fix:** —
- **Dipende da:** [[914263 personalhub-schema-persistence-all-tables-p0|914263]]
- **Sblocca:** [[462279 personalhub-health-canonical-e2e-v4|462279]]
- **Padri/precedenti:** [[793678 personalhub-zombie-function-cleanup-closure|793678]]
- **Figli/follow-up:** —
- **Chat Codex:** Nuova chat Codex; usare PR #20 solo come sorgente del lavoro già fatto

## Spiegazione

Chiude la pulizia delle vecchie funzioni standalone già raccolte nella PR #20, ma la riconcilia sul main risultante dal P0 senza sovrascriverne i fix. Serve a evitare che il vecchio branch e le istruzioni di merge diretto confliggano con il nuovo single writer per-repository. Richiede Codex per compilazione, CI e integrazione locale controllata.

## Esecuzioni

| Inizio | Fine | Esito | Durata s | Modello | Reasoning | Tool-call | Token totali |
| --- | --- | --- | ---: | --- | --- | ---: | ---: |
| — | — | — | — | — | — | — | — |

## Analisi ChatGPT

- Non ancora analizzato.

## Modifiche di codice ChatGPT

- Nessuna modifica di codice registrata.
