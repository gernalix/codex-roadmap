[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=381527 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

> Esecuzione diretta: questo file è il task Codex completo. Non eseguire `roadmap_guard.py select` e non rileggere roadmap/README/spiegazioni. Usa direttamente quanto segue come specifica autoritativa.

# Goal
Completare Random timer + Random alerts e cablare il date picker Substances già preparato. Riusa lo stato verificato qui sotto: **non rifare inventory di stock/date-picker/scheduler**. Un solo bump versione, una sola build/install/device QA.

# Stato già verificato sul remoto
- `SostanzeRepository.recordIntake()` registra già correttamente anche con `stockCurrent=0`: usa `appliedStockDelta=-minOf(stockCurrent, appliedDose)` e crea comunque l'intake; non modificare questa semantica.
- `SostanzeCampaignTest.zeroStockStillRecordsIntakeWithoutMakingStockNegative` copre già stock=0 + undo. Eseguilo, non riscriverlo.
- è già presente `feature/sostanze/.../ui/EpochDayPickerField.kt` con conversione `epoch-day ↔ UTC millis` e UI Material DatePicker;
- `EpochDayPickerFieldTest` copre il round-trip anche su date DST;
- stringhe EN/IT `order_date` e `prescription_date` sono già presenti.

## Infrastruttura scheduling già localizzata — NON inventariare
Timer:
- scheduler AlarmManager esistente: `feature/multitimetracker/src/main/java/com/example/multitimetracker/TimeFenceTimerScheduler.kt`;
- receiver/reboot/notifier: `TimeFenceTimerReceiver.kt`, `TimeFenceRestoreReceiver.kt`, `TimeFenceNotifier.kt` nella stessa package root;
- regole/stato: `capsules/alerts/controller/AlertsCapsuleViewModel.kt` e `capsules/alerts/core/TimeFenceAlarmReconciliation.kt`;
- test mirato esistente: `feature/multitimetracker/src/test/java/com/example/multitimetracker/TimeFenceAlarmReconciliationTest.kt`.

Substances:
- `feature/sostanze/src/main/java/com/gernalix/sostanze/notifications/SostanzeNotificationScheduler.kt` contiene già scheduler, `SostanzeNotificationReceiver` e `SostanzeNotificationRestoreReceiver`;
- il restore legge già lo stato notifiche dal DB e rischedula; riusa questo boundary, non creare un secondo motore/reboot path;
- UI/config: `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeViewModel.kt` + `SostanzeApp.kt`; persistence: `SostanzeRepository.kt`/DAO solo se serve davvero persistere nuova config.

Identità pulsanti Timer:
- parti solo da `capsules/quickevents/controller/QuickEventsCapsuleViewModel.kt`, `core/quickevent/QuickEventExecution.kt` e `persistence/QuickEventRepository.kt`;
- amplia a UI/model solo se manca concretamente uno stable ID necessario alla config.

I deep-link/notifier esistenti devono essere estesi, non sostituiti. Non cercare altri scheduler/reboot receiver prima di una failure concreta nei file sopra.

# A — completa solo il cablaggio Substances
In `feature/sostanze/src/main/java/com/gernalix/sostanze/ui/SostanzeApp.kt`, nei dialog prescrizione:
- sostituisci esclusivamente i due `OutlinedTextField` raw `Order epoch day` / `Prescription epoch day` con `EpochDayPickerField`, usando `R.string.order_date` / `R.string.prescription_date`;
- mantieni i valori nello stato come epoch-day, senza cambiare persistence/schema;
- new prescription: entrambe default=today;
- existing: round-trip esatto; cambiare una data non modifica l'altra.

Non toccare la logica stock salvo test failure concreto.

# B — Random timer
Home card + setting max minuti (default 60, >0). Un solo run attivo; target casuale `0<target<=max` completamente nascosto fino alla risposta, anche da accessibility/notification. Persisti run per process death/reboot **estendendo il scheduling già localizzato sopra**, non introducendo un scheduler parallelo. Alla scadenza notifica `Quanto tempo è passato?`; tap apre input numerico focalizzato. Solo dopo submit mostra elapsed reale e `perceived/actual`, persistendo attempt/timestamp/precisione sufficiente. QA usa clock/duration controllati, non attese reali.

# C — Random alerts Timer + Substances
Usa direttamente i boundary elencati in `Infrastruttura scheduling già localizzata`; **nessuna nuova inventory scheduler/reboot/deep-link**.

Per ogni button configurabile: enabled, N positivo, per-hour/per-day, persistiti per stable button identity. Master switch globale sospende/cancella delivery senza cancellare config e al ri-enable riparte dal futuro senza catch-up.

Con clock/random testabili genera esattamente N istanti unici per finestra attiva (60m/24h), persisti pending state, sopravvivi process death/reboot, cancella stale schedule su config/delete e impedisci duplicati. Notifica identifica modulo/button e NON esegue/recorda automaticamente l'azione.

Riusa `TimeFenceTimerScheduler`/restore per Timer e `SostanzeNotificationScheduler`/restore per Substances dove compatibile; estrai una piccola logica condivisa pura solo se elimina duplicazione reale senza creare un nuovo framework.

# Verification
Test focalizzati: `EpochDayPickerFieldTest` + stock0 esistente + picker wiring; hidden timer/one-active/deep-link/ratio/recreation; multi-button random alerts/master OFF-ON/N bounds/no duplicates. Riusa/estendi `TimeFenceAlarmReconciliationTest` per Timer e `SostanzeCampaignTest` per Substances quando sufficiente invece di creare harness paralleli. UNA smoke Pixel: date picker+stock0, Random timer breve controllato, un Timer + un Substances Random alert forzato. Niente broad QA.

PASS solo se A+B+C passano; poi un bump, una build APK, Pixel install, Telegram delivery, commit/push.

Su PASS, dopo il push del repo target, finalizza questo task nella roadmap con `python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 381527 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 381527`. `push_verified=git_push_exit_0` è prova sufficiente: non fare verifiche Git successive sulla roadmap e non aprire il task successivo. Su BLOCKED/FAIL non avanzare la roadmap. Stop immediato.

Output conciso: `PROMPT_ID`, `RESULT`, date-picker wiring/stock0 test, scheduler riusato, Random timer semantics, Random alerts/master, test/Pixel, version/APK/delivery, SHA, blocker.
