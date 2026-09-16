PROMPT_ID=681247 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal
Distribuisci sul Fedora reale il fix già presente in `codex-usage-monitor/main` che conserva ogni esecuzione di uno stesso `PROMPT_ID` in un path univoco `prompts/<id>/cycles/<cycle_key>/`, mantenendo il vecchio path flat come alias dell'ultimo ciclo, quindi esegui un solo backfill/publish reale e verifica il caso concreto `583214`.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/codex-usage-monitor`, branch `main`, project_id `8`;
- commit minimo richiesto: `86becc51d2a2f79c517c4b4b2ec4a37909af005e` o successivo;
- GitHub Actions run `35082850978` sul commit minimo è già **PASS**: NON duplicare la suite localmente;
- runtime canonico: Fedora locale; Oracle VM NON è runtime;
- il codice e i test deterministici sono già sul remoto: NON reimplementare il fix;
- repo dati privato: `/home/daniele/projects/codex-usage`;
- il backfill ora parte anche se in quel run non esiste alcun nuovo ciclo da pubblicare;
- il bug precedente faceva condividere a più cicli `prompts/<PROMPT_ID>/metrics.json` e `transcript.jsonl`, lasciando la Git history come unico recupero delle versioni precedenti;
- `PROMPT_ID=583214` ha più esecuzioni storiche ed è il caso di verifica.

Prompt autosufficiente: niente audit repo-wide, README/roadmap/MegaVault, refactor o nuova discovery architetturale.

# Esecuzione minima
1. Fotografia Git del solo `codex-usage-monitor`. Se pulito: UNA sync `git fetch origin main && git merge --ff-only origin/main`. Se dirty non pertinente/divergente: `BLOCKED`, stop.
2. Verifica solo che `86becc51d2a2f79c517c4b4b2ec4a37909af005e` sia antenato di HEAD. Non rieseguire test già coperti dalla CI PASS.
3. Esegui UNA volta il deploy canonico già documentato (`python3 deploy_runtime.py`) dal checkout pulito/sincronizzato.
4. Avvia UNA volta `codex-usage-publisher.service` oppure l'equivalente comando runtime canonico già installato, lasciando che completi il backfill/push. Nessun loop/retry identico.
5. Verifica nel checkout locale `codex-usage` solo il caso `583214`:
   - le righe correnti di `index/prompts.jsonl` per `583214` devono puntare a path distinti `prompts/583214/cycles/<cycle_key>`;
   - ogni path indicizzato deve contenere `metrics.json` e `transcript.jsonl` col `cycle_key` corretto;
   - `prompts/583214/metrics.json` deve restare presente come alias dell'esecuzione cronologicamente più recente;
   - nessuna esecuzione distinta deve essere persa/sovrascritta nel tree corrente.
6. Verifica una sola volta che `codex-usage-publisher.timer` sia enabled/attivo secondo il contratto già esistente e che il run non abbia traceback/errori.
7. Se tutto PASS, nessun'altra esplorazione/test/audit.

# Acceptance
PASS se il runtime Fedora usa il commit richiesto o successivo, il publisher reale completa e pusha, `583214` conserva i cicli in path distinti, il flat path resta compatibile e il timer rimane operativo.

# Non-goal
Niente modifiche al formato dei metrics/transcript, parser status, quota monitor, Telegram, analyzer, capsule refactor, Oracle VM, full-suite locale o cleanup generale.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 681247 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 681247`

Prima riga finale `RESULT=PASS|BLOCKED|FAIL`; massimo 6 righe: `COMMIT`, `CI`, `DEPLOY`, `PUBLISH`, `583214`, `TIMER/BLOCKER`.
