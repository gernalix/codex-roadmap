[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=684731 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=5/5 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Esegui l'UNICA release finale PersonalHub: valida il fix Random Timer già presente su `main`, produci un APK `release` realmente shrunk, installa e prova ESATTAMENTE quell'artefatto sul Pixel e consegnalo senza rebuild duplicati.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`;
- `origin/main` contiene `a0d1ba094681c192d9d96b25535b93ae628ae4cc` o successivo;
- il fix Random Timer è già implementato remotamente: `expectedEndMs` resta autorevole, `TimedSessionSupport.syncScheduledAlarms()` include gli ID di `RandomTimerStore`, il restore boot/update riusa lo stesso scheduler e `TimeFenceTimerReceiver` chiude idempotentemente a `expectedEndMs`;
- test regressivo già presente: `TimeFenceAlarmReconciliationTest.randomTimerRestoreSchedulesFutureDeadlineWithoutTimedTag`;
- GitHub Actions `Architecture boundaries` su `a0d1ba...` è PASS;
- `app/build.gradle.kts`: `release` ha già R8/resource shrinking; non reimplementare minificazione;
- baseline utente APK ~146 MB, probabilmente debug/non shrunk;
- helper canonici: `tools/android_pixel_apk.py` e `tools/deliver_personalhub_apk.py`.

Niente audit repo-wide, README/roadmap/MegaVault o emulatori salvo blocker concreto.

# Esecuzione minima
1. `python3 tools/personalhub_task_lock.py acquire --prompt-id 684731`; failure => `BLOCKED`, stop. Rilascia sempre il lease.
2. Worktree pulito → UNA `git fetch --prune origin` + `git merge --ff-only origin/main`. Se dirty non pertinente/divergente: `BLOCKED`.
3. Verifica solo che `a0d1ba094681c192d9d96b25535b93ae628ae4cc` sia antenato di HEAD.
4. Esegui UNA sola volta il test host mirato:
   `./gradlew --quiet --console=plain :feature:multitimetracker:testDebugUnitTest --tests com.example.multitimetracker.TimeFenceAlarmReconciliationTest`
   Se fallisce, correggi solo il leaf Random Timer indicato dal report e rilancia solo questo test. Niente suite generale.
5. Incrementa `version.txt` una sola volta secondo convenzione esistente e costruisci UNA release iniziale:
   `./gradlew --no-configuration-cache --quiet --console=plain :app:assembleRelease`
6. Risolvi `FINAL_APK` da `app/build/outputs/apk/release/output-metadata.json`; registra byte/MiB e delta rispetto al debug esistente o ~146 MB. Se la riduzione è evidente, non analizzare altro. Solo se resta sorprendentemente vicino alla baseline usa UN analyzer locale già disponibile e al massimo un fix evidente/localizzato + UNA seconda release.
7. Installa ESATTAMENTE `FINAL_APK` sul Pixel senza uninstall/clear usando l'helper canonico.
8. Fai una sola QA Random Timer reale che copra anche il restore: avvia un Random Timer breve, porta l'app fuori foreground/swipala via senza force-stop e riavvia il Pixel prima o intorno al deadline. Dopo boot il timer deve risultare chiuso a `expectedEndMs` e deve comparire una sola notifica `Quanto tempo è passato?`; tap → Timer/Now/dialog corretto; reopen non deve duplicare. Se il deadline cade mentre il device è spento, è valido il path overdue purché finalizzi/notifichi una sola volta dopo boot.
9. Launch smoke minimo degli altri componenti solo quanto necessario a confermare che l'APK release si apre. Niente esplorazione UI generale.
10. Consegna lo STESSO `FINAL_APK` già testato con `tools/deliver_personalhub_apk.py`; nessun rebuild dopo la QA.
11. Prima del commit/push fai UNA `git fetch origin`; se `origin/main` è avanzato dalla base, `BLOCKED`, niente rebase/merge/rerun. Altrimenti commit/push una volta.

# Acceptance
PASS se test Random Timer mirato PASS, release shrunk è materialmente più piccola della baseline, lo stesso APK installato supera smoke + Random Timer con reboot/restore senza duplicati ed è lo stesso artefatto consegnato.

# Non-goal
Niente nuovo scheduler/minifier, emulatori, dependency upgrade, suite generale, AAB/Play Store, refactor o QA non pertinente.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 684731 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 684731`

Stop immediato dopo PASS/BLOCKED/FAIL. Output massimo 7 righe: `RESULT`, `RANDOM_TIMER_TEST`, `APK_BEFORE`, `APK_RELEASE`, `PIXEL_RANDOM_TIMER`, `DELIVERY`, `PUSH/BLOCKER`.