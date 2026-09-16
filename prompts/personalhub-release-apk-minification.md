[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=684731 | project_id=49 | campaign_id=personalhub-20260916-apk-size | phase=1/1 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Ridurre l’APK PersonalHub consegnato all’utente, oggi osservato intorno a 146 MB, usando prima di tutto la pipeline `release` già esistente invece di inventare nuova logica di minificazione.

# Starting point autoritativo
- repo/workdir: `/home/daniele/projects/PersonalHub`;
- `app/build.gradle.kts`: `release` ha già `isMinifyEnabled = true`, `isShrinkResources = true` e `proguard-android-optimize.txt`; quindi NON reimplementare R8/ProGuard;
- `app/proguard-rules.pro` esiste: non modificarlo senza un errore release/smoke concreto che lo richieda;
- `tools/android_pixel_apk.py` accetta già `--metadata`, quindi può risolvere/installare anche l’APK release passando `app/build/outputs/apk/release/output-metadata.json`;
- `tools/deliver_personalhub_apk.py` accetta già un path APK arbitrario: riusalo senza creare un nuovo delivery script;
- baseline utente: APK attuale ~146 MB, verosimilmente debug/non shrunk. Se l’APK debug corrente esiste già, misuralo con `stat`; NON rebuildare debug solo per ottenere la baseline;
- scope iniziale limitato ai file sopra e alle sole istruzioni canoniche che oggi impongono `assembleDebug` per l’APK finale. Niente esplorazione generale del repo.

# Task
1. Acquisisci il lease con `python3 tools/personalhub_task_lock.py acquire --prompt-id 684731`; failure => `BLOCKED`, niente attesa.
2. Con worktree pulito: `git fetch --prune origin && git pull --ff-only origin main`. Non rebase/merge.
3. Verifica rapidamente che la configurazione `release` sopra sia ancora presente. Se sì, non toccarla.
4. Costruisci UNA sola volta il release APK con:
   `./gradlew --no-configuration-cache --quiet --console=plain :app:assembleRelease`
5. Risolvi l’artefatto da `app/build/outputs/apk/release/output-metadata.json`; registra byte/MiB. Confrontalo con il debug esistente se già disponibile, altrimenti con la baseline osservata ~146 MB senza costruire un debug aggiuntivo.
6. Installa ESATTAMENTE quell’APK sul Pixel usando lo script esistente:
   `python3 tools/android_pixel_apk.py install --metadata app/build/outputs/apk/release/output-metadata.json`
   Riusa il serial restituito e fai solo un launch smoke essenziale; niente esplorazione UI generale.
7. Se build/install/launch PASS e la dimensione è materialmente inferiore alla baseline, rendi `release` l’artefatto canonico per le future consegne modificando SOLO le istruzioni/helper canonici strettamente necessari che oggi fissano il final APK a debug. Riusa `android_pixel_apk.py` e `deliver_personalhub_apk.py`; non creare nuovi script.
8. Se l’APK release resta sorprendentemente vicino a ~146 MB, allora e solo allora usa un singolo strumento locale già disponibile (`apkanalyzer`, `aapt`/`apkanalyzer files list`, o equivalente presente) per identificare i componenti dominanti. Applica solo un fix evidente, localizzato e a basso rischio; niente audit dipendenze generale, upgrade o refactor. Se non c’è un fix sicuro, riporta i principali responsabili e termina senza allargare lo scope.
9. Consegna lo STESSO APK release già testato con:
   `python3 tools/deliver_personalhub_apk.py "$FINAL_APK" --version "$(cat version.txt)" --telegram-title "PersonalHub APK"`
   Nessun rebuild per delivery.
10. Prima del commit/push finale fai UNA `git fetch origin`; se `origin/main` è avanzato dalla base => `BLOCKED`, niente rebase/merge/rerun. Commit/push una volta. Rilascia sempre il lease.

# Non-goal
Niente nuovo minifier/script di build, dependency upgrades, split APK/AAB/Play Store work, refactor, cleanup, ottimizzazioni prestazionali, test suite generale o modifiche fuori dal percorso release/delivery.

# Acceptance
PASS se: release build firmato riesce; R8/resource shrinking restano attivi; l’APK release è misurato e materialmente più piccolo della baseline ~146 MB; lo stesso artefatto viene installato e avviato sul Pixel e poi consegnato senza rebuild; la pipeline futura usa release anziché debug per il final APK. Se la riduzione non è materiale, PASS non è consentito: `FAIL` con dimensione misurata e massimo 3 cause dominanti, senza espandere l’indagine.

# Stop
Appena gli acceptance criteria sono verificati, STOP: niente audit post-PASS, niente test aggiuntivi, niente seconda build equivalente. Prova `roadmap_guard complete --prompt-id 684731 --dry-run`; se ready esegui complete. Altri errori guard => `BLOCKED`.

Prima riga output `RESULT=PASS|BLOCKED|FAIL`; massimo 6 righe, includendo `APK_BEFORE`, `APK_RELEASE`, delta percentuale e commit SHA se PASS.
