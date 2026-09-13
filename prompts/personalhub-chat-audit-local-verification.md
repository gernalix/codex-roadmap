[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=641904 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST | campaign_id=PH_FINAL_20260912 | type=Prompt`

# Goal
Verifica **solo localmente** le modifiche già pushate da ChatGPT su `gernalix/PersonalHub/main` per l'audit PH. Non rifare l'audit e non implementare nuove feature. Correggi soltanto failure concrete necessarie a far passare questi gate. **Niente bump di `version.txt`, niente package reale Pixel, niente Telegram/release finale.**

# Starting point verificato
La modifica originaria ha già portato `version.txt` a **45**. Boundary modificati:
- root `build.gradle.kts`: root `check` deve aggregare i check dei moduli;
- `PersonalHubApplication.kt`, `HubAutoExport.kt`, `HubAutoExportStartupTest.kt`: startup ordinato/isolato e auto-export retryable;
- `MainActivity.kt`, `HubTemporalSearchScreen.kt`: system back e filtri temporali coerenti/non vuoti;
- `SostanzeRepository.kt`, `SostanzeCampaignTest.kt`: stock insufficiente e quantità non finite non registrano intake;
- `TimeFenceTimerScheduler.kt`, `TimeFenceTimerReceiver.kt`: errori alarm osservabili e lavoro receiver fuori main thread;
- `SostanzeNotificationScheduler.kt`: tap reminder apre direttamente Sostanze;
- `CallSystemOverlayController.kt`: una chiamata senza overlay permission non apre automaticamente Settings.
Parti solo da questi file; usa `.codex/CODE_MAP.tsv` solo se un failure punta altrove.

# Esegui
1. Acquisisci il lock PH per `641904`. Fai un solo fetch/pull fast-forward di `origin/main`; worktree incompatibile => `BLOCKED`, niente stash/reset/force.
2. Gate host in **una sola invocazione Gradle**: `./gradlew check :app:assembleQa --no-configuration-cache`. Il root `check` deve realmente eseguire i lifecycle `check` dei moduli oltre a `checkArchitectureBoundaries`. Non ripetere task già PASS.
3. Se il gate fallisce, individua il primo failure concreto e applica il fix minimo solo nei file coinvolti; niente refactor/cleanup/audit generale, niente retry identico senza nuova evidenza. Mantieni `version.txt=45`.
4. Solo dopo PASS host, avvia il solo emulatore canonico con `tools/android_emulator_control.py`. Installa l'APK `.qa` appena costruito, senza nuova build. QA mirata:
   - Home → Context, Cerca e Registro: il **system back** torna alla Home senza terminare PH;
   - Cerca: non è possibile lasciare zero moduli selezionati; un deep link con soli moduli sconosciuti non produce uno stato visivo "nessun filtro" che poi significhi "tutti";
   - avvio/restart `.qa`: nessun crash immediato legato allo startup post-frame;
   - se esiste già un helper/test mirato per timed-session alarm/receiver, overlay chiamata o notification content-intent, usa quello; altrimenti limita il gate a una verifica emulator economica e deterministica, senza costruire nuova infrastruttura di test.
   Usa `tools/android_ui_summary.py`/`--match` per evidenza; niente dump XML salvo blocker.
5. Le regressioni automatiche devono provare almeno: retry startup auto-export; Sostanze stock=0/stock<dose/`NaN` senza mutazioni. Non creare dati personali sul device per duplicare test già coperti.
6. Disinstalla sempre `.qa`, ferma l'emulatore se lo hai avviato, commit/push solo eventuali fix indispensabili. Rilascia sempre il lock PH.

# PASS / stop
PASS = root check aggregato + assembleQa + regressioni mirate + QA back/filter/startup `.qa` + cleanup. Appena PASS, STOP: niente audit aggiuntivo, niente Pixel reale, niente APK finale, niente altro task.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 641904 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 641904`

Output ≤7 righe: RESULT, root gate, regressioni, QA back/filter/startup, Timer/notifiche/overlay, SHA/fix, blocker/cleanup.
