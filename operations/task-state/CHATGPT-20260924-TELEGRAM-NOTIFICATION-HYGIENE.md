# Operational task state — Telegram notification hygiene

TASK_ID: CHATGPT-20260924-TELEGRAM-NOTIFICATION-HYGIENE
Updated: 2026-09-24 17:16 Europe/Copenhagen

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
- [x] Riparare la collisione di identità del follow-up: 333860 superseded/non azionabile; 966124 registrato e materializzato come ID remoto canonico.
- [x] Eseguire SOLO 966124 per integrare su main i fix verificati di task/422308 insieme a chatgpt/telegram-autodelete-archive, chiudere il source/runtime gate e rimuovere i branch assorbiti.
- [ ] Lasciare accumulare cronologia reale sufficiente.
- [ ] Classificare notifiche verbose/incomprensibili/inutili/ripetute/flapping.
- [ ] Applicare fix mirati ai singoli producer; niente broad refactor.
- [ ] Rivalutare la policy legacy del prefisso project_id visibile e spostarlo a metadata se non serve all'utente.

## Current step
Source/runtime closure completata tramite 966124. Lasciare accumulare cronologia reale; il prossimo lavoro è il successivo audit dei producer rumorosi, non un altro task di integrazione Telegram.

## Verified facts
- PROMPT_ID 966124 è terminale `completed`; `fedora-system-monitor/main` integra il collector tecnico, l'archivio auto-delete e il tracking relationship/block-state. Il checkpoint terminale dedicato riporta main `7c18ac68134b616228cc1e49f29b8be42eaebec4`, CI/runtime PASS e rimozione dei branch temporanei assorbiti.
- Baseline storica: PROMPT_ID 417826 ha già effettuato una prima signal-hygiene.
- PROMPT_ID 422308 è terminale BLOCKED storico, ma il suo precedente prerequisito umano è ormai soddisfatto.
- Lineage sorgente storico: `task/422308` fino a `5d8ed32`; il branch è stato assorbito e rimosso durante la chiusura 966124.
- Test collector dopo i fix live: 6/6 PASS; py_compile e diff-check PASS.
- Sessione Telegram account-level autorizzata.
- Target reale delle notifiche rumorose: datasette_alerts_bot; il vecchio chat_id -1004426028673 risultava non valido per il bot principale.
- RUN1 PASS: new_messages=4244; data commit 99a9952479074f56095586a6ed3fb210111496db.
- RUN2 PASS: new_messages=0; origin/main invariato.
- Data repo gernalix/telegram-notification-history verificato PRIVATE e leggibile via GitHub connector.
- archive/state.json remoto contiene last_message_id=372496.
- telegram-notification-history.timer è enabled+active e schedulato ogni 15 minuti.
- È operativo anche il collector separato per la chat con auto-delete 1 giorno: runtime locale SQLite+media, timer ogni 5 minuti e session lock condiviso. Il source è ormai integrato in `fedora-system-monitor/main` tramite 966124; include view umana, rendering chiamate e relationship/block-state tracking. I contenuti/peer restano locali e non vengono versionati.
- L'allocatore remoto MegaVault per chatgpt-telegram-history-runtime-closure-20260924-v1 ha assegnato 966124.
- Il fallback locale aveva erroneamente restituito 333860 allo stesso request_id e quel prompt era stato registrato prima del ritorno remoto.
- Mutation roadmap #1056 ha applicato replacement 333860 -> 966124; MegaVault Issue #105 ha materializzato 966124. La materialization Issue #104 per 333860 è stata chiusa not_planned.

## Decisions
- Il runtime collector resta attivo mentre la master recovery procede perché è un servizio non-model e non muta i repo sovrapposti alla lane attiva.
- Non rilanciare 422308.
- Non lanciare 333860.
- 966124 è stato completato e non va rilanciato. 333860 resta superseded/non azionabile.
- L'audit delle notifiche userà la cronologia Git reale.
- Le correzioni successive devono avvenire nei producer reali.

## Completed
- Implementazione collector, data repo privato, autorizzazione, runtime deploy e validazione E2E.
- RUN1/RUN2 e no-op semantics verificate.
- Timer periodico attivo.
- Repo dati accessibile da ChatGPT tramite GitHub connector.
- Fix live storici persistiti sul branch task/422308 fino a 5d8ed32.
- Source/runtime closure completata tramite 966124 su `fedora-system-monitor/main`; branch Telegram assorbiti e rimossi.
- Richiesta errata di materializzazione 333860 chiusa prima che il worker la applicasse.

## Remaining
- Accumulare e analizzare cronologia reale.
- Correggere i producer rumorosi e verificare una nuova finestra di notifiche post-fix.

## Blockers
- Nessun blocker runtime o source-integration del collector.
- L'audit successivo richiede solo una finestra di cronologia reale sufficientemente rappresentativa.

## Evidence
- Lineage storico `fedora-system-monitor task/422308`: f577f66, 9d736aa, 5d8ed32; branch poi assorbito/rimosso da 966124.
- gernalix/telegram-notification-history commit 99a9952479074f56095586a6ed3fb210111496db.
- GitHub readback archive/state.json: last_message_id 372496.
- systemd runtime readback: RUN1 4244, RUN2 0, timer enabled+active.
- MegaVault Issue #103: remote allocation => PROMPT_ID 966124.
- codex-roadmap Issue #1050: accidental local-fallback prompt 333860.
- codex-roadmap Issue #1056: canonical replacement 333860 -> 966124 applicato.
- MegaVault Issue #105: PROMPT_ID 966124 materialized.
- MegaVault Issue #104: wrong 333860 materialization closed not_planned.
- completed/telegram-notification-signal-hygiene.md baseline 417826.

## Acceptance criteria
Collector lane source/runtime closure is complete only when runtime remains healthy/incremental, no secret is versioned, source fixes are integrated on fedora-system-monitor main through canonical 966124, 333860 is non-actionable, 966124 is canonical/materialized and terminal PASS, and the history-based audit produces producer-specific fixes.

## Next action
Non rilanciare 422308, 333860 o 966124. Lasciare il collector non-model attivo e, quando la cronologia reale è sufficiente, eseguire l'audit history-based dei producer e applicare solo fix producer-specific.
