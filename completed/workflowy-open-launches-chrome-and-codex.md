PROMPT_ID=731805
PROJECT=Facilitatori di prompt
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=FAST
WORKDIR=/home/daniele/projects/chrome-codex-switcher

GOAL
Correggi l'azione Workflowy 🚀 Apri affinché prepari entrambi i lati del pairing: crea/focalizza la tab Chrome associata al PROMPT_ID, arma CCS, quindi apra Codex Desktop per ultimo così il focus finale resta su Codex.

COMPORTAMENTO
- Se il PROMPT_ID non ha ancora un thread Codex associato: apri una nuova chat Codex tramite codex://threads/new.
- Se esiste già un codex_deep_link associato: apri il thread Codex esatto invece di crearne uno nuovo.
- Mantieni il prompt canonico copiato negli appunti.
- Non auto-inviare il prompt e non forzare modello/reasoning.
- Il lato Chrome deve essere creato/bindato/armato PRIMA di aprire Codex.
- Se il context Chrome non è valido o l'arm fallisce, non aprire Codex e restituisci errore.
- 🚀 Apri deve quindi significare davvero: prepara Chrome + apri Codex, con focus finale su Codex.

SCOPE
Solo chrome-codex-switcher: extension/background.js, daemon/API e test strettamente necessari. Riusa il fix pairing/overlay già mergiato da PR #7; niente refactor.

ACCEPTANCE
- nuovo prompt: Chrome context presente + pending_prompt armato + codex://threads/new aperto;
- prompt già associato: apre il deep link esatto;
- nessun Codex launch se binding/arm Chrome fallisce;
- test mirati + CI PASS;
- Workflowy continua a usare lo stesso URL /ui/prompt/<PROMPT_ID>/launch;
- nessuna modifica allo stato di altri prompt.

REPORT
PROMPT_ID=731805
RESULT=PASS|BLOCKED|FAIL
FLOW=
TESTS=
PR=
BLOCKER=