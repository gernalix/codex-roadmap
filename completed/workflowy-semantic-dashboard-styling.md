PROMPT_ID=764382
PROJECT=Facilitatori di prompt
MODEL=GPT-5.6 Luna
REASONING=low
MEGAVAULT=FAST
REPO=gernalix/chrome-codex-switcher

GOAL
Aggiungere alla dashboard Workflowy un livello visuale leggero e semantico per attirare l'attenzione, senza modificare la fonte canonica.

ACCEPTANCE
- Il content script Workflowy colora semanticamente i segnali generati dalla dashboard: rosso problemi/fix, arancione link mancanti, blu running, viola integration, verde ready/done, grigio metadati.
- I prompt problematici risultano visivamente più evidenti; link di azione principali in grassetto.
- Tema leggibile sia chiaro sia scuro.
- Solo CSS/DOM enhancement della dashboard; nessuna dipendenza da selettori fragili di una singola build Workflowy.
- MutationObserver limitato e idempotente, senza loop o scansioni aggressive.
- Test/syntax/CI PASS.