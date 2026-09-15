[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=681204 | project_id=8 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Validare sul runtime Fedora reale l'hardening già implementato remotamente in `gernalix/codex-usage-monitor` PR #2, quindi integrarlo e distribuire il publisher solo se i gate passano.

# Starting point autoritativo — non rifare discovery
- Repo: `/home/daniele/projects/codex-usage-monitor`.
- PR: `gernalix/codex-usage-monitor#2`.
- Branch: `chatgpt/token-efficiency-hardening`.
- Head atteso al momento della creazione task: `e32d9094cbb01eadfed3c8a1313fa1a82c320b44`.
- Base verificata: `main@34e8624081ed7325b938c86362987a74746c6112`.
- Modifiche già fatte in chat: dedup `repo_paths`; attribuzione `apply_patch` ai repo locali osservati; preferenza del singolo write-repo come `repo_project`; test regressivi; `scripts/verify_repo.py` stdlib; `scripts/analyze_prompt_efficiency.py`.
- Sessione reale di regressione: chat `227`, native session `01a0a6ea-82e2-7410-9053-01a2c9648b83`, `PROMPT_ID=594217`.
- Non leggere `~/.codex/memories/MEMORY.md`; questo task è già prelocalizzato.

# Esecuzione minima
1. Un solo `git status --short --branch`, poi `git fetch --prune origin`.
2. Se il branch/head remoto è avanzato, integra solo cambi compatibili; niente audit generale.
3. Checkout del branch PR e usa come gate canonico, senza pytest/uv/venv:
   `python3 scripts/verify_repo.py`
   Se fallisce, correggi solo la failure concreta e ripeti il gate una volta.
4. Valida l'attribuzione sul rollout nativo della sessione indicata usando una **state DB temporanea**, senza alterare il publisher state di produzione. Per il ciclo di `PROMPT_ID=594217` che contiene le write:
   - `repo_paths` non deve contenere duplicati;
   - `repo_write_projects` deve includere `/home/daniele/projects/codex-usage-monitor`;
   - se quello è l'unico write-repo del ciclo, `repo_project` deve essere `/home/daniele/projects/codex-usage-monitor`.
5. Esegui una sola volta l'analizzatore sul materiale già pubblicato di `PROMPT_ID=594217`:
   `python3 scripts/analyze_prompt_efficiency.py ~/projects/codex-usage/prompts/594217/metrics.json --transcript ~/projects/codex-usage/prompts/594217/transcript.jsonl`
   Deve rilevare almeno l'alta quantità di tool-call/uncached input e la lettura di `MEMORY.md`; non modificare i dati storici solo per rendere il report più pulito.
6. Se tutti i gate passano e `origin/main` non è divergente, integra il branch in `main` con fast-forward, push `main`, elimina il branch integrato.
7. Da `main` pulito/sincronizzato esegui una sola volta il deploy canonico già esistente (`deploy_runtime.py`) e verifica che il manifest/runtime `current` punti al commit finale.
8. Avvia al massimo una volta `codex-usage-publisher.service` solo per smoke test del runtime; nessun loop, nessuna ricostruzione generale degli archivi.

# Non-goal / risparmio token
- niente rilettura di README/roadmap/spiegazioni/MegaVault salvo blocker concreto;
- niente pytest, `uv run`, creazione `.venv` o installazioni: il runner canonico è `scripts/verify_repo.py`;
- niente audit generale di Codex usage, Kuma o Oracle VM;
- niente backfill/ripubblicazione massiva di `codex-usage`;
- niente test equivalenti ripetuti dopo PASS;
- niente refactor/cleanup fuori scope;
- problemi collaterali: segnala senza investigarli.

# Acceptance
- runner canonico PASS;
- regressione reale `594217` attribuisce correttamente il write-repo e deduplica i path;
- efficiency analyzer funziona sul prompt reale;
- branch integrato in `main` solo dopo PASS;
- runtime publisher distribuito dal commit finale e smoke test PASS.

# Stop
Dopo PASS completa questo solo task con `roadmap_guard.py complete --prompt-id 681204` secondo il protocollo corrente e fermati. Nessun audit post-PASS.

Output massimo 6 righe: RESULT, main SHA, verify, regressione 594217, analyzer, deploy/smoke oppure blocker.
