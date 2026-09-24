---
prompt_id: 697920
status: blocked
project_id: 92
model: GPT-6 Sol
reasoning: medium
tags:
  - roadmap/prompt
  - roadmap/status/blocked
  - roadmap/project/prompt-infrastructure
---

# 697920 · Rendere ChatGPTExporter resiliente e affidabile

- **Stato:** blocked
- **Progetto:** [[../Projects/prompt-infrastructure|Prompt infrastructure]]
- **Prompt:** [[../../falliti/chatgpt-exporter-resilience-hardening-v1|Apri prompt]]
- **Primo lancio:** 2026-09-24T02:12:33Z
- **Ultimo lancio:** 2026-09-24T02:12:33Z
- **Ultimo esito:** BLOCKED
- **Analizzato da ChatGPT:** sì
- **Codice modificato da ChatGPT:** no (0 interventi)
- **Fix:** —
- **Dipende da:** —
- **Sblocca:** —
- **Padri/precedenti:** [[199166 openai-vs-chatgpt-exporter-data-completeness-v1|199166]]
- **Figli/follow-up:** [[812553 chatgpt-exporter-resilience-canonical-primary-repo-recovery-v1|812553]]
- **Chat Codex:** Nuova chat Codex. Riusa come evidenza i report di 199166, non la sua sessione lunga.

## Spiegazione

Rende il collector ChatGPT Web capace di ritentare e riprendere automaticamente errori di chat e allegati, distingue ciò che è davvero irrecuperabile, evita falsi completamenti e mantiene l’export OpenAI solo come controllo/backfill occasionale.

## Esecuzioni

| Inizio | Fine | Esito | Durata s | Modello | Reasoning | Tool-call | Token totali |
| --- | --- | --- | ---: | --- | --- | ---: | ---: |
| 2026-09-24T02:12:33Z | 2026-09-24T02:14:11Z | BLOCKED | 97.768 | gpt-6-sol | medium | 6 | 47974 |

## Analisi ChatGPT

- 2026-09-24T02:16:06Z · colli di bottiglia: sì · fix: — · {"blocker":"il claim canonico ha fallito perché il campo repo contiene `gernalix/prompt-history + ChatGPTExporter fork`, che non identifica un worktree canonico; inoltre `PROJECT_ID=92` risolve a `github-autosync`. Serve correggere i metadati in un nuovo prompt canonico prima di iniziare il lavoro.","next_action":"Use the concrete blocker above for the smallest corrective action.","outcome":"BLOCKED","prompt_id":"697920","report_ref":"codex-usage:450d3fc0f45eaf965b268c48:1494a3333a28c4fe","schema":"codex-roadmap.fix-packet.v1","work_state":{}}

## Modifiche di codice ChatGPT

- Nessuna modifica di codice registrata.
