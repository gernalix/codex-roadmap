# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, nello stesso ordine della roadmap, una spiegazione semplice di ciò che farà ogni prompt.

## 1. [[prompts/telegram-notification-signal-hygiene|telegram-notification-signal-hygiene]]

Riduce il rumore Telegram visto oggi: niente messaggi per piccole oscillazioni disco, snapshot Facebook senza cambiamenti, normali push Codex o ogni singolo punto percentuale di quota. Migliora invece i messaggi T7 distinguendo disco assente da vero errore, deduplica i problemi finché non cambiano, rende i `senza PROMPT_ID` un unico alert utile e aggiunge soglie/digest Codex più informativi. Evita anche test Telegram PersonalHub ripetuti quando la readiness è già valida.

## 2. [[prompts/codex-workflow-foundation-hardening|codex-workflow-foundation-hardening]]

Accorpa due lavori che riducono il costo di quasi tutti i task futuri: rende la roadmap sicura anche con checkout locali sporchi e impedisce che Codex archivi il prompt sbagliato o committi modifiche altrui; inoltre aggiunge a MegaVault comandi stabili per registrare e validare un evento senza riscoprire ogni volta schema SQLite e INSERT manuali.

## 3. [[prompts/personalhub-qa-delivery-tooling|personalhub-qa-delivery-tooling]]

Crea in un solo passaggio gli strumenti riutilizzabili per i task PersonalHub: preflight ADB per scegliere Pixel/TCL/emulatore, harness stabile per testare i widget senza setup SQLite manuale o toast scraping, e un comando Telegram file-only per consegnare l'APK. Non cambia funzioni dell'app e non richiede una release.

## 4. [[prompts/personalhub-context-composer-temporal-search|personalhub-context-composer-temporal-search]]

Unisce Composer e Cerca perché entrambi devono capire persone, luoghi, Timer, Soldi, Substances e WordPulse. Codex inventaria adapter e semantica temporale una sola volta: Composer crea Context persistenti con suggerimenti e rilevazioni, mentre Cerca ricostruisce in sola lettura ciò che è successo in un intervallo senza creare collegamenti permanenti.

## 5. [[prompts/personalhub-random-timing-substances|personalhub-random-timing-substances]]

Unisce in un solo giro Timer/Substances tre lavori che condividono impostazioni, notifiche, scheduling e QA: Random timer per misurare il tempo percepito, Random alerts configurabili per i pulsanti Timer/Substances e le piccole correzioni Substances su calendari prescrizioni e registrazione dei pulsanti anche con stock zero.

## 6. [[prompts/personalhub-global-activity-register-safe-undo|personalhub-global-activity-register-safe-undo]]

Aggiunge un unico Registro attività per le modifiche di tutti i moduli, con cronologia paginata, filtri e annullamento sicuro. Riusa gli audit già presenti in Timer/Places, evita doppioni e registra l'undo come nuova operazione invece di cancellare la storia.

## 7. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]]

Viene eseguito dopo i task che possono cambiare lo schema, così controlla una sola volta lo schema finale. Costruisce un'unica catena autorevole di migrazioni, testa tutte le versioni storiche verso quella corrente e impedisce che un aggiornamento incompatibile o fallito sostituisca i dati con un database vuoto.

## 8. [[prompts/personalhub-ui-people-final-hardening|personalhub-ui-people-final-hardening]]

Chiude con un solo passaggio visuale/QA i lavori che non richiedono nuovi modelli dati: indicatore backup, versione PersonalHub coerente, dark mode sulle schermate mancanti e i tre bug del riquadro chiamate People. Un solo build/install e una sola navigazione finale evitano QA ripetuta.
