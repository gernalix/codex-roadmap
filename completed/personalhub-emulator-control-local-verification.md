[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=593406 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | type=Prompt`

> Solo verifica locale. Codice, test unitari e documentazione sono già implementati e pushati; non fare redesign, audit o modifiche salvo blocker che renda impossibile eseguire la verifica.

# Goal
Verificare sul Fedora reale la nuova façade canonica dell'emulatore PersonalHub e chiudere il task senza build APK/UI.

# Starting point verificato
- `tools/android_emulator_control.py`: façade canonica;
- `tools/test_android_emulator_control.py`: 4 test unitari già PASS fuori host;
- low-level preflight invariato rispetto alla validazione host già PASS 22/22 + 6/6;
- `docs/ANDROID_EMULATOR.md` e `AGENTS.md` già aggiornati;
- commit pertinenti già su `origin/main`: `f540d53`, `e7796da`, `1a67ca3`, `0e35b7d`;
- precedente prova reale pre-facade: startup 18.198 s, ADB OK, una sola istanza, stop con 0 residui.

# Procedura minima
1. In `/home/daniele/projects/PersonalHub` acquisisci il lock PH previsto da `AGENTS.md`; se occupato => BLOCKED immediato.
2. Fai un solo `git fetch origin`. Se `main` può avanzare con fast-forward senza toccare modifiche locali, allinealo; altrimenti BLOCKED. Non stash/reset/cleanup.
3. Esegui solo:
   `PYTHONDONTWRITEBYTECODE=1 python3 tools/test_android_emulator_control.py`
4. Se PASS, esegui una sola prova reale:
   `python3 tools/android_emulator_control.py smoke --timeout 90`
5. PASS solo se i 4 test passano e il JSON `smoke` riporta `status=ok`, `boot_completed=true`, `single_pixel_8a_process=true`, `final_stop_clean=true`, `residual_pids=[]`.
6. Non eseguire le suite 22/22 o 6/6 già validate, non buildare/installare APK, non fare UI QA, screenshot, benchmark, retry identici o discovery ADB manuale.
7. Non modificare né pushare PersonalHub. Rilascia il lock.
8. Su PASS completa questo prompt con:

```bash
python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 593406 --dry-run && \
python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 593406
```

Dopo `status=completed` + `push_verified=git_push_exit_0`, STOP immediato.

Output massimo 5 righe: RESULT, test façade, smoke/startup, residui, blocker.
