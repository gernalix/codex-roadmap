[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=364208 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Distribuire sul Fedora il fix **già pushato e con CI verde** di `codex-usage-monitor` che rende conservativa l'associazione dei follow-up al PROMPT_ID, mantiene la deduplica di `chat.metrics.prompt_ids` e corregge il backfill storico troppo permissivo.

Task di deploy/backfill, non di sviluppo.

# Starting point verificato
- repo: `/home/daniele/projects/codex-usage-monitor`;
- `origin/main` contiene commit `24de6235e959f71a3a0e3d3bf5656a74b16ad1fa` o successivo;
- GitHub Actions run `35051564112` PASS;
- regressioni remote: prompt allegato, continuazione goal automatica, follow-up breve dopo BLOCKED, messaggio umano successivo non correlato, deduplica PROMPT_ID;
- il precedente run di questo stesso prompt ha correttamente testato/deployato la versione precedente ma ha verificato troppo presto: il commit `codex-usage` che sistemava `157771` è arrivato ~51 s dopo il suo BLOCKED;
- inoltre la policy precedente era troppo ampia e ha retro-associato cicli storici non correlati.

# Sentinelle autoritative
Dopo il nuovo backfill devono valere tutte:
1. **follow-up BLOCKED corretto** — chat `233`, ciclo finale `afd01ade7018f3d34bd7f493`: `prompt_id=157771`, `path=prompts/157771`, `status=PASS`; `chats/233/metrics.json.prompt_ids == ["157771"]`;
2. **continuazione goal corretta** — chat `231`, ciclo finale PASS `350b0853726e20ade2b63add`: deve restare associato a `472913`;
3. **falso positivo da rimuovere** — chat `85`, ciclo `33f38dc71a01b3ee8ca0f360`, testo utente `scrivi il percorso completo del final manifest`: deve tornare `prompt_id=null` e `path=prompts/unassigned/33f38dc71a01b3ee8ca0f360`, non `816428`.

# Esecuzione minima
1. Una sola fotografia Git. Dirty non riconducibile al task => BLOCKED; niente stash/reset.
2. `git pull --ff-only origin main` una volta e verifica che HEAD includa `24de6235e959f71a3a0e3d3bf5656a74b16ad1fa`; nessun audit.
3. Una sola volta:
   `PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_repo.py tests.test_usage_publisher_regressions`
   Deve risultare PASS (8 test). Failure => BLOCKED immediato, nessun source edit/retry.
4. `python3 deploy_runtime.py` una volta; verifica che `current` punti alla release del nuovo HEAD.
5. Registra `origin/main` corrente di `/home/daniele/projects/codex-usage`, poi avvia una sola run con `systemctl --user start codex-usage-publisher.service`. Se fallisce, leggi solo status + ultimo log pertinente e STOP.
6. **Evita il race del run precedente:** senza modificare il checkout `codex-usage`, fai al massimo un unico loop bounded di fetch/verifica per <=90 s (intervallo ~5 s):
   - `git -C ~/projects/codex-usage fetch origin main`;
   - leggi gli artefatti direttamente da `origin/main` con `git show origin/main:<path>`;
   - termina appena tutte e tre le sentinelle sopra sono vere.
   Non fare polling separati, pull, retry del publisher o sleep dopo PASS.
7. Verifica anche una sola volta che `codex-usage-publisher.service` abbia `Result=success` / exit 0.
8. Nessun backfill manuale, nessuna modifica a `codex-usage`: le correzioni devono provenire dal publisher.

# Non-goal
Niente source edit, refactor, nuove feature, schema DB, modifica systemd, tuning generale, analisi di altre sessioni, MegaVault update, Telegram o VM Oracle.

# Acceptance
PASS solo se: regressioni PASS; deploy nuovo HEAD PASS; publisher PASS; le tre sentinelle sono vere su `origin/main`. In particolare, non basta correggere `157771`: deve essere provato anche che il falso `33f38dc… -> 816428` sia stato rimosso.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 364208 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 364208`

Output massimo 6 righe: RESULT, TEST, DEPLOY/PUBLISHER, SENTINEL_157771, SENTINEL_472913, SENTINEL_FALSE_POSITIVE/BLOCKER.