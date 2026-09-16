PROMPT_ID=681247 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal
Distribuisci sul Fedora reale l'ultimo `codex-usage-monitor/main`, che include sia il fix dei path univoci per cicli dello stesso `PROMPT_ID` sia il parser canonico degli stati terminali (`FIXED` incluso), quindi esegui un solo backfill/publish reale e verifica i casi concreti `583214` e `742615`.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/codex-usage-monitor`, branch `main`, project_id `8`;
- commit minimo richiesto: `a916dceb6e553967bfc219ec0a4c1fa1c6ec3fb0` o successivo;
- GitHub Actions run `35085456040` sul commit minimo è già **PASS**: NON duplicare la suite localmente;
- runtime canonico: Fedora locale; Oracle VM NON è runtime;
- il codice e i test deterministici sono già sul remoto: NON reimplementare i fix;
- repo dati privato: `/home/daniele/projects/codex-usage`;
- il backfill parte anche se nel run non esiste alcun nuovo ciclo da pubblicare;
- `PROMPT_ID=583214` ha più esecuzioni storiche ed è il caso di verifica per i path cycle-aware;
- `PROMPT_ID=742615` è stato pubblicato storicamente con `status=UNKNOWN` benché la risposta finale inizi con `FIXED`; il nuovo parser deve riclassificarlo come `FIXED`.

Prompt autosufficiente: niente audit repo-wide, README/roadmap/MegaVault, refactor o nuova discovery architetturale.

# Esecuzione minima
1. Fotografia Git del solo `codex-usage-monitor`. Se pulito: UNA sync `git fetch origin main && git merge --ff-only origin/main`. Se dirty non pertinente/divergente: `BLOCKED`, stop.
2. Verifica solo che `a916dceb6e553967bfc219ec0a4c1fa1c6ec3fb0` sia antenato di HEAD. Non rieseguire test già coperti dalla CI PASS.
3. Esegui UNA volta il deploy canonico già documentato (`python3 deploy_runtime.py`) dal checkout pulito/sincronizzato.
4. Avvia UNA volta `codex-usage-publisher.service` oppure l'equivalente comando runtime canonico già installato, lasciando che completi backfill/push. Nessun loop/retry identico.
5. Verifica nel checkout locale `codex-usage`, senza audit generale:
   - per `583214`, le righe correnti di `index/prompts.jsonl` devono puntare a path distinti `prompts/583214/cycles/<cycle_key>`;
   - ogni path `583214` indicizzato deve contenere `metrics.json` e `transcript.jsonl` col `cycle_key` corretto;
   - `prompts/583214/metrics.json` deve restare presente come alias dell'esecuzione cronologicamente più recente;
   - nessuna esecuzione distinta `583214` deve essere persa/sovrascritta nel tree corrente;
   - per `742615`, `prompts/742615/metrics.json` e la riga/ciclo corrispondente nell'indice devono riportare `status=FIXED`, non `UNKNOWN`.
6. Verifica una sola volta che `codex-usage-publisher.timer` sia enabled/attivo secondo il contratto già esistente e che il run non abbia traceback/errori.
7. Se tutto PASS, nessun'altra esplorazione/test/audit.

# Acceptance
PASS se il runtime Fedora usa il commit richiesto o successivo, il publisher reale completa e pusha, `583214` conserva i cicli in path distinti con alias flat compatibile, `742615` viene riclassificato `FIXED` e il timer rimane operativo.

# Non-goal
Niente nuove modifiche al formato metrics/transcript, quota monitor, Telegram, analyzer, capsule refactor, Oracle VM, full-suite locale o cleanup generale.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 681247 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 681247`

Prima riga finale `RESULT=PASS|BLOCKED|FAIL`; massimo 7 righe: `COMMIT`, `CI`, `DEPLOY`, `PUBLISH`, `583214`, `742615`, `TIMER/BLOCKER`.
