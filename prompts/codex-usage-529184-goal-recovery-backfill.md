PROMPT_ID=684271 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal

Chiudi sul Fedora reale il recovery di `PROMPT_ID=529184` usando il fix remoto già verificato. Non modificare codice: fai solo sync, deploy, al massimo una ripubblicazione del solo usage publisher e readback deterministico.

# Stato autoritativo

- `978216` ha già verificato la pipeline runtime e si è fermato correttamente sull'unico mismatch residuo: `prompt_id_source=user_prompt_or_attachment` invece di `goal_objective_output`.
- Il bug è già corretto su `gernalix/codex-usage-monitor/main`; commit minimo richiesto: `f1049bfec217efa5da8315607f4e5bb3b519f6b6`, CI PASS.
- Repo locale monitor: `/home/daniele/projects/codex-usage-monitor`.
- Repo dati: `/home/daniele/projects/codex-usage`.
- Sessione: `01a0a93b-8941-7d52-b53e-7f5523e84275`.
- Valori attesi del goal recuperato: `status=PASS`, `completion_state=goal_complete_turn_aborted`, `prompt_id_source=goal_objective_output`, `total_tokens=126386`, `duration_seconds=473.0`.

Prompt autosufficiente. NON leggere MEMORY/MegaVault/README/roadmap, non fare audit repo-wide, non aprire PersonalHub, non usare Oracle VM, non rieseguire test già coperti dalla CI.

# Esecuzione minima

1. In `~/projects/codex-usage-monitor`, in UN SOLO blocco shell:
   - verifica worktree pulito e branch `main`; altrimenti `BLOCKED` e stop;
   - esegui UNA sola sync: `timeout 20s git fetch origin main && git merge --ff-only origin/main`;
   - verifica `HEAD == origin/main` e che `f1049bfec217efa5da8315607f4e5bb3b519f6b6` sia antenato di `HEAD`;
   - esegui UNA sola volta `python3 deploy_runtime.py --skip-fetch`;
   - verifica che `current` e `current/manifest.json` puntino allo stesso `HEAD` e che il manifest includa `codex_usage_publisher_base.py`.
   Qualunque failure => `BLOCKED` e stop.
2. Leggi UNA volta `~/projects/codex-usage/prompts/529184/metrics.json`. Se soddisfa già tutta l'Acceptance, non pubblicare nulla e vai al punto 4.
3. Altrimenti esegui UNA sola volta:
   `timeout 300s /usr/bin/python3 /home/daniele/.local/lib/codex-usage-monitor/current/codex_usage_publisher.py run`
   Se il processo resta attivo oltre il primo yield, attendi solo quel processo; nessun secondo run. NON avviare `codex-usage-publisher.service`.
4. Fai UN SOLO readback finale di `prompts/529184/metrics.json` e relativo transcript. Verifica l'Acceptance.
5. Verifica in un solo blocco che `~/projects/codex-usage` sia pulito e non ahead/behind rispetto al tracking locale aggiornato dal publisher. Non fare fetch aggiuntivi.
6. Primo mismatch => riporta soltanto il valore fallito e termina `BLOCKED`. Niente debugging, patch, retry o test ulteriori.

# Acceptance

PASS solo se:
- runtime deployato da `HEAD == origin/main`, contenente `f1049bfec217efa5da8315607f4e5bb3b519f6b6`;
- `current` e manifest corrispondono allo stesso HEAD;
- `prompt_id == "529184"`;
- `native_session_id == "01a0a93b-8941-7d52-b53e-7f5523e84275"`;
- `status == "PASS"`;
- `completion_state == "goal_complete_turn_aborted"`;
- `prompt_id_source == "goal_objective_output"`;
- `total_tokens == 126386`;
- `duration_seconds == 473.0`;
- prompt/transcript rappresentano il goal recuperato e non il follow-up `qual è il prompt id su cui hai lavorato?`;
- se il publisher è stato eseguito, exit code 0;
- `~/projects/codex-usage` pulito e non ahead/behind.

# Non-goal

Niente modifiche codice, suite test, discovery, refactor, Android, PersonalHub, chat-dump publisher, GitHub Actions watcher, servizi compositi, retry identici o indagini collaterali.

# Stop

Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 684271 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 684271`

Termina subito dopo PASS o primo blocker. Output massimo 5 righe: `RESULT`, `RUNTIME`, `529184`, `PUBLISH`, `BLOCKER`.
