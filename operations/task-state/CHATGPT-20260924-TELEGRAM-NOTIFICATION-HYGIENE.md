# Operational task state — Telegram notification hygiene

TASK_ID: CHATGPT-20260924-TELEGRAM-NOTIFICATION-HYGIENE
Updated: 2026-09-24 13:36 Europe/Copenhagen

## Objective
Automatizzare la raccolta della chat Telegram usata per le notifiche tecniche e usare la cronologia reale come evidenza per ridurre rumore, duplicati, messaggi incomprensibili e flapping senza export manuali.

## Constraints
- Fedora user service/timer; nessun processo model-driven always-on.
- Archivio Git privato; nessun token, session file, API hash, OTP, 2FA o credenziale nel repository/checkpoint.
- Export incrementale e resumable; nessun commit/push quando non ci sono nuovi messaggi.
- Collector separato da telegram_insert_bot.
- Correggere i producer reali, non filtrare a valle le notifiche.
- Testi futuri comprensibili a un non tecnico: brevi, autoesplicativi, ben formattati, con emoji utili.
- Stesso incidente invariato => silenzio; recovery una sola volta dopo un alert realmente inviato.
- Rispettare la single-active-recovery-lane globale: il timer può continuare come servizio non-model, ma nessun nuovo task modello Telegram va lanciato in parallelo alla master lane.

## Plan / checklist
- [x] Allocare/materializzare il task iniziale 422308.
- [x] Implementare collector incrementale + test in fedora-system-monitor.
- [x] Creare il repo dati privato gernalix/telegram-notification-history.
- [x] Installare service+timer systemd --user e lock anti-overlap.
- [x] Completare autorizzazione Telegram account-level senza versionare segreti.
- [x] Correggere login con TELEGRAM_PHONE vuoto; commit 9d736aa.
- [x] Correggere runtime reale e persistere i fix; commit 5d8ed32.
- [x] Verificare test mirati: 6/6 PASS + py_compile + git diff --check.
- [x] RUN1 reale: 4.244 messaggi archiviati e pushati.
- [x] RUN2 reale: new_messages=0 e commit remoto invariato.
- [x] Abilitare timer ogni 15 minuti; enabled+active.
- [x] Verificare dal connettore GitHub che repo privato e archive/state.json siano leggibili.
- [ ] Riparare la collisione di identità del follow-up: 333860 non canonico; 966124 ID remoto canonico. Mutation roadmap #1056 deve sostituire 333860 con 966124 e poi 966124 va materializzato.
- [ ] Quando la master recovery arriva a Phase 4, eseguire SOLO 966124 per integrare su main i fix già verificati del branch task/422308 e chiudere il source/runtime gate.
- [ ] Lasciare accumulare cronologia reale sufficiente.
- [ ] Classificare notifiche verbose/incomprensibili/inutili/ripetute/flapping.
- [ ] Applicare fix mirati ai singoli producer; niente broad refactor.
- [ ] Rivalutare la policy legacy del prefisso project_id visibile e spostarlo a metadata se non serve all'utente.

## Current step
Collector runtime operativo e non-model. Il lavoro modello è parcheggiato per rispettare la master recovery. In parallelo va completata solo la correzione amministrativa dell'identità del follow-up: 966124 è il PROMPT_ID canonico remoto; 333860 deve restare superseded/non azionabile.

## Verified facts
- Baseline storica: PROMPT_ID 417826 ha già effettuato una prima signal-hygiene.
- PROMPT_ID 422308 è terminale BLOCKED storico, ma il suo precedente prerequisito umano è ormai soddisfatto.
- Branch sorgente: gernalix/fedora-system-monitor task/422308; ultimo commit pushato verificato 5d8ed32.
- Test collector dopo i fix live: 6/6 PASS; py_compile e diff-check PASS.
- Sessione Telegram account-level autorizzata.
- Target reale delle notifiche rumorose: datasette_alerts_bot; il vecchio chat_id -1004426028673 risultava non valido per il bot principale.
- RUN1 PASS: new_messages=4244; data commit 99a9952479074f56095586a6ed3fb210111496db.
- RUN2 PASS: new_messages=0; origin/main invariato.
- Data repo gernalix/telegram-notification-history verificato PRIVATE e leggibile via GitHub connector.
- archive/state.json remoto contiene last_message_id=372496.
- telegram-notification-history.timer è enabled+active e schedulato ogni 15 minuti.
- L'allocatore remoto MegaVault per chatgpt-telegram-history-runtime-closure-20260924-v1 ha assegnato 966124.
- Il fallback locale aveva erroneamente restituito 333860 allo stesso request_id e quel prompt era stato registrato prima del ritorno remoto.
- Mutation roadmap #1056 corregge la collisione tramite replacement 333860 -> 966124; la materialization Issue MegaVault #104 per 333860 è stata chiusa not_planned.

## Decisions
- Il runtime collector resta attivo mentre la master recovery procede perché è un servizio non-model e non muta i repo sovrapposti alla lane attiva.
- Non rilanciare 422308.
- Non lanciare 333860.
- Il solo follow-up valido è 966124, dopo applicazione/materializzazione canonica e quando Phase 4 della global recovery diventa la lane attiva.
- L'audit delle notifiche userà la cronologia Git reale.
- Le correzioni successive devono avvenire nei producer reali.

## Completed
- Implementazione collector, data repo privato, autorizzazione, runtime deploy e validazione E2E.
- RUN1/RUN2 e no-op semantics verificate.
- Timer periodico attivo.
- Repo dati accessibile da ChatGPT tramite GitHub connector.
- Fix live persistiti sul branch task/422308 fino a 5d8ed32.
- Richiesta errata di materializzazione 333860 chiusa prima che il worker la applicasse.

## Remaining
- Attendere/applicare roadmap mutation #1056 e materializzare 966124.
- Integrare i fix sorgente su main tramite 966124 quando la master lane arriva a Phase 4.
- Accumulare e analizzare cronologia reale.
- Correggere i producer rumorosi e verificare una nuova finestra di notifiche post-fix.

## Blockers
- Nessun blocker runtime del collector.
- Blocker amministrativo corrente: collisione allocator locale/remoto da riconciliare completamente con 966124 prima di qualunque source-closure task.

## Evidence
- fedora-system-monitor task/422308: f577f66, 9d736aa, 5d8ed32.
- gernalix/telegram-notification-history commit 99a9952479074f56095586a6ed3fb210111496db.
- GitHub readback archive/state.json: last_message_id 372496.
- systemd runtime readback: RUN1 4244, RUN2 0, timer enabled+active.
- MegaVault Issue #103: remote allocation => PROMPT_ID 966124.
- codex-roadmap Issue #1050: accidental local-fallback prompt 333860.
- codex-roadmap Issue #1056: canonical replacement 333860 -> 966124.
- MegaVault Issue #104: wrong 333860 materialization closed not_planned.
- completed/telegram-notification-signal-hygiene.md baseline 417826.

## Acceptance criteria
Collector lane source/runtime closure is complete only when runtime remains healthy/incremental, no secret is versioned, source fixes are integrated on fedora-system-monitor main through canonical 966124, 333860 is non-actionable, 966124 is canonical/materialized and terminal PASS, and the history-based audit produces producer-specific fixes.

## Next action
Do not launch a Telegram model task now. Verify roadmap mutation #1056 applies, materialize canonical PROMPT_ID 966124, and keep it parked. When the global master reaches Phase 4, claim only 966124, integrate the already-verified task/422308 changes, run its bounded gates/readback, finalize PASS, then begin the history-based notification audit.
