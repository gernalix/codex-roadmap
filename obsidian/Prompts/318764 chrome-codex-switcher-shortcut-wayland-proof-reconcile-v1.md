---
prompt_id: 318764
status: pending
project_id: 96
model: GPT-5.6 Luna
reasoning: low
tags:
  - chrome-codex-switcher
  - fix
  - gnome
  - shortcut
  - roadmap/prompt
  - roadmap/status/pending
  - roadmap/project/facilitatori-di-prompt
---

# 318764 · Chiudere il blocker di prova della shortcut GNOME

- **Stato:** pending
- **Progetto:** [[../Projects/facilitatori-di-prompt|Facilitatori di prompt]]
- **Prompt:** [[../../prompts/chrome-codex-switcher-shortcut-wayland-proof-reconcile-v1|Apri prompt]]
- **Primo lancio:** —
- **Ultimo lancio:** —
- **Ultimo esito:** —
- **Analizzato da ChatGPT:** no
- **Codice modificato da ChatGPT:** no (0 interventi)
- **Fix:** —
- **Dipende da:** —
- **Sblocca:** —
- **Padri/precedenti:** [[604812 chrome-codex-switcher-gnome-global-search-shortcut-rpm-fix-v2|604812]]
- **Figli/follow-up:** —
- **Chat Codex:** Stessa chat/contesto Fedora di 604812; verifica stretta, nessun audit

## Spiegazione

604812 ha già prodotto e mergiato il fix della shortcut in PR #22; il solo blocker residuo è l'impossibilità di sintetizzare una pressione fisica Alt+Shift+S sotto Wayland. Il correttivo deve sostituire quel gate non automatizzabile con una prova deterministica separata di registrazione binding + launcher/dashboard e riconciliare il parent senza rifare il lavoro.

## Esecuzioni

| Inizio | Fine | Esito | Durata s | Modello | Reasoning | Tool-call | Token totali |
| --- | --- | --- | ---: | --- | --- | ---: | ---: |
| — | — | — | — | — | — | — | — |

## Analisi ChatGPT

- Non ancora analizzato.

## Modifiche di codice ChatGPT

- Nessuna modifica di codice registrata.
