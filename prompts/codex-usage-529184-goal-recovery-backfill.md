PROMPT_ID=978216 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal

Completa sul runtime Fedora il recovery di `PROMPT_ID=529184`: distribuisci il fix già presente su `gernalix/codex-usage-monitor/main`, esegui al massimo una ripubblicazione mirata del solo usage publisher e dimostra con readback deterministico che il record falso del follow-up è stato sostituito dal goal sostanziale completato.

# Starting point autoritativo

- repo locale: `/home/daniele/projects/codex-usage-monitor`;
- dati pubblicati locali: `/home/daniele/projects/codex-usage`;
- sessione nativa interessata: `01a0a93b-8941-7d52-b53e-7f5523e84275` sotto `~/.codex/sessions`;
- `main` remoto contiene già recovery + hardening deploy; commit minimo richiesto `be19be45f1c01e8ba21b311cdc17cd7d54072c17`, con CI verde già verificata;
- `deploy_runtime.py --skip-fetch` evita il fetch ridondante che ha bloccato `618427`, mantenendo worktree-clean e `HEAD == upstream`;
- il goal vero ha `tokensUsed=126386`, `timeUsedSeconds=473`, status `complete`;
- il record pubblicato prima del recovery era errato: `status=UNKNOWN`, `total_tokens=99508`, `duration_seconds=4.628`, prompt text `qual è il prompt id su cui hai lavorato?`;
- `codex-usage-publisher.service` esegue anche chat-dump publisher e GitHub Actions watcher: NON usarlo per questo backfill, perché sono failure domain estranei;
- PersonalHub commit `9afe91aedff03c35b29246a29e768f11815d0cd9` è già valido: non aprire né testare PersonalHub.

Prompt autosufficiente: non leggere MEMORY/MegaVault/README/roadmap, non fare audit repo-wide, non usare Oracle VM.

# Esecuzione minima

1. In `/home/daniele/projects/codex-usage-monitor`, esegui una sola fotografia: `git status --short`, branch, HEAD. Se dirty o branch != `main`, `RESULT=BLOCKED` e stop.
2. Fai una sola sincronizzazione di rete: `timeout 20s git fetch origin main`, quindi `git merge --ff-only origin/main`. Niente `git pull`, niente secondo fetch, niente retry. Failure/timeout => `BLOCKED` e stop.
3. Salva `RUN_HEAD=$(git rev-parse HEAD)` e verifica localmente entrambe le condizioni: `RUN_HEAD == origin/main` e `be19be45f1c01e8ba21b311cdc17cd7d54072c17` è antenato di `RUN_HEAD`. Non rieseguire test già coperti dalla CI.
4. Esegui una sola volta `python3 deploy_runtime.py --skip-fetch`. Verifica senza altri deploy che:
   - exit code = 0 e JSON `status=deployed`;
   - JSON `commit == RUN_HEAD`;
   - `current` risolve a `~/.local/lib/codex-usage-monitor/releases/$RUN_HEAD`;
   - `current/manifest.json` ha `commit == RUN_HEAD` e contiene `codex_usage_publisher_base.py` in `files`.
5. Leggi una sola volta `/home/daniele/projects/codex-usage/prompts/529184/metrics.json`. Se soddisfa già TUTTI i criteri dati del blocco Acceptance, salta la ripubblicazione. Altrimenti esegui UNA sola volta, direttamente dal runtime appena deployato:
   `timeout 300s /usr/bin/python3 /home/daniele/.local/lib/codex-usage-monitor/current/codex_usage_publisher.py run`
   Non avviare `codex-usage-publisher.service`: non servono chat dumps né GitHub Actions watcher.
6. Dopo l'eventuale publisher, fai un unico readback di `prompts/529184/metrics.json` + transcript e verifica TUTTI i criteri dati sotto. Non cercare altri prompt/sessioni.
7. In `/home/daniele/projects/codex-usage`, verifica in un solo blocco che il worktree sia pulito e che la branch non risulti ahead/behind rispetto a `origin/main`; se il publisher è stato eseguito, deve essere terminato con exit code 0. Non fare fetch aggiuntivi solo per questa verifica.
8. Qualunque mismatch => raccogli esclusivamente il valore fallito o l'errore direttamente pertinente e termina `BLOCKED`; niente debugging esplorativo, patch, retry o suite aggiuntive.

# Acceptance

PASS SOLO se sono vere contemporaneamente queste condizioni:

## Runtime
- `RUN_HEAD == origin/main` dopo l'unica fetch;
- `RUN_HEAD` include `be19be45f1c01e8ba21b311cdc17cd7d54072c17`;
- `current` punta alla release di `RUN_HEAD`;
- il manifest della release dichiara lo stesso commit e include `codex_usage_publisher_base.py`.

## Record 529184
- `prompt_id == "529184"`;
- `native_session_id == "01a0a93b-8941-7d52-b53e-7f5523e84275"`;
- `status == "PASS"`;
- `completion_state == "goal_complete_turn_aborted"`;
- `prompt_id_source == "goal_objective_output"`;
- `total_tokens == 126386`;
- `duration_seconds == 473.0`;
- `prompt_text_redacted` NON è e non contiene il follow-up `qual è il prompt id su cui hai lavorato?`;
- transcript/metrics rappresentano il goal recuperato, non il turno follow-up privo di tool-call.

## Pubblicazione
- se è stato necessario eseguire il publisher, il comando è terminato con exit code 0;
- `/home/daniele/projects/codex-usage` è pulito e non risulta ahead/behind da `origin/main` nel tracking locale aggiornato dal publisher;
- nessun errore di deploy/publisher è stato ignorato.

Non richiedere il successo di chat-dump publisher, GitHub Actions watcher o altre unità: non fanno parte di questo task.

# Non-goal

Niente modifiche codice, niente MEMORY/MegaVault discovery, niente Android/PersonalHub, niente emulatori/Gradle, niente Oracle VM, niente ricostruzione globale archivi, niente chat-dump publisher, niente GitHub Actions watcher, niente retry identici, niente test duplicati.

# Stop

Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 978216 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 978216`

Termina immediatamente dopo acceptance o primo blocker. Output massimo 5 righe: `RESULT`, `RUNTIME`, `529184`, `PUBLISH`, `BLOCKER`.
