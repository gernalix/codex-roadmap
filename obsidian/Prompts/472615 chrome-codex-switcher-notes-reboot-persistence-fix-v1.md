---
prompt_id: 472615
status: pending
project_id: 96
model: GPT-5.6 Terra
reasoning: medium
tags:
  - chrome-codex-switcher
  - notes
  - persistence
  - reboot
  - startup-race
  - roadmap/prompt
  - roadmap/status/pending
  - roadmap/project/facilitatori-di-prompt
---

# 472615 · Ripristinare le note dopo reboot

- **Stato:** pending
- **Progetto:** [[../Projects/facilitatori-di-prompt|Facilitatori di prompt]]
- **Prompt:** [[../../prompts/chrome-codex-switcher-notes-reboot-persistence-fix-v1|Apri prompt]]
- **Primo lancio:** —
- **Ultimo lancio:** —
- **Ultimo esito:** —
- **Analizzato da ChatGPT:** no
- **Codice modificato da ChatGPT:** no (0 interventi)
- **Fix:** —
- **Dipende da:** —
- **Sblocca:** [[989559 codex-desktop-roadmap-launcher|989559]]
- **Padri/precedenti:** [[741928 chrome-codex-switcher-full-runtime-reliability-v1|741928]]
- **Figli/follow-up:** —
- **Chat Codex:** Nuova chat Codex; regressione post-741928 sul Fedora reale

## Spiegazione

Dopo un reboot tutte le note risultano vuote: verifica se il DB è intatto e corregge la reidratazione/startup race o il remapping dei context senza rischiare i dati reali.

## Esecuzioni

| Inizio | Fine | Esito | Durata s | Modello | Reasoning | Tool-call | Token totali |
| --- | --- | --- | ---: | --- | --- | ---: | ---: |
| — | — | — | — | — | — | — | — |

## Analisi ChatGPT

- Non ancora analizzato.

## Modifiche di codice ChatGPT

- Nessuna modifica di codice registrata.
