PROMPT_ID=825405 | PARENT_PROMPT_ID=357214 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Valida la piattaforma Git Data Sync + history/event-sourcing lite + Time Machine globale già implementata; modifica codice solo se un gate dimostra un difetto concreto. È il gate rischio-dati prima del Data Explorer offline.

# Precondizione
Esegui dopo 355842 PASS. Repo `/home/daniele/projects/PersonalHub`.

# Esecuzione minima
1. Su main pulito, localizza solo boundary Git/history già mappati in CODE_MAP/docs. Esegui prima i leaf test esistenti; se tutto è PASS e non serve alcun fix, non creare branch/commit/bump.
2. Verifica con dati sintetici: Git OFF default e nessun traffico; repo ammesso solo GitHub privato/scrivibile; event before/after atomici e group_id transazionale; rollback/context cleanup; debounce/offline recovery/ack revision-safe; diff semantico; restore globale staging; revert granulare come nuovo edit con preview/FK/stale guard; patch remota verificata ma mai auto-applicata; history Timer globale senza motore duplicato.
3. Verifica statistiche/proiezioni idempotenti e rebuild, BLOB/signature/sharding solo tramite test già esistenti pertinenti; non espandere scope per feature non fallite.
4. Se emerge un defect, crea branch dedicato, correggi in batch il failure domain, rilancia solo leaf invalidati + un gate aggregato finale. Se modifichi prodotto, bump `version.txt` una volta; se validation-only, nessun bump.
5. QA `Pixel_8a` con repository/fake test seam e dati sintetici: Git OFF, History/Time Machine, preview/revert safe+blocked, pending patch review/apply esplicita, restore. Nessun dato/repo personale.
6. Per fix: push/PR, lease + latest-main semantic review, merge/delete branch. Per no-op: lease solo per QA condivisa. Nessuna release/Pixel fisico.

# Acceptance / stop
PASS solo se rischio-dati e gate pertinenti PASS, nessuna credential/data reale esposta e nessun lavoro non necessario introdotto. Finalizza PROMPT_ID 825405. Output max 8 righe.
