---
prompt_id: 914263
status: running
project_id: 49
model: GPT-5.6 Sol
reasoning: medium
tags:
  - roadmap/prompt
  - roadmap/status/running
  - roadmap/project/personalhub
---

# 914263 · P0 — Verificare e correggere il salvataggio di ogni tabella PersonalHub su 3 device

- **Stato:** running
- **Progetto:** [[../Projects/personalhub|PersonalHub]]
- **Prompt:** [[../../prompts/personalhub-schema-persistence-all-tables-p0|Apri prompt]]
- **Primo lancio:** —
- **Ultimo lancio:** —
- **Ultimo esito:** —
- **Analizzato da ChatGPT:** no
- **Codice modificato da ChatGPT:** no (0 interventi)
- **Fix:** —
- **Dipende da:** —
- **Sblocca:** [[618338 personalhub-pixel-sqlite-bloat-remediation|618338]], [[825147 personalhub-zombie-function-cleanup-single-writer-v2|825147]]
- **Padri/precedenti:** —
- **Figli/follow-up:** —
- **Chat Codex:** Nuova chat Codex; P0 bloccante — eseguire prima degli altri task PersonalHub

## Spiegazione

v56 mostra regressioni gravi di persistenza/UI: Events Timer non salvabili/modificabili, Substances con crash su un pulsante e People non affidabile. Costruisce una suite schema-driven che copre ogni tabella app-owned e ogni tipo di entry editabile, corregge tutti i failure e valida la stessa matrice su emulatore, TCL e Pixel senza perdere dati reali.

## Esecuzioni

| Inizio | Fine | Esito | Durata s | Modello | Reasoning | Tool-call | Token totali |
| --- | --- | --- | ---: | --- | --- | ---: | ---: |
| — | — | — | — | — | — | — | — |

## Analisi ChatGPT

- Non ancora analizzato.

## Modifiche di codice ChatGPT

- Nessuna modifica di codice registrata.
