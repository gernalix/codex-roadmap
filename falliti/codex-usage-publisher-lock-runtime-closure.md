PROMPT_ID=642815 | PARENT_PROMPT_ID=371237 | project_id=8 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
Codex Desktop project: Fedora
last_result=BLOCKED

# Goal
Distribuisci sul Fedora reale SOLO i fix già preparati dopo l'analisi di 371237 e chiudi il gate runtime rimasto: il publisher non deve più fallire per una breve sovrapposizione col timer, i test mirati non devono inondare l'output di ResourceWarning SQLite, PROMPT_ID=918274 deve essere pubblicato correttamente e il secondo publisher consecutivo deve chiudersi col fast-path `noop_unchanged_sources`.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/codex-usage-monitor`, branch `main`;
- remoto: `gernalix/codex-usage-monitor`;
- baseline remota minima: `7e25635c1afd1571aa800c1d13e18b383c1eed87`;
- 371237 ha già verificato: 42 test PASS e deploy runtime PASS sulla baseline precedente; si è fermato SOLO perché il primo publisher manuale ha restituito `status=locked`;
- il remoto ora contiene già: attesa bounded del publisher lock, chiusura esplicita delle connessioni SQLite usate nei context manager, test mirati e documentazione;
- target storico ancora da pubblicare: sessione `01a0b571-34c1-77a0-873b-79aab0d23acf`, cycle `00a0f021a74b7246cbec3109`, PROMPT_ID=918274;
- runtime canonico: `/home/daniele/.local/lib/codex-usage-monitor/current`;
- repo dati locale: `/home/daniele/projects/codex-usage`;
- non rileggere README/roadmap/spiegazioni/MEMORY/MegaVault: questo prompt è autosufficiente.

# Esecuzione minima
1. In UNA shell call fail-fast:
   - richiedi branch `main`;
   - `timeout 20s git fetch origin main && git merge --ff-only origin/main`;
   - richiedi `HEAD=origin/main` e baseline minima antenata;
   - esegui SOLO:
     `PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=default::ResourceWarning python3 scripts/verify_repo.py tests.test_usage_publisher tests.test_session_archive tests.test_task_costs tests.test_publication_semantic_backfill tests.test_usage_publisher_regressions 2>&1 | tee /tmp/codex-usage-642815-tests.log`
   - test exit 0 e nessuna riga contenente `ResourceWarning`.
   Se emerge un failure direttamente causato dai fix lock/SQLite già circoscritti, correggi SOLO quel failure domain e rilancia il leaf necessario; niente audit/refactor.
2. Dopo PASS dei test, esegui una sola volta:
   `PYTHONDONTWRITEBYTECODE=1 python3 deploy_runtime.py --skip-fetch`.
3. In UNA sola shell call runtime:
   - esegui il publisher installato con attesa esplicita bounded: `codex_usage_publisher.py run --wait-lock-seconds 90`; misura il wall time;
   - `status=locked` dopo 90 s è un vero blocker runtime; non fare retry identico;
   - verifica direttamente nel checkout dati che il cycle `00a0f021a74b7246cbec3109` sia sotto `prompts/918274/` e che metrics riporti la sessione/cycle esatti;
   - esegui subito un secondo publisher con `--wait-lock-seconds 90`, misura il wall time e richiedi `status=noop_unchanged_sources`;
   - verifica nello stesso batch che `codex-usage-publisher.timer` sia enabled e che l'ultima service non sia failed.
4. Se hai dovuto correggere source in-scope al punto 1, commit/push `main` solo dopo i gate PASS; altrimenti nessun commit locale.
5. Termina subito dopo il risultato terminale. Nessuna suite completa, benchmark extra, scansione di altri rollout, cleanup dello storico o audit post-PASS.

# Acceptance
PASS solo se:
- test mirati PASS senza ResourceWarning;
- runtime deploy PASS;
- publisher run1 non viene abortito da una sovrapposizione transitoria del lock;
- sessione/cycle target risultano pubblicati come PROMPT_ID 918274;
- run2 = `noop_unchanged_sources`;
- timer enabled e service non failed;
- wall time run1/run2 riportati.

# Finalizzazione esatta
PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 642815 --confirm-executed`

BLOCKED:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 642815 --result BLOCKED --confirm-executed`

FAIL:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 642815 --result FAIL --confirm-executed`

Output massimo 7 righe: RESULT, TESTS, DEPLOY, BACKFILL_918274, RUN1, RUN2, TIMER.
