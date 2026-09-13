[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=917364 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | campaign_id=PH_SOLDI_V2_PREMERGE_20260913 | type=Prompt`

# Goal
Completa **solo i due gate locali rimasti** della PR PersonalHub `#7` / branch `feature/soldi-ui-v2`, poi pusha eventuali fix minimi e completa la roadmap. Non rifare review, test host o smoke già PASS.

# Già verificato: NON ripetere
Commit precedente `ac11c70`: `checkArchitectureBoundaries`, unit `core:database` + `feature:soldi`, `:app:compileDebugKotlin`, `:app:assembleQa`, schema Room `12.json`, migrazione Room reale 11→12 su host, editor Spesa/Entrata/Trasferimento, trasferimento EUR→DKK, ricorrenza giorno fisso, modifica `solo questa` / `questa e successive`, forecast per valuta e calendario sono già PASS. Non rieseguire questi gate salvo che un tuo fix tocchi direttamente il relativo codice.

Il branch contiene inoltre `tools/android_room_fixture.py` (commit `6122361`), aggiunto per evitare la precedente sequenza ad-hoc `push/cp/cat/.read/SELinux` nella creazione della fixture Room sul device.

# Scope / sicurezza
- `python3 tools/personalhub_task_lock.py acquire --prompt-id 917364`; lock occupato => `BLOCKED`, nessun polling.
- `~/projects/PersonalHub`, fetch una volta, branch `feature/soldi-ui-v2`; worktree sporco non-task => `BLOCKED`, niente stash/reset.
- Nessun merge/main, bump versione, release, Telegram, package reale o DB personale.
- QA esclusivamente `com.gernalix.personalhub.qa` su `Pixel_8a` canonico.
- Niente discovery generale. Parti da `tools/android_room_fixture.py` e dal codice ricorrenze Soldi solo se un gate fallisce.

# Gate locale A — migrazione Android 11→12
1. Controlla sintassi helper una volta (`python3 -m py_compile tools/android_room_fixture.py`).
2. Avvia/attendi il Pixel_8a con `tools/android_emulator_control.py` e installa **l'APK QA già esistente** se ancora disponibile. Costruisci `:app:assembleQa --no-configuration-cache` solo se l'APK manca.
3. Crea un piccolo seed SQL v11 con almeno un account EUR e una transazione finance riconoscibile.
4. Esegui **una sola volta** `tools/android_room_fixture.py` con schema `11.json`, package QA e seed SQL.
5. Avvia l'app QA per far eseguire Room 11→12; verifica via `run-as ... sqlite3` soltanto: `user_version=12`, record campione preservato e nuova superficie v12 presente.
6. Se l'helper fallisce, correggi solo l'helper sulla base dell'errore concreto e ripeti questo gate. Vietati tentativi manuali alternativi equivalenti finché non emerge nuova evidenza.

# Gate locale B — ultimo giorno lavorativo
Verifica nel package QA una ricorrenza `Ultimo giorno lavorativo`: creazione/salvataggio e presenza corretta dopo riapertura. Usa `android_ui_summary.py` e il minimo numero di input ADB; niente XML completo. Se esiste già un test mirato capace di provarlo, preferiscilo alla navigazione manuale. Un bug reale e localizzato può essere corretto con fix minimo + test mirato; non ridisegnare UX/ricorrenze.

# Stop
PASS appena A+B sono verdi. Non eseguire ulteriori audit/test dopo PASS. Commit/push solo eventuali fix necessari sul branch e verifica divergenza una volta; ferma emulatore e rilascia lock.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 917364 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 917364`

Output ≤6 righe: RESULT, gate A, gate B, fix/commit, push, blocker.
