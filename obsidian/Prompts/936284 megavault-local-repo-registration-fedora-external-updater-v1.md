---
prompt_id: 936284
status: running
project_id: 23
model: GPT-5.6 Terra
reasoning: medium
tags:
  - fedora-external-updater
  - fix
  - local-repo
  - megavault
  - roadmap/prompt
  - roadmap/status/running
  - roadmap/project/megavault
---

# 936284 · Aggiungere il contratto MegaVault per repo local-only e chiudere 417592

- **Stato:** running
- **Progetto:** [[../Projects/megavault|MegaVault]]
- **Prompt:** [[../../prompts/megavault-local-repo-registration-fedora-external-updater-v1|Apri prompt]]
- **Primo lancio:** —
- **Ultimo lancio:** —
- **Ultimo esito:** —
- **Analizzato da ChatGPT:** no
- **Codice modificato da ChatGPT:** no (0 interventi)
- **Fix:** —
- **Dipende da:** —
- **Sblocca:** —
- **Padri/precedenti:** [[417592 fedora-external-updater-megavault-git-closure-v2|417592]]
- **Figli/follow-up:** —
- **Chat Codex:** Stessa chat di 417592; correzione diretta del blocker, riusa lo stato locale già verificato

## Spiegazione

417592 è BLOCKED perché MegaVault espone solo la registrazione GitHub e non ha un contratto canonico/idempotente per un checkout Git local-only. Aggiungi il minimo supporto generico derivato dal worktree, usalo una volta per fedora-external-updater e poi persisti gli hunk pip_user già implementati, senza creare remote né rifare il lavoro applicativo.

## Esecuzioni

| Inizio | Fine | Esito | Durata s | Modello | Reasoning | Tool-call | Token totali |
| --- | --- | --- | ---: | --- | --- | ---: | ---: |
| — | — | — | — | — | — | — | — |

## Analisi ChatGPT

- Non ancora analizzato.

## Modifiche di codice ChatGPT

- Nessuna modifica di codice registrata.
