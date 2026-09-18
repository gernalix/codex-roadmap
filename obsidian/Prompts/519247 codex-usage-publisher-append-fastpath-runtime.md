---
prompt_id: 519247
status: completed
project_id: 8
model: GPT-5.6 Luna
reasoning: low
tags:
  - single-writer-e2e
  - single-writer-enforced
  - roadmap/prompt
  - roadmap/status/completed
  - roadmap/project/fedora
---

# 519247 · Attivare il fast-path del publisher Codex

- **Stato:** completed
- **Progetto:** [[../Projects/fedora|Fedora]]
- **Prompt:** [[../../completed/codex-usage-publisher-append-fastpath-runtime|Apri prompt]]
- **Primo lancio:** 2026-09-18T22:45:09Z
- **Ultimo lancio:** 2026-09-18T22:45:09Z
- **Ultimo esito:** PASS
- **Analizzato da ChatGPT:** sì
- **Codice modificato da ChatGPT:** sì (2 interventi)
- **Fix:** —
- **Dipende da:** —
- **Sblocca:** —
- **Padri/precedenti:** [[817264 codex-usage-publisher-autonomous-runtime-closure|817264]]
- **Figli/follow-up:** —
- **Chat Codex:** Nuova chat

## Spiegazione

Installa sul PC l’ottimizzazione che evita di rileggere tutte le vecchie sessioni Codex quando la sessione corrente aggiunge solo eventi intermedi, e verifica che il salvataggio veloce funzioni davvero.

## Esecuzioni

| Inizio | Fine | Esito | Durata s | Modello | Reasoning | Tool-call | Token totali |
| --- | --- | --- | ---: | --- | --- | ---: | ---: |
| 2026-09-18T22:45:09Z | 2026-09-18T22:46:50Z | PASS | 100.888 | gpt-5.6-luna | low | 12 | 38579 |

## Analisi ChatGPT

- 2026-09-18T22:50:32Z · colli di bottiglia: sì · fix: — · PASS con 38.579 token totali, 98,38% cached: 618 input non-cached, 329 output e 242 reasoning. Luna low era appropriato. Rispetto a 817264: input totale -72,4%, tool-call 57→12 (-78,9%), durata 753,3→100,9 s (-86,6%). Il fast-path è riuscito: run1 one-shot reconcile 52,857 s, run2 noop_unchanged_sources/nonterminal_append 0,42 s (~126x più rapido). Sprechi residui: una lettura preventiva molto ampia di MegaVault/MEMORY non necessaria e tool-call extra per un comando lungo >30 s il cui output è stato perso dal wrapper; nessun nuovo bug funzionale richiede follow-up Codex.

## Modifiche di codice ChatGPT

- 2026-09-18T22:50:32Z · `gernalix/codex-roadmap` · prompt-efficiency · commit `6e29a75cfc8caa1c7ed93c28d310b0510157fdb1` · MegaVault=FAST con starting point completo non deve caricare preventivamente MegaVault/MEMORY; i comandi lunghi vanno attesi sullo stesso processo/sessione invece di polling/proxy.
- 2026-09-18T22:50:32Z · `gernalix/codex-roadmap` · prompt-efficiency · commit `9a0325ee8ae322b05841f90ff5752dd6d44ba9d2` · README allineato: FAST consulta solo fatti specifici mancanti e non dumpa contesto preventivo.
