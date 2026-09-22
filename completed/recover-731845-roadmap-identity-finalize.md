PROMPT_ID=865431 | PARENT_PROMPT_ID=731845 | project_id=23 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
WORKDIR=/home/daniele/projects/codex-roadmap

# Goal
Recupera SOLO la finalizzazione canonica di 731845. Il lavoro sostanziale dell’audit è già stato completato: NON rieseguire gitleaks, scansioni repository, cambi di visibility o l’audit di pubblicazione. Risolvi esclusivamente il mismatch di identità che ha fatto fallire il roadmap_guard finale e porta 731845 allo stato canonico corretto.

# Evidenza già verificata
- il fix-packet di 731845 riporta come unico blocker finale: `roadmap_guard` con `prompt_identity_mismatch:selected=529184:requested=[TELEGRAM_TOKEN_REDACTED]`;
- il lavoro aveva già prodotto il commit `d8112b2efd520a1d765962c7578035c1c7d8c974` (`Harden repository publication audit policy`);
- quel commit è già un antenato del `main` corrente di `gernalix/codex-roadmap`;
- il prompt sostanziale è già archiviato sotto `completed/repository-publication-audit-correction-apply.md`.

# Esecuzione minima
1. Avvia 865431 col normale `roadmap_start`; non tentare di riavviare 731845.
2. Ispeziona SOLO il percorso di risoluzione identità usato da `roadmap_guard`/single-writer per 731845 e la selezione stale `529184`. Non stampare, recuperare o ricostruire valori di token/segreti: il valore redatto resta redatto.
3. Determina da fonti canoniche se il mismatch deriva da selezione/session attribution stale oppure da un bug minimo nel resolver. Non inventare identità e non modificare altre registrazioni.
4. Se basta una correzione dati/stato, applicala esclusivamente tramite il single writer. Modifica codice solo se il mismatch è riproducibile nel resolver corrente; in tal caso fai il cambiamento minimo e aggiungi un test mirato.
5. Verifica che 731845 risulti `completed` senza rieseguire alcun audit e che una seconda finalizzazione sia idempotente/no-op.
6. Se hai modificato codice: esegui solo i test mirati del resolver/guard e `git diff --check`. Niente suite ampia salvo failure direttamente pertinente.
7. Finalizza 865431 e STOP.

# Acceptance
PASS solo se: 731845 è canonicamente `completed`; il mismatch di identità non ricorre; `d8112b2` resta intatto e contenuto in main; nessun audit/scansione/visibility change viene rieseguito; nessun segreto viene letto o pubblicato; nessun prompt estraneo viene modificato.

# Report
Massimo 6 righe: RESULT, ROOT_CAUSE, PARENT_STATUS, CODE_CHANGE, TESTS, BLOCKER.