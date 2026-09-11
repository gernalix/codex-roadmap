[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=739214 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Completare e verificare localmente la toolbox QA PersonalHub già in gran parte preparata sul remoto. **Non rifare inventory generale e non riscrivere il widget harness**. È tooling-only: nessun bump versione, APK release o modifica funzionale.

# Stato remoto da riusare
Parti dal `main` corrente di `gernalix/PersonalHub`.

Già presenti:
- `tools/android_target_preflight.py`: parser `adb devices -l`, classificazione machine-readable di Pixel 8a / TCL 6102H / emulator senza `transport_id`, `--target` e distinzione `pixel_physical_required_but_absent`;
- `tools/test_android_target_preflight.py`: test parser/classificazione/offline;
- `QuickEventWidgetTapRunner` + `QuickEventWidgetClickActivity`: boundary già esistente che esegue i tap senza richiedere Activity esportata e senza toast scraping;
- `QuickEventWidgetTapRunnerTest`: già copre tap=>entry, failure=>nessun successo e due target distinti.

MegaVault ha già evidenza che `telegram_notify.py` è infrastruttura condivisa; non confonderla con `telegram_insert_bot` o `android_build_telegram_watch_v1`.

# A — completa solo il preflight ADB
Estendi **lo script esistente**, senza crearne un secondo:
- se la prima `adb devices -l` fallisce, consenti al massimo un recovery `adb start-server` e un solo retry;
- per emulator live risolvi l'AVD con `adb -s SERIAL emu avd name`, non con transport ID;
- riusa un target valido già presente;
- avvia l'AVD esistente `Pixel_8a` solo se il target richiesto lo consente e serve davvero; polling bounded, niente loop indefiniti;
- Pixel fisico richiesto senza fallback deve restare BLOCKED, mai sostituito silenziosamente dall'emulatore;
- preserva JSON machine-friendly.

Aggiungi/estendi solo i test Python necessari per recovery singolo, fallback consentito/non consentito e AVD matching.

# B — widget QA: solo entrypoint canonico
Non ridisegnare runner/fixture. Se manca un singolo comando documentato, aggiungi il wrapper/comando minimo che esegue soltanto `QuickEventWidgetTapRunnerTest`. Verifica i tre casi già presenti; niente UIAutomator/toast scraping e niente nuova instrumentation salvo failure concreta.

# C — Telegram file-only
Risolvi **una volta** il package condiviso installato sul Fedora runtime (es. import Python/metadata già installati; niente repo sweep). Sul notifier condiviso rendi canonico:

`python3 -m telegram_notify --file <path>`

Requisiti: caption vuota senza title/message dummy; path invalido rifiutato prima della rete; compatibilità testo/caption esistente preservata; nessun secret stampato. Non cambiare destinazione Telegram. Se il package sorgente non è in un repo modificabile già noto localmente, riporta il path/owner esatto come blocker invece di duplicare il notifier in PersonalHub.

# Verification
Una sola passata:
1. test Python preflight;
2. test `QuickEventWidgetTapRunnerTest` soltanto;
3. preflight contro i target correnti + caso Pixel-assente/fallback simulato;
4. test parser Telegram, poi **al massimo un** invio file reale se serve a verificare la compatibilità.

Niente broad suite, build APK, device navigation QA o audit dei repository. Correggi codice solo su failure concreta. PASS quando i tre entrypoint sono riutilizzabili/documentati; commit/push solo repo realmente cambiati, archivia roadmap e STOP.

Output conciso: `PROMPT_ID`, `RESULT`, comando preflight + target rilevato, comando widget QA + esito, comando Telegram + esito, file/SHA modificati, blocker.
