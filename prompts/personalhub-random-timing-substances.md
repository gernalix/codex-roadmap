[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=381527 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD | campaign_id=PH_FINAL_20260912 | type=Goal`

# Goal — fase 1/3
Completa in PH, con diff minimo: (A) date picker prescrizioni Substances; (B) Random timer; (C) Random alerts Timer+Substances; (D) bulk end Since When; (E) residui UI/People già localizzati. Nella **stessa** build/QA assorbi anche la verifica locale dei fix audit già pushati su `main` e l'integrazione/verifica del fix Places già pushato su `fix/places-accuracy-aware-checkin`, senza aprire gate separati. **Niente bump/final APK/Pixel main/Telegram**.

# Starting point
Riusa boundary esistenti: `EpochDayPickerField`; `TimeFence*`/`AlertsCapsuleViewModel`; `SostanzeNotificationScheduler`+receiver/restore/ViewModel; `SinceWhenCapsuleViewModel`/`LifePeriodsScreen`. Stock=0 intake è già corretto: non cambiarlo. Home conserva l'unica versione host. `SoldiTheme` esiste. People call overlay ha già intent/gate/redaction: verifica, non ri-auditare.

È già pushato sul branch remoto `fix/places-accuracy-aware-checkin` un fix strettamente localizzato a Places: `CheckInPolicy` usa `accuracyM` con cap, `FusedLocationCapsule` richiede fix recenti/≤50 m e usa `PRIORITY_HIGH_ACCURACY`, con `CheckInAccuracyPolicyTest` che copre il caso reale tipo “Carlo Visda” (`radius_m=40`). Integra quel branch una sola volta dopo il fetch; se è già contenuto nel branch di lavoro/main, non rifare merge/cherry-pick. Non reimplementare né ampliare il fix salvo test failure concreta.

Sono già pushati e vanno **solo verificati nello stesso gate finale di questa fase**: root `check` aggregato; startup/auto-export retryable; system-back e filtri Cerca; Sostanze stock insufficiente/NaN senza mutazioni; errori Timer alarm osservabili + receiver fuori main thread; tap reminder Sostanze; overlay chiamata senza apertura automatica Settings. Non rifare l'audit e non esplorare oltre questi boundary salvo failure concreta.

# Implementa
- **Substances dates:** sostituisci solo i 2 epoch-day raw con `EpochDayPickerField`; new=oggi, edit round-trip, campi indipendenti; no migration.
- **Random timer:** Home card, max minuti >0 default 60, un run; target `0<target<=max` invisibile UI/accessibility/notifica fino al submit; persistenza+process death/reboot riusando scheduling; scadenza→`Quanto tempo è passato?`→input numerico→solo submit mostra reale+rapporto. Clock/random iniettabili, zero wait reali nei test.
- **Random alerts:** per pulsante: enabled,N>0, per-hour/day, stable identity persistita; master OFF cancella future senza perdere config, ON solo futuro; esattamente N istanti unici/finestra; reboot-safe/no duplicate/stale cancel su config/delete; notifica identifica modulo+pulsante e NON esegue/registra azione. Riusa scheduler esistenti, niente secondo motore.
- **Since When:** multiselect soli attivi; `Termina selezionati ora` cattura 1 timestamp e assegna stesso `endMs>startMs`; singola operazione bulk + un refresh/persist/backup; selection saveable/clear success/cancel; no migration.
- **UI/People:** rimuovi solo versioni visibili già localizzate: Timer `AppPatchVersion/versione_patch_v`, Substances `BuildConfig.VERSION_NAME`, Places Home version item/footer, WordPulse `v${BuildConfig.VERSION_NAME}`/duplicato root, Soldi root, People `patch-version.txt/loadPatchVersion()` visibile. Non eliminare helper tecnici usati altrove. Risultato: Home PH=1 versione host, root moduli=0. In `SoldiActivity` usa `SoldiTheme` al posto del root `MaterialTheme` se ancora presente.

# Un solo gate locale consolidato
1. Acquisisci lock PH; un solo fetch/pull fast-forward. Integra una sola volta `origin/fix/places-accuracy-aware-checkin` se non già contenuto, poi implementa il resto senza build intermedie salvo errore di compilazione inevitabile.
2. **Una sola invocazione host finale:** `./gradlew check :app:assembleQa --no-configuration-cache`. Deve coprire sia le nuove regressioni della fase sia i fix audit già pushati e `CheckInAccuracyPolicyTest`; non rilanciare test PASS separatamente.
3. Solo dopo PASS host, **una sola sessione QA** sul solo emulatore canonico `.qa`, riusando l'APK appena costruito. Verifica insieme:
   - picker + Random timer/alerts + bulk Since When + version matrix/Soldi theme;
   - Home→Context/Cerca/Registro: system-back torna alla Home;
   - Cerca non può restare con zero moduli; deep link sconosciuti non producono falso “nessun filtro”;
   - restart `.qa` senza crash startup;
   - Timer/notifiche/overlay solo tramite helper/test già esistenti se disponibili; non costruire nuova infrastruttura QA.
   - Non aprire una sessione device separata per simulare l'errore GPS di Places: la regressione accuracy-aware è coperta dal test unitario mirato e dal normale build gate; fai runtime Places aggiuntivo solo se quel test/build fallisce o emerge un'anomalia concreta.
4. Disinstalla `.qa`, ferma emulatore se avviato, commit/push PH; non cambiare `version.txt`.

# Stop
PASS = feature fase 1 + fix audit già esistenti + fix Places accuracy-aware coperti dallo stesso host gate/QA necessario + cleanup. Side issue non bloccanti: segnala senza investigare. **Nessun audit successivo e nessun nuovo prompt di verifica per questa fase.**

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 381527 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 381527`

Output ≤8 righe: RESULT, picker, random timer/alerts, SinceWhen, UI/People, audit+Places regressions, test/QA, SHA/blocker.