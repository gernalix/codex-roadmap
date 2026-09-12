[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=381527 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD | campaign_id=PH_FINAL_20260912`

> Esecuzione diretta. Non usare `roadmap_guard.py select`, non rileggere roadmap/README/spiegazioni. Fase 1/4 della campagna PersonalHub: **niente bump versione, final APK, Pixel main install o Telegram delivery**. Questi avverranno una sola volta nella fase finale.

# Goal
Completare: date picker prescrizioni Substances, Random timer, Random alerts Timer+Substances e chiusura multipla Since When. Riusa i boundary già localizzati; nessuna inventory generale.

# Starting point verificato
- stock=0 registra già l'intake correttamente ed è testato: non cambiare questa semantica;
- `EpochDayPickerField.kt` + test DST esistono già;
- Timer scheduling: `TimeFenceTimerScheduler/Receiver/RestoreReceiver/Notifier`, `AlertsCapsuleViewModel`, `TimeFenceAlarmReconciliation`;
- Substances scheduling: `SostanzeNotificationScheduler` + receiver/restore, `SostanzeViewModel`, `SostanzeApp`, `SostanzeRepository`;
- Timer quick-event identity: `QuickEventsCapsuleViewModel`, `QuickEventExecution`, `QuickEventRepository`;
- Since When: `SinceWhenCapsuleViewModel` + `LifePeriodsScreen`; `endMs=null` = attivo.

# Implementazione
## Substances date picker
Sostituisci solo i due campi raw order/prescription epoch-day con `EpochDayPickerField`; EN+IT già esistenti. New=oggi, edit round-trip esatto, cambiare una data non cambia l'altra. Nessuna migration.

## Random timer
Home card + max minuti configurabile (default 60, >0). Un solo run attivo. Target casuale `0<target<=max` totalmente nascosto da UI/accessibility/notification fino alla risposta. Persisti run e ripristinalo dopo process death/reboot riusando scheduling esistente. A scadenza notifica `Quanto tempo è passato?`; tap→input numerico; solo submit mostra elapsed reale e rapporto percepito/reale. Test con clock/random controllati, mai attese reali.

## Random alerts Timer + Substances
Per ogni pulsante configurabile: enabled, N positivo, per-hour/per-day, stable identity persistita. Master globale OFF cancella/sospende future delivery senza perdere config; ON riparte solo dal futuro. Genera esattamente N istanti unici per finestra con clock/random testabili, persisti pending state, reboot-safe, no duplicati, stale cancel su config/delete. Notifica identifica modulo+pulsante e **non registra/esegue** l'azione.

Riusa gli scheduler/restore già indicati; niente secondo motore.

## Since When bulk end
Selection mode per più periodi realmente attivi. Azione unica `Termina selezionati ora`: cattura un solo timestamp e assegna lo stesso `endMs` a tutti gli ID validi; `endMs>startMs`. ViewModel con una singola operazione bulk, refresh/persist/backup una volta. Selection state saveable e pulito su success/cancel. Nessuna migration.

# Verification fase
Esegui solo test mirati: picker + stock0; random timer hidden/one-active/recreation/deep-link; random alerts N/master/reboot/no-duplicate; Since When 2+ attivi con identico timestamp e singolo persist. Una QA isolata emulator/TCL solo per i flussi non dimostrabili dai test. Non installare il package reale sul Pixel.

Commit/push PersonalHub al PASS. **Non cambiare `version.txt`** e non produrre/consegnare l'APK finale: la campagna usa una sola versione nella fase `personalhub-database-schema-upgrade-safety`.

Su PASS completa solo questo prompt con `roadmap_guard.py complete --prompt-id 381527` (dry-run + real nello stesso comando). `push_verified=git_push_exit_0` basta; niente controlli roadmap successivi.

Output ≤7 righe: RESULT, date picker, Random timer, Random alerts, Since When bulk, test/QA isolata, SHA/blocker.
