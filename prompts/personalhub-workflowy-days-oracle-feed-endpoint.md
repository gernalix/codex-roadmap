[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=681427 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD | type=Prompt`

# Goal
Rendi operativo **Workflowy-days → PersonalHub**: trova/configura l'URL HTTPS reale sulla VM Oracle, provalo dall'esterno e aggiungi a PH solo l'eventuale auth read-only minima.

# Fatti autoritativi
`workflowy-import` (`project_id=94`) produce `workflowy_days` in `workflowy.db` e `/home/ubuntu/imports/workflowy_days.json`. PH `main` ha già `WorkflowyDaysSync`, `workflowy_days.db`, WorkManager giornaliero, ETag/304, deep-link e UI impostazioni. `datasette5` usa già nginx/reverse proxy/API HTTPS mobili. Non toccare OCR/transazioni, `DatasetteSync` o `SyncJournal` salvo blocker diretto.

# Esegui
1. Prima della VM: pull fast-forward del checkout canonico `vm_oracle`. Pull `workflowy-import`/`PersonalHub`/`datasette5` solo se realmente letti/modificati. Niente inventory repo.
2. Partendo solo dai service/config Datasette/nginx pertinenti, determina runtime, hostname HTTPS, se `workflowy.db` è già servito, route riusabile e auth effettiva.
3. Preferisci: Datasette route `workflowy_days` se già disponibile; altrimenti esponi il JSON compatto tramite HTTPS esistente. Vietato creare nuovo daemon/server se nginx/Datasette bastano.
4. Prova da Fedora/host esterno alla VM: HTTP 200 + JSON parseabile da `WorkflowyDaysFeed` + almeno un giorno reale `2026-09-01..07` se presente nel DB.
5. Se serve Bearer: actor/token dedicato **read-only least-privilege**, segreto fuori Git/log; aggiungi a `WorkflowyDaysSync`/impostazioni solo il supporto minimo e prova anche che una risorsa non autorizzata resti negata. Se non serve, non inventare auth.
6. Prima di modificare PH: un fetch, fast-forward sicuro, verifica sovrapposizioni; conflitto concorrente reale => `BLOCKED`, niente overwrite/rebase esplorativi.
7. Testa solo ciò che cambia; nessuna QA Android/build se PH non cambia. Push di ogni repo modificato; niente retry identici senza nuova evidenza.

PASS = `FEED_URL` HTTPS verificato esternamente, JSON valido/compatibile, PH lo consuma, auth eventuale read-only, nessuna modifica fuori scope.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 681427 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 681427`
Poi STOP.

Output ≤8 righe: RESULT, FEED_URL, AUTH, DATABASE/TABLE, PH_CHANGE, TEST, SHA repo modificati, BLOCKER.
