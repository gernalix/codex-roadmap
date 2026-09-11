[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=381527 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Completare Random timer + Random alerts e cablare il date picker Substances già preparato. Riusa lo stato verificato qui sotto: **non rifare inventory di stock/date-picker**. Un solo bump versione, una sola build/install/device QA.

# Stato già verificato sul remoto
- `SostanzeRepository.recordIntake()` registra già correttamente anche con `stockCurrent=0`: usa `appliedStockDelta=-minOf(stockCurrent, appliedDose)` e crea comunque l'intake; non modificare questa semantica.
- `SostanzeCampaignTest.zeroStockStillRecordsIntakeWithoutMakingStockNegative` copre già stock=0 + undo. Eseguilo, non riscriverlo.
- è già presente `feature/sostanze/.../ui/EpochDayPickerField.kt` con conversione `epoch-day ↔ UTC millis` e UI Material DatePicker;
- `EpochDayPickerFieldTest` copre il round-trip anche su date DST;
- stringhe EN/IT `order_date` e `prescription_date` sono già presenti.

# A — completa solo il cablaggio Substances
In `SostanzeApp.kt`, nei dialog prescrizione:
- sostituisci esclusivamente i due `OutlinedTextField` raw `Order epoch day` / `Prescription epoch day` con `EpochDayPickerField`, usando `R.string.order_date` / `R.string.prescription_date`;
- mantieni i valori nello stato come epoch-day, senza cambiare persistence/schema;
- new prescription: entrambe default=today;
- existing: round-trip esatto; cambiare una data non modifica l'altra.

Non toccare la logica stock salvo test failure concreto.

# B — Random timer
Home card + setting max minuti (default 60, >0). Un solo run attivo; target casuale `0<target<=max` completamente nascosto fino alla risposta, anche da accessibility/notification. Persisti run per process death/reboot usando scheduler esistente. Alla scadenza notifica `Quanto tempo è passato?`; tap apre input numerico focalizzato. Solo dopo submit mostra elapsed reale e `perceived/actual`, persistendo attempt/timestamp/precisione sufficiente. QA usa clock/duration controllati, non attese reali.

# C — Random alerts Timer + Substances
Inventaria scheduler/reboot/deep-link/settings e button identity **una sola volta**, partendo dai file indicati in `.codex/CODE_MAP.tsv`; amplia solo se manca un collaborator diretto.

Per ogni button configurabile: enabled, N positivo, per-hour/per-day, persistiti per stable button identity. Master switch globale sospende/cancella delivery senza cancellare config e al ri-enable riparte dal futuro senza catch-up.

Con clock/random testabili genera esattamente N istanti unici per finestra attiva (60m/24h), persisti pending state, sopravvivi process death/reboot, cancella stale schedule su config/delete e impedisci duplicati. Notifica identifica modulo/button e NON esegue/recorda automaticamente l'azione.

Riusa scheduler/reboot infrastructure esistente; niente secondo motore.

# Verification
Test focalizzati: `EpochDayPickerFieldTest` + stock0 esistente + picker wiring; hidden timer/one-active/deep-link/ratio/recreation; multi-button random alerts/master OFF-ON/N bounds/no duplicates. UNA smoke Pixel: date picker+stock0, Random timer breve controllato, un Timer + un Substances Random alert forzato. Niente broad QA.

PASS solo se A+B+C passano; poi un bump, una build APK, Pixel install, Telegram delivery, commit/push e STOP.

Output conciso: `PROMPT_ID`, `RESULT`, date-picker wiring/stock0 test, scheduler riusato, Random timer semantics, Random alerts/master, test/Pixel, version/APK/delivery, SHA, blocker.
