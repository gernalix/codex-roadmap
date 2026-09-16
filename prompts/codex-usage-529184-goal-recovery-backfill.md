PROMPT_ID=618427 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal

Distribuisci sul runtime Fedora canonico il fix già presente su `gernalix/codex-usage-monitor/main` e riprocessa una sola volta il rollout reale che contiene `PROMPT_ID=529184`, così il publisher sostituisce la falsa attribuzione del follow-up con il goal sostanziale realmente completato.

# Starting point autoritativo

- repo locale: `/home/daniele/projects/codex-usage-monitor`;
- dati pubblicati locali: `/home/daniele/projects/codex-usage`;
- sessione nativa interessata: `01a0a93b-8941-7d52-b53e-7f5523e84275` sotto `~/.codex/sessions`;
- `main` remoto contiene già il fix, i test di regressione e il packaging runtime; non modificare codice salvo blocker locale dimostrato;
- il goal vero ha `tokensUsed=126386`, `timeUsedSeconds=473`, status `complete`;
- il record attualmente pubblicato sotto `prompts/529184` è errato: rappresenta il follow-up “qual è il prompt id su cui hai lavorato?”, `tool_call_count=0`, non il task;
- PersonalHub commit `9afe91aedff03c35b29246a29e768f11815d0cd9` è già valido: non aprire né testare PersonalHub.

Prompt autosufficiente: niente audit repo-wide, niente MegaVault/README/roadmap discovery, niente Oracle VM.

# Esecuzione minima

1. In `/home/daniele/projects/codex-usage-monitor`, controlla solo `git status --short`, branch e HEAD. Se pulito, `git fetch origin` + `git pull --ff-only origin main`; se dirty o divergente, `RESULT=BLOCKED` e stop.
2. Verifica che HEAD includa almeno `52b7b6cf46efc1593430480c5f95fdf063b61b06` e che la CI di quel commit o di un suo discendente sia verde. Nessuna suite locale duplicata.
3. Esegui una sola volta `python3 deploy_runtime.py`. Conferma dal JSON che `current` punta alla release del nuovo HEAD e che il manifest contiene `codex_usage_publisher_base.py`.
4. Esegui una sola volta `systemctl --user start codex-usage-publisher.service`; attendi il completamento del oneshot e leggi solo lo status/journal di questa esecuzione se serve.
5. Controlla direttamente `/home/daniele/projects/codex-usage/prompts/529184/metrics.json` e il relativo transcript. PASS solo se il record sostanziale risulta ricostruito con:
   - `prompt_id = "529184"`;
   - `status = "PASS"`;
   - `completion_state = "goal_complete_turn_aborted"`;
   - `prompt_id_source = "goal_objective_output"`;
   - `total_tokens = 126386`;
   - `duration_seconds = 473.0`;
   - il testo non è il follow-up “qual è il prompt id su cui hai lavorato?”.
6. Verifica con un solo `git status`/`git log -1` nel checkout `/home/daniele/projects/codex-usage` che la ripubblicazione sia stata committata/pushata. Non cercare altri prompt.
7. Se il publisher non ricostruisce `529184`, raccogli soltanto l’errore/log pertinente e termina `BLOCKED`; non fare debugging esplorativo o patch non richieste in questa sessione.
8. Dopo PASS, esegui una sola volta:
   `python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 618427 --confirm-executed`

# Acceptance

PASS se il runtime Fedora usa il nuovo commit, il publisher reale completa senza errore e `prompts/529184` rappresenta il goal completato con `126386` token e `473 s`, non il follow-up.

# Non-goal

Niente modifiche Android/PersonalHub, niente emulatori/Gradle, niente refactor del monitor, niente ricostruzione globale degli archivi, niente Oracle VM, niente retry identici, niente test già coperti dalla CI.

# Stop

Termina immediatamente dopo l’acceptance. Output massimo 5 righe: `RESULT`, `RUNTIME`, `529184`, `PUBLISH`, `BLOCKER`.