[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=739214 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Creare una sola toolbox riutilizzabile per i task PersonalHub, eliminando tre costi ricorrenti: scoperta target ADB, setup/test widget fragile e consegna APK Telegram via tentativi/inline Python.

Assorbe i vecchi prompt `308941`, `742615`, `271905`. È infrastruttura: nessun bump versione, APK release o modifica funzionale solo per questo task.

# A — Android target preflight
Implementa un comando/script canonico che con una sola procedura bounded:
- classifichi device ADB fisici/emulatori e riconosca Pixel 8a, TCL e AVD Pixel_8a tramite configurazione esistente, non transport ID fragili;
- riusi un target valido già disponibile;
- faccia solo recovery ADB sicura e limitata;
- avvii l'AVD esistente solo se fallback emulatore è consentito e serve;
- distingua chiaramente `Pixel fisico richiesto ma assente` da `fallback consentito`;
- emetta output machine-friendly consumabile dai prompt futuri.

# B — widget QA
Parti dall'instrumentation già funzionante e crea un harness/helper canonico che:
- eserciti tap widget anche su click activity non esportate;
- crei fixture Kotlin/domain, non SQL/XML shell;
- verifichi risultato e messaggio success/failure a un boundary testabile, senza toast scraping UIAutomator;
- offra un solo comando Gradle/wrapper QA riutilizzabile;
- provi: un tap=>una entry, failure=>nessun successo, due target distinti.

# C — Telegram file-only
Sul notifier condiviso, rendi canonico `python3 -m telegram_notify --file <path>` (o equivalente già stilisticamente previsto): nessun title/message dummy, caption vuota, path invalido rifiutato prima della rete, compatibilità text/caption preservata, nessun secret in output. Aggiorna il bootstrap PersonalHub a usare solo questo comando. Non cambiare destinazione Telegram.

# Verification
Una sola passata mirata: test parser Telegram senza invii duplicati; preflight contro target correnti + un caso di assenza simulato; harness widget su un target disponibile. Niente audit Android/notifier, niente broad suite. PASS solo se i tre entrypoint sono documentati e riutilizzabili. Commit/push solo i repo modificati; roadmap e STOP.

Output: `PROMPT_ID`, `RESULT`, tre comandi canonici, target/preflight result, widget representative test, Telegram compatibility, file/SHA, blocker.
