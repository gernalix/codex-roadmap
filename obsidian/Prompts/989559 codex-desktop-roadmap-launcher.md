---
prompt_id: 989559
status: blocked
project_id: 23
model: gpt-5.6-terra
reasoning: medium
tags:
  - roadmap/prompt
  - roadmap/status/blocked
  - roadmap/project/facilitatori-di-prompt
---

# 989559 · Automatizza Avvia verso Codex Desktop

- **Stato:** blocked
- **Progetto:** [[../Projects/facilitatori-di-prompt|Facilitatori di prompt]]
- **Prompt:** [[../../falliti/codex-desktop-roadmap-launcher|Apri prompt]]
- **Primo lancio:** 2026-09-22T01:55:13Z
- **Ultimo lancio:** 2026-09-22T01:55:13Z
- **Ultimo esito:** BLOCKED
- **Analizzato da ChatGPT:** sì
- **Codice modificato da ChatGPT:** no (0 interventi)
- **Fix:** —
- **Dipende da:** [[472615 chrome-codex-switcher-notes-reboot-persistence-fix-v1|472615]]
- **Sblocca:** —
- **Padri/precedenti:** —
- **Figli/follow-up:** —
- **Chat Codex:** new chat

## Spiegazione

Quando premi Avvia nella dashboard, apre il prompt direttamente in ChatGPT Desktop/Codex nel posto giusto e prepara anche modello e livello di ragionamento. Così non devi impostare tutto a mano.

## Esecuzioni

| Inizio | Fine | Esito | Durata s | Modello | Reasoning | Tool-call | Token totali |
| --- | --- | --- | ---: | --- | --- | ---: | ---: |
| 2026-09-22T01:55:13Z | 2026-09-22T01:55:22Z | BLOCKED | 8.873 | gpt-5.6-terra | medium | 1 | 31618 |

## Analisi ChatGPT

- 2026-09-22T01:58:44Z · colli di bottiglia: sì · fix: — · {"blocker":"`roadmap_start.py --prompt-id 989559` ha fallito: `roadmap_pull_blocked:branch_mismatch:expected=main:actual=master`. Senza claim/worktree autoritativo, stop.","next_action":"Use the concrete blocker above for the smallest corrective action.","outcome":"BLOCKED","prompt_id":"989559","report_ref":"codex-usage:f478e0f2cefc2463e70afb25:22e0e8ffbb2c4e66","schema":"codex-roadmap.fix-packet.v1","work_state":{}}

## Modifiche di codice ChatGPT

- Nessuna modifica di codice registrata.
