PROMPT_ID=532918 | PARENT_PROMPT_ID=583742 | RECOVERY_PROMPT_ID=155893 | project_id=49 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
WORKDIR=/home/daniele/projects/codex-roadmap

# Goal
Riconcilia SOLO il BLOCKED storico 583742 con il retry diretto 155893 già completed/PASS. Non rieseguire PersonalHub, ADB, Pixel, build, test, installazioni o diagnosi dati.

# Evidenza già verificata
- 583742 è canonically `blocked`; il fix-packet è generico, ma il prompt di retry 155893 dichiara esplicitamente che 583742 si era fermato SOLO per problemi del gate roadmap, senza diagnosi PH e senza modifiche a dati/app.
- 155893 è `completed` con ultimo esito `PASS` ed è il retry diretto di 583742 (`RETRY_OF=583742`).
- 583742 ha come unico figlio/follow-up visibile 155893; non risultano fix/replacement pending o running associati al parent.

# Esecuzione minima
1. Avvia SOLO 532918 con `roadmap_start.py`; non riavviare 583742 o 155893.
2. Leggi SOLO i record canonici 583742/155893 e `completed/personalhub-v53-freeze-data-recovery-v2.md`. Niente audit repo-wide e nessun accesso al device.
3. Conferma che 155893 resta completed/PASS e che il completion artifact mantiene `RETRY_OF=583742`.
4. Tramite il single writer registra la recovery canonica minima che rende 583742 non più un blocker operativo irrisolto. Non inventare una nuova execution di 583742; se la semantica conserva il parent come storico/blocked, lascialo tale e collega esplicitamente la recovery 155893 PASS.
5. Non modificare PersonalHub né altri repo. Verifica idempotenza: un secondo reconcile deve essere no-op.
6. Finalizza 532918 e STOP.

# Acceptance
PASS solo se la roadmap rappresenta chiaramente che 583742 è stato recuperato da 155893 PASS, senza nuove execution del parent, senza runtime/test ripetuti, senza modifiche a PersonalHub e con reconcile idempotente.

# Report
Massimo 6 righe: RESULT, PARENT_583742, RECOVERY_155893, MUTATION, IDEMPOTENCE, BLOCKER.
