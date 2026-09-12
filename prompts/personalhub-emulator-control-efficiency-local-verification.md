[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=816274 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | type=Prompt`

> Solo verifica locale. Il codice è già implementato nel branch `infra/emulator-control-efficiency`. Non fare audit, redesign, refactor o cleanup.

# Goal
Verificare sul Fedora reale l'hardening della façade emulator e il nuovo gate aggregato, senza merge in `main`.

# Starting point verificato
- branch PH: `infra/emulator-control-efficiency`;
- façade: `tools/android_emulator_control.py`;
- gate unico: `tools/test_android_emulator_stack.py`;
- il gate include già suite storica preflight + regressioni + façade e rifiuta cache Python tracciate;
- `smoke` mantiene un budget per lo stop finale e restituisce già boot, processo singolo e residui;
- docs e `AGENTS.md` sono già aggiornati;
- nessun bump versione, APK, UI QA o merge richiesto.

# Procedura minima
1. In `/home/daniele/projects/PersonalHub` acquisisci il lock PH per `816274`; se occupato => `BLOCKED` immediato.
2. Fai un solo `git fetch origin`. Preserva qualunque modifica locale: niente stash/reset/cleanup. Porta il checkout sul branch remoto `infra/emulator-control-efficiency` solo se possibile senza perdere o inglobare lavoro locale; altrimenti `BLOCKED`.
3. Esegui esattamente una volta:
   `PYTHONDONTWRITEBYTECODE=1 python3 tools/test_android_emulator_stack.py`
   Se FAIL, riporta il test/errore esatto e STOP. Non rilanciare separatamente le tre suite componenti e non modificare codice.
4. Solo se PASS, esegui esattamente una prova reale:
   `python3 tools/android_emulator_control.py smoke --timeout 90`
5. PASS solo se il JSON riporta `status=ok`, `checks.boot_completed=true`, `checks.single_pixel_8a_process=true`, `checks.final_stop_clean=true` e `residual_pids=[]`.
6. Dopo lo smoke non fare discovery ADB/processi manuale: il JSON è l'evidenza autoritativa. Verifica soltanto `git status --short` e `git ls-files '*__pycache__*' '*.pyc' '*.pyo'`: devono essere vuoti per artefatti generati/tracciati da questa verifica.
7. Non buildare/installare APK, non aprire UI, non fare screenshot, benchmark, retry identici, test componenti separati, modifiche o push a PersonalHub. Non mergiare il branch.
8. Rilascia il lock. Su PASS completa solo `PROMPT_ID=816274` con `roadmap_guard complete`; quindi STOP.

# Acceptance
- gate aggregato PASS;
- unico smoke reale PASS;
- stop finale pulito e nessun PID residuo;
- nessun nuovo file/cache Python tracciato o modifica del checkout;
- nessuna modifica a PersonalHub e nessun merge.

Output massimo 5 righe: RESULT, gate aggregato, smoke/startup, git/cache cleanliness, blocker.
