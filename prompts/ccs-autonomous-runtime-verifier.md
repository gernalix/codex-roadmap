PROMPT_ID=658142
PROJECT=Facilitatori di prompt
MODEL=GPT-5.6 Sol
REASONING=medium
MEGAVAULT=FAST

GOAL
Aggiungi a chrome-codex-switcher un control plane/test harness non distruttivo che permetta a Codex di verificare autonomamente un PROMPT_ID end-to-end senza accesso generico alla UI Chrome.

ACCEPTANCE
- comando CLI unico: context-twin verify-prompt <PROMPT_ID> --full
- verifica binding PROMPT_ID ↔ context Chrome ↔ thread/deep-link Codex
- verifica runtime Chrome extension e GNOME companion con heartbeat/ack freschi
- può aprire/focalizzare i due lati e ricevere ack programmatici
- verifica overlay associato al thread corretto e stale-note guard
- test note shared bidirezionale con snapshot/restore non distruttivo
- output machine-readable PASS/BLOCKED con gate granulari
- niente guessing su titoli/thread ambigui
- test unitari/JS mirati + CI
- usa workflow repo canonico; stop a PASS.
