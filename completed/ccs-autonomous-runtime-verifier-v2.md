PROMPT_ID=684327
PROJECT=Facilitatori di prompt
MODEL=GPT-5.6 Sol
REASONING=medium
MEGAVAULT=FAST
WORKDIR=/home/daniele/projects/chrome-codex-switcher

GOAL
Rendi completamente autonomo il collaudo Chrome ↔ Codex creando un control plane/test harness non distruttivo che permetta a Codex di verificare un PROMPT_ID end-to-end senza accesso visuale alla UI Chrome.

CONTESTO
- 314792 ha dimostrato che il pairing/overlay non era verificabile autonomamente.
- PR #7 di chrome-codex-switcher contiene il fix pairing/overlay già testato in CI; riusalo, non rifare discovery generale.
- Non introdurre browser automation generica, OCR o screenshot.
- Usa gli stati reali già mantenuti da daemon, extension e GNOME companion.

IMPLEMENTA
- context-twin verify-prompt <PROMPT_ID> --full
- context-twin verify-binding <PROMPT_ID>
- context-twin verify-note <PROMPT_ID>
- context-twin verify-overlay
- context-twin verify-workflowy <PROMPT_ID>
- context-twin self-test
- endpoint GET /api/verify/prompt/<PROMPT_ID>
- heartbeat/ack sufficienti a verificare extension, GNOME companion, focus/open dei due lati, overlay/thread corretto e stale-note guard
- test note shared bidirezionale con snapshot/restore non distruttivo
- output JSON machine-readable PASS/BLOCKED con gate granulari
- Workflowy: azione 🔎 Verify che mostri ✅ Runtime verified oppure ❌ Runtime failed con motivo

VINCOLI
- niente guessing su titoli/thread ambigui
- riusa logica esistente; niente refactor/cleanup fuori scope
- test unitari/JS mirati + CI
- usa workflow repo canonico
- stop immediato a PASS

ACCEPTANCE
PASS solo se il prossimo caso tipo 314792 è verificabile completamente da Codex via CLI/API senza chiedere conferme manuali all'utente.

REPORT
PROMPT_ID=684327
RESULT=PASS|BLOCKED|FAIL
NEW_COMMANDS=
NEW_ENDPOINTS=
WORKFLOWY_VERIFY=
SELF_TEST=
TESTS=
CI=
BLOCKER=