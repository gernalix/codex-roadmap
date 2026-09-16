[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=684731 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=5/5 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Esegui l'UNICA release finale della campagna PersonalHub: produci un APK `release` realmente shrunk, misurane la dimensione, verifica sul Pixel anche il Random Timer della fase 4/5 e consegna esattamente lo stesso artefatto. Evita qualsiasi build/install/delivery duplicato.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`;
- la fase 4/5 (`PROMPT_ID=232198`) deve essere già PASS prima di questa fase;
- `app/build.gradle.kts`: `release` ha già `isMinifyEnabled = true`, `isShrinkResources = true` e `proguard-android-optimize.txt`; non reimplementare R8/ProGuard;
- `app/proguard-rules.pro` esiste: modificalo solo in risposta a un errore release/smoke concreto;
- `tools/android_pixel_apk.py` accetta `--metadata app/build/outputs/apk/release/output-metadata.json`;
- `tools/deliver_personalhub_apk.py` accetta un path APK arbitrario;
- baseline osservata dall'utente: APK ~146 MB, probabilmente debug/non shrunk. Se un debug già esiste, misuralo; non rebuildarlo solo per la baseline.

Niente discovery generale, README/roadmap/spiegazioni/MegaVault salvo blocker concreto.

# Esecuzione minima
1. `python3 tools/personalhub_task_lock.py acquire --prompt-id 684731`; failure => `BLOCKED`, niente attesa.
2. Worktree pulito → `git fetch --prune origin && git pull --ff-only origin main`; registra la base. Non rebase/merge.
3. Verifica una volta che la configurazione `release` sopra sia ancora presente. Se sì, non toccarla.
4. Incrementa `version.txt` una sola volta secondo la convenzione esistente della release finale.
5. Costruisci una sola release iniziale:
   `./gradlew --no-configuration-cache --quiet --console=plain :app:assembleRelease`
6. Risolvi l'APK da `app/build/outputs/apk/release/output-metadata.json`; registra byte/MiB e delta rispetto al debug esistente o alla baseline ~146 MB.
7. Se la riduzione è materialmente evidente, usa quell'artefatto come `FINAL_APK`. Se resta sorprendentemente vicino alla baseline, usa UN solo analyzer locale già disponibile (`apkanalyzer`, `aapt` o equivalente) per trovare i componenti dominanti. Applica al massimo un fix evidente/localizzato/a basso rischio; solo in quel caso è ammessa UNA seconda build release, che sostituisce `FINAL_APK`. Se non esiste un fix sicuro, `FAIL` con massimo 3 cause dominanti: niente audit dipendenze generale.
8. Installa ESATTAMENTE `FINAL_APK` sul Pixel con `python3 tools/android_pixel_apk.py install --metadata app/build/outputs/apk/release/output-metadata.json` (oppure il path finale se una seconda build controllata lo richiede). Nessun uninstall/clear.
9. Sul Pixel fai solo questa QA finale: launch smoke + Random Timer breve (~1 min), app in background/swipata via senza force-stop, notifica entro tolleranza pratica <=5 s da `expectedEndMs`, tap → dialog corretto, reopen senza duplicato. Niente esplorazione UI generale.
10. Se le istruzioni/helper canonici impongono ancora un APK debug come artefatto finale, cambia SOLO quei riferimenti necessari affinché le future release usino `release`; riusa gli helper esistenti, non crearne altri.
11. Consegna lo STESSO `FINAL_APK` già testato:
   `python3 tools/deliver_personalhub_apk.py "$FINAL_APK" --version "$(cat version.txt)" --telegram-title "PersonalHub APK"`
12. Prima del commit/push fai UNA `git fetch origin`; se `origin/main` è avanzato dalla base => `BLOCKED`, niente rebase/merge/rerun. Altrimenti commit/push una volta. Rilascia sempre il lease.

# Acceptance
PASS se: release build firmato riesce; R8/resource shrinking restano attivi; APK è materialmente più piccolo della baseline; lo stesso `FINAL_APK` viene installato, supera smoke + Random Timer sul Pixel e viene consegnato senza rebuild; la pipeline futura usa release anziché debug.

# Non-goal
Niente nuovo minifier/script di build, dependency upgrades, split APK/AAB/Play Store, refactor, cleanup, suite generale o seconda QA di feature già coperte.

# Stop
Dopo PASS tecnico esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 684731 --confirm-executed`

Stop immediato dopo PASS/BLOCKED/FAIL; niente audit post-PASS.

Prima riga output `RESULT=PASS|BLOCKED|FAIL`; massimo 6 righe includendo `APK_BEFORE`, `APK_RELEASE`, delta %, `PIXEL`, `DELIVERY/PUSH`.