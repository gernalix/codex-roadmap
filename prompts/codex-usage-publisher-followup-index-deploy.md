[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=364208 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Distribuire sul Fedora il fix **già pushato e con CI verde** di `codex-usage-monitor` che associa i turni di continuazione al PROMPT_ID attivo e deduplica `chat.metrics.prompt_ids`, quindi ripubblicare gli indici e verificare specificamente la sessione `157771`/chat `233`.

Task di deploy/backfill, non di sviluppo.

# Starting point verificato
- repo: `/home/daniele/projects/codex-usage-monitor`;
- `origin/main` contiene commit `4b228ab82aa2eef7e5b84c99b580b0bf749c350a` o successivo;
- GitHub Actions run `35049969845` PASS;
- regressioni remote coprono follow-up umano `autorizzo` e deduplica PROMPT_ID;
- sessione da correggere: chat `233`, native session `01a0a7ed-f4f2-7270-9756-ae11659ee693`;
- prima del fix il ciclo finale PASS `afd01ade7018f3d34bd7f493` risultava `unassigned` e `chats/233/metrics.json` ripeteva `157771` più volte.

# Esecuzione minima
1. Una sola fotografia Git del repo. Dirty non riconducibile al task => BLOCKED; niente stash/reset.
2. `git pull --ff-only origin main` una volta. Verifica solo che HEAD includa `4b228ab82aa2eef7e5b84c99b580b0bf749c350a`; nessun audit.
3. Esegui una sola volta:
   `PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_repo.py tests.test_usage_publisher_regressions`
   Deve risultare PASS. Non modificare sorgenti se fallisce: riporta BLOCKED con il test fallito.
4. Esegui `python3 deploy_runtime.py` una volta.
5. Avvia una singola run con `systemctl --user start codex-usage-publisher.service`; poi leggi solo status/ultimo log dell'unit se il comando fallisce.
6. Verifica il risultato nel clone locale `~/projects/codex-usage` dopo il publisher; fai `git pull --ff-only` solo se necessario per vedere il commit appena pubblicato. Richiedi:
   - `index/prompts.jsonl`: ciclo `afd01ade7018f3d34bd7f493` => `prompt_id=157771`, `path=prompts/157771`, `status=PASS`;
   - `prompts/157771/metrics.json`: `prompt_id=157771` e `status=PASS`;
   - `chats/233/metrics.json`: `cycle_count=8` e `prompt_ids` esattamente `["157771"]`.
7. Nessuna modifica a `codex-usage`, nessun backfill manuale di JSON: deve essere prodotto dal publisher.

# Non-goal
Niente refactor, nuove feature, schema DB, tuning performance, modifica systemd, analisi di altre sessioni, MegaVault update, Telegram, VM Oracle o retry identici.

# Acceptance
PASS solo se test locali, deploy, singola run publisher e tre verifiche di `157771` sono PASS. Se il publisher non rigenera l'indice correttamente, BLOCKED con il primo mismatch concreto e STOP.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 364208 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 364208`

Output massimo 5 righe: RESULT, TEST, DEPLOY/PUBLISHER, INDEX_157771, CHAT_233/BLOCKER.