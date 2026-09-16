PROMPT_ID=978216 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal

Completa sul runtime Fedora il recovery di `PROMPT_ID=529184`: distribuisci il fix già presente su `gernalix/codex-usage-monitor/main`, esegui una sola ripubblicazione reale e verifica che il record falso del follow-up venga sostituito dal goal sostanziale completato.

# Starting point autoritativo

- repo locale: `/home/daniele/projects/codex-usage-monitor`;
- dati pubblicati locali: `/home/daniele/projects/codex-usage`;
- sessione nativa interessata: `01a0a93b-8941-7d52-b53e-7f5523e84275` sotto `~/.codex/sessions`;
- `main` remoto contiene già sia il recovery del goal abortito sia l'hardening di `deploy_runtime.py`; il commit minimo richiesto è `be19be45f1c01e8ba21b311cdc17cd7d54072c17`;
- `deploy_runtime.py --skip-fetch` evita il fetch ridondante che ha bloccato il precedente tentativo `618427`, ma continua a richiedere worktree pulito e `HEAD == upstream`;
- il goal vero ha `tokensUsed=126386`, `timeUsedSeconds=473`, status `complete`;
- PersonalHub commit `9afe91aedff03c35b29246a29e768f11815d0cd9` è già valido: non aprire né testare PersonalHub.

Prompt autosufficiente: non leggere MEMORY/MegaVault/README/roadmap, non fare audit repo-wide, non usare Oracle VM.

# Esecuzione minima

1. In `/home/daniele/projects/codex-usage-monitor`, controlla una sola volta `git status --short`, branch e HEAD. Se dirty o non sei su `main`, `RESULT=BLOCKED` e stop.
2. Fai una sola sincronizzazione di rete: `timeout 20s git fetch origin main`, poi solo localmente `git merge --ff-only origin/main`. Non usare `git pull` e non rifare fetch. Se la fetch fallisce/scade, `RESULT=BLOCKED` e stop senza retry.
3. Verifica solo che `be19be45f1c01e8ba21b311cdc17cd7d54072c17` sia antenato di HEAD. Non rieseguire suite locali già coperte dalla CI.
4. Esegui una sola volta `python3 deploy_runtime.py --skip-fetch`. Dal JSON verifica che `current` punti alla release del nuovo HEAD e che il manifest contenga `codex_usage_publisher_base.py`.
5. Esegui una sola volta `systemctl --user start codex-usage-publisher.service`; attendi il completamento del oneshot e leggi status/journal solo se necessario.
6. Controlla direttamente `/home/daniele/projects/codex-usage/prompts/529184/metrics.json` e il transcript. PASS solo se risultano:
   - `prompt_id = "529184"`;
   - `status = "PASS"`;
   - `completion_state = "goal_complete_turn_aborted"`;
   - `prompt_id_source = "goal_objective_output"`;
   - `total_tokens = 126386`;
   - `duration_seconds = 473.0`;
   - il testo non è il follow-up “qual è il prompt id su cui hai lavorato?”.
7. Nel checkout `/home/daniele/projects/codex-usage`, usa un solo `git status --short` + `git log -1 --oneline` e verifica che la ripubblicazione sia stata committata/pushata. Non cercare altri prompt.
8. Se il publisher non ricostruisce `529184`, raccogli solo l'errore/log direttamente pertinente e termina `BLOCKED`; niente debugging esplorativo o patch in questa sessione.

# Acceptance

PASS se il runtime Fedora usa un commit che include `be19be45f1c01e8ba21b311cdc17cd7d54072c17`, il publisher reale completa senza errore e `prompts/529184` rappresenta il goal completato con `126386` token e `473 s`, non il follow-up.

# Non-goal

Niente modifiche codice, niente MEMORY/MegaVault discovery, niente Android/PersonalHub, niente emulatori/Gradle, niente Oracle VM, niente ricostruzione globale archivi, niente retry identici, niente test duplicati.

# Stop

Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 978216 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 978216`

Termina immediatamente dopo acceptance o primo blocker. Output massimo 5 righe: `RESULT`, `RUNTIME`, `529184`, `PUBLISH`, `BLOCKER`.
