[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=364208 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Distribuire sul Fedora il fix **già pushato e con CI verde** di `codex-usage-monitor` che associa correttamente al PROMPT_ID sia i follow-up di sblocco sia le continuazioni automatiche senza messaggio utente, senza reintrodurre false associazioni storiche.

Task di deploy/backfill, non di sviluppo.

# Starting point verificato
- repo: `/home/daniele/projects/codex-usage-monitor`;
- `origin/main` contiene commit `fa17bf13c9cc0816bc58c97ab5dbbf561ab90714` o successivo;
- GitHub Actions run `35052711895` PASS;
- `tests.test_usage_publisher_regressions` contiene 9 regressioni, inclusa la continuazione automatica senza user message osservata realmente in `472913`;
- il run precedente di `364208` ha già provato che `157771` e la sentinella negativa `33f38dc…` sono corretti; l'unico residuo era `472913`, il cui secondo ciclo ha `prompt_text_redacted=null`.

# Sentinelle autoritative
Dopo il backfill devono valere tutte:
1. chat `233`, ciclo `afd01ade7018f3d34bd7f493` => `prompt_id=157771`, `path=prompts/157771`, `status=PASS`; `chats/233/metrics.json.prompt_ids == ["157771"]`;
2. chat `231`, ciclo `350b0853726e20ade2b63add` => `prompt_id=472913`, `path=prompts/472913`, `status=PASS`;
3. chat `85`, ciclo `33f38dc71a01b3ee8ca0f360` => `prompt_id=null`, `path=prompts/unassigned/33f38dc71a01b3ee8ca0f360`.

# Esecuzione minima
1. Una sola fotografia Git. Dirty non riconducibile al task => BLOCKED; niente stash/reset.
2. `git pull --ff-only origin main` una volta; verifica che HEAD includa `fa17bf13c9cc0816bc58c97ab5dbbf561ab90714`. Nessun audit/memory discovery.
3. Una sola volta:
   `PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_repo.py tests.test_usage_publisher_regressions`
   Richiedi PASS con 9 test. Failure => BLOCKED immediato; nessun source edit/retry.
4. `python3 deploy_runtime.py` una volta; `current` deve puntare al nuovo HEAD.
5. Registra l'attuale `origin/main` di `~/projects/codex-usage`, poi avvia una sola run `systemctl --user start codex-usage-publisher.service`. Failure => solo status/ultimo log pertinente e STOP.
6. Senza modificare il checkout `codex-usage`, usa **un solo loop bounded <=90 s** (~5 s) che fa `git fetch origin main` e legge le tre sentinelle direttamente da `origin/main` con `git show`. Esci immediatamente appena sono tutte vere; nessun secondo publisher, pull o retry identico.
7. Una sola verifica finale `Result=success` / exit 0 del service.
8. Nessun backfill manuale e nessuna modifica a `codex-usage`.

# Non-goal
Niente source edit, refactor, feature, schema DB, modifica systemd, tuning generale, MegaVault, Telegram, Oracle o analisi di altre sessioni.

# Acceptance
PASS solo con: 9 regressioni PASS; deploy nuovo HEAD PASS; publisher PASS; tutte e tre le sentinelle vere su `origin/main`.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 364208 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 364208`

Output massimo 6 righe: RESULT, TEST, DEPLOY/PUBLISHER, SENTINEL_157771, SENTINEL_472913, SENTINEL_FALSE_POSITIVE/BLOCKER.