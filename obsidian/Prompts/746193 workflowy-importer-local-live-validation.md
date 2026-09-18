---
prompt_id: 746193
status: blocked
project_id: 23
model: GPT-5.6 Terra
reasoning: medium
tags:
  - project/fedora-workflowy
  - roadmap
  - roadmap/prompt
  - roadmap/status/blocked
  - roadmap/project/fedora-workflowy
---

# 746193 · Provare davvero l’importatore Workflowy

- **Stato:** blocked
- **Progetto:** [[../Projects/fedora-workflowy|Fedora / Workflowy]]
- **Prompt:** [[../../falliti/workflowy-importer-local-live-validation|Apri prompt]]
- **Primo lancio:** 2026-09-18T19:11:43Z
- **Ultimo lancio:** 2026-09-18T19:11:43Z
- **Ultimo esito:** BLOCKED
- **Analizzato da ChatGPT:** sì
- **Fix:** 693572
- **Dipende da:** —
- **Sblocca:** —
- **Padri/precedenti:** —
- **Figli/follow-up:** [[693572 workflowy-importer-live-smoke-secret-file|693572]]
- **Chat Codex:** Nuova chat

## Spiegazione

Prova l’importatore Workflowy sul PC con dati finti e controlla che non crei duplicati o lasci residui.

## Esecuzioni

| Inizio | Fine | Esito | Durata s | Modello | Reasoning | Tool-call | Token totali |
| --- | --- | --- | ---: | --- | --- | ---: | ---: |
| 2026-09-18T19:11:43Z | 2026-09-18T19:13:12Z | BLOCKED | 88.682 | gpt-5.6-terra | medium | 16 | 40690 |

## Analisi ChatGPT

- 2026-09-18T19:34:30Z · colli di bottiglia: sì · fix: 693572 · Host gates e dry-run PASS. Il run è stato BLOCKED solo dalla chiave Workflowy assente; 16 tool-call includevano discovery segreti e cleanup evitabili. Il follow-up usa il file segreto canonico e un unico smoke helper.
