[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=284731 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | campaign_id=PH_SOLDI_V2_PREMERGE_20260913 | type=Prompt`

# Goal
Valida **solo** il commit remoto `2f63bbc` su `feature/soldi-ui-v2`: `tools/android_room_fixture.py` deve attendere internamente la vera migrazione Room e dichiarare PASS solo con schema target, `integrity_check=ok` e `foreign_key_check` pulito. Nessuna review generale, nessun altro gate Soldi, merge o release.

# Scope
- Acquisisci il lock PH per `284731`; lock occupato => `BLOCKED`, nessun polling.
- Fai un solo fetch e usa `feature/soldi-ui-v2`; worktree sporco non-task => `BLOCKED`, niente stash/reset.
- Parti esclusivamente da `tools/android_room_fixture.py`; apri altro codice solo se una failure concreta lo richiede.
- Riusa APK QA esistente; `:app:assembleQa --no-configuration-cache` solo se manca. Solo package `com.gernalix.personalhub.qa` e Pixel_8a canonico.

# Gate unico
1. `python3 -m py_compile tools/android_room_fixture.py`.
2. Avvia/attendi Pixel_8a e installa l'APK QA se necessario.
3. Prepara seed v11 minimo + query di preservazione in file temporanei.
4. Esegui **una sola invocazione** di `android_room_fixture.py` con `--launch-and-verify --target-version 12 --expect-table finance_recurrences --verify-sql ... --expect-line ...`.
5. PASS solo se la stessa invocazione arriva a v12, preserva il record, trova `finance_recurrences` e il JSON finale riporta `migration.integrity="ok"` e `migration.foreign_keys="ok"`.
6. Se fallisce, correggi solo l'helper in base alla failure concreta e ripeti il gate una volta; niente workaround manuali equivalenti `adb shell sqlite3`, pipe, push/cp/.read o test aggiuntivi.

# Stop
Appena PASS, verifica divergenza una volta, push solo eventuale fix indispensabile, ferma emulatore e rilascia lock. Non eseguire Gradle/test/UI/smoke ulteriori.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 284731 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 284731`

Output ≤4 righe: RESULT, helper gate, fix/push, blocker/cleanup.