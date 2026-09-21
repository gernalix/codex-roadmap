---
prompt_id: 604812
status: blocked
project_id: —
model: GPT-5.6 Terra
reasoning: medium
tags:
  - chrome-codex-switcher
  - chrome-rpm
  - gnome
  - runtime-fix
  - shortcut
  - roadmap/prompt
  - roadmap/status/blocked
  - roadmap/project/facilitatori-di-prompt
---

# 604812 · Fix GNOME global search shortcut on Chrome RPM

- **Stato:** blocked
- **Progetto:** [[../Projects/facilitatori-di-prompt|Facilitatori di prompt]]
- **Prompt:** [[../../falliti/chrome-codex-switcher-gnome-global-search-shortcut-rpm-fix-v2|Apri prompt]]
- **Primo lancio:** 2026-09-21T21:50:23Z
- **Ultimo lancio:** 2026-09-21T21:50:23Z
- **Ultimo esito:** BLOCKED
- **Analizzato da ChatGPT:** sì
- **Codice modificato da ChatGPT:** no (0 interventi)
- **Fix:** —
- **Dipende da:** —
- **Sblocca:** —
- **Padri/precedenti:** [[917403 chrome-codex-switcher-gnome-global-search-shortcut-runtime-fix-v1|917403]]
- **Figli/follow-up:** [[318764 chrome-codex-switcher-shortcut-wayland-proof-reconcile-v1|318764]], [[741928 chrome-codex-switcher-full-runtime-reliability-v1|741928]]
- **Chat Codex:** —

## Spiegazione

Chrome Flatpak è stato rimosso e Chrome RPM con lo switcher funziona: il task deve isolare e correggere esclusivamente il percorso della shortcut globale GNOME verso la dashboard.

## Esecuzioni

| Inizio | Fine | Esito | Durata s | Modello | Reasoning | Tool-call | Token totali |
| --- | --- | --- | ---: | --- | --- | ---: | ---: |
| 2026-09-21T21:50:23Z | 2026-09-21T21:56:19Z | BLOCKED | 355.822 | gpt-5.6-terra | medium | 41 | 136377 |

## Analisi ChatGPT

- 2026-09-21T21:57:37Z · colli di bottiglia: sì · fix: — · {"blocker":"No privileged Wayland input injector/native UI control to prove Alt+Shift+S.","next_action":"Use the concrete blocker above for the smallest corrective action.","outcome":"BLOCKED","prompt_id":"604812","report_ref":"codex-usage:0ee05dcbfd64f034c0bc1b85:1bc5b94a6bd92292","schema":"codex-roadmap.fix-packet.v1","work_state":{"commit":"beca7f9"}}

## Modifiche di codice ChatGPT

- Nessuna modifica di codice registrata.
