PROMPT_ID=643918 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal
Chiudi sul Fedora reale il recovery di `PROMPT_ID=529184` usando il fix remoto già verificato. Nessuna modifica codice: solo sync, deploy, al massimo una ripubblicazione mirata e readback.

# Stato autoritativo
- `978216` ha già verificato sync/deploy/publisher e si è fermato sul solo mismatch `prompt_id_source=user_prompt_or_attachment` vs `goal_objective_output`.
- Fix remoto minimo: `gernalix/codex-usage-monitor/main` commit `f1049bfec217efa5da8315607f4e5bb3b519f6b6`, CI PASS.
- Repo monitor: `/home/daniele/projects/codex-usage-monitor`; repo dati: `/home/daniele/projects/codex-usage`.
- Sessione: `01a0a93b-8941-7d52-b53e-7f5523e84275`.
- Atteso: `status=PASS`, `completion_state=goal_complete_turn_aborted`, `prompt_id_source=goal_objective_output`, `total_tokens=126386`, `duration_seconds=473.0`.

Prompt autosufficiente. NON leggere MEMORY/MegaVault/README/roadmap, non fare audit repo-wide, non aprire PersonalHub, non usare Oracle VM, non rieseguire test coperti dalla CI.

# Esecuzione minima
1. In `~/projects/codex-usage-monitor`, in UN solo blocco shell: verifica clean+`main`; esegui UNA sync `timeout 20s git fetch origin main && git merge --ff-only origin/main`; verifica `HEAD == origin/main` e che `f1049bf...` sia antenato; esegui UNA volta `python3 deploy_runtime.py --skip-fetch`; verifica `current` + manifest sullo stesso HEAD e presenza di `codex_usage_publisher_base.py`. Failure => `BLOCKED` e stop.
2. Leggi UNA volta `~/projects/codex-usage/prompts/529184/metrics.json`. Se soddisfa già l'Acceptance, salta il publisher.
3. Altrimenti esegui UNA sola volta `timeout 300s /usr/bin/python3 /home/daniele/.local/lib/codex-usage-monitor/current/codex_usage_publisher.py run`. Se resta attivo oltre il primo yield, attendi solo quel processo. NON avviare `codex-usage-publisher.service`.
4. Fai UN readback finale di metrics + transcript e verifica l'Acceptance.
5. In un solo blocco verifica `~/projects/codex-usage` pulito e non ahead/behind rispetto al tracking locale aggiornato dal publisher. Nessun fetch aggiuntivo.
6. Primo mismatch => riporta solo il valore fallito e termina `BLOCKED`; niente debugging, patch, retry o test ulteriori.

# Acceptance
PASS solo se runtime/manifest corrispondono a `HEAD == origin/main` contenente `f1049bf...`; record `529184` ha sessione corretta, `PASS`, `goal_complete_turn_aborted`, `goal_objective_output`, `126386`, `473.0`; prompt/transcript sono del goal e non del follow-up; eventuale publisher exit 0; repo dati pulito e sincronizzato.

# Non-goal
Niente coding, test suite, discovery, refactor, Android, PersonalHub, chat-dump publisher, GitHub Actions watcher, servizi compositi o retry identici.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 643918 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 643918`

Stop subito dopo PASS o primo blocker. Output massimo 5 righe: `RESULT`, `RUNTIME`, `529184`, `PUBLISH`, `BLOCKER`.
