PROMPT_ID=748203 | PARENT_PROMPT_ID=643918 | project_id=8
MODEL=GPT-5.6 Luna | REASONING=low | MEGAVAULT=FAST
WORKDIR=/home/daniele/projects/codex-usage-monitor

# Goal
Chiudi SOLO il BLOCKED storico 643918 causato da `session_id mismatch on final readback`. Non rieseguire backfill globali, deploy completi, audit o ricostruzioni del vecchio transcript. Verifica il comportamento corrente di publisher/readback per il caso equivalente e modifica codice solo se il mismatch è ancora riproducibile.

# Evidenza già verificata
- 643918 è canonically `blocked`, senza fix/follow-up registrato.
- Il fix-packet riporta esattamente: `session_id mismatch on final readback`.
- Il work-state punta a `f1049bfec217efa5da8315607f4e5bb3b519f6b6` in `gernalix/codex-usage-monitor`; quel commit porta in CI la regressione di source precedence del goal.
- Il task 643918 era un recovery locale di 529184 basato su quel fix remoto già verificato; il residuo era il solo readback finale.

# Esecuzione minima
1. Avvia 748203 normalmente. Usa AGENTS/MegaVault solo quanto serve al percorso diretto; niente audit repo-wide.
2. Ispeziona SOLO codice e test responsabili di publisher final readback / session identity, più il record canonico necessario a capire 643918. Non stampare transcript completi, session ID, secret o token.
3. Riproduci il mismatch con il test/fixture deterministico minimo. Se il codice corrente passa già il caso equivalente, NON patchare codice.
4. Se il mismatch è ancora riproducibile, applica il fix minimo e aggiungi un solo regression test mirato. Niente refactor/cleanup.
5. Non eseguire publisher live, backfill o deploy se il test deterministico basta. Se un live readback è davvero indispensabile, massimo una esecuzione; nessun retry identico senza nuova evidenza.
6. Tramite il single writer registra la recovery canonica minima per 643918 senza inventare una nuova execution del parent. Se deve restare storico/blocked, preservalo e rendi esplicita la recovery tramite questo fix.
7. Se hai modificato codice, esegui solo i test mirati coinvolti + `git diff --check`. Verifica idempotenza e STOP.

# Acceptance
PASS solo se il caso equivalente di final readback risolve deterministicamente la stessa session identity; 643918 non resta un blocker operativo irrisolto; nessun backfill/deploy/audit globale viene ripetuto; nessun transcript/secret viene pubblicato; un secondo reconcile è no-op.

# Report
Massimo 6 righe: RESULT, ROOT_CAUSE, CURRENT_BEHAVIOR, CODE_CHANGE, MUTATION, BLOCKER.
