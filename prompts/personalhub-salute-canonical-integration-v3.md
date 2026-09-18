PROMPT_ID=790233 | PARENT_PROMPT_ID=862541 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STRICT

# Goal
Implementa il fondamento dati canonico Salute dentro `personalhub.db`: schema Room/migration/view, contratto patch ChatGPT, sample grouping/turnaround e AI snapshot persistenti/history. Niente UI Salute oltre ciò che serve a compilare.

# Precondizione e fonti
- esegui dopo 830867 PASS;
- repo `/home/daniele/projects/PersonalHub`;
- usa CODE_MAP `health.data`, `health.workflow`, `database.schema` e i documenti `docs/HEALTH_MODULE.md`, `docs/health/HEALTH_DATA_MODEL.md`, `docs/health/CHATGPT_PATCH_CONTRACT.md`.

# Esecuzione minima
1. Crea branch dedicato dal canonical corrente; niente lease durante implementazione.
2. Consumer preflight prima di API/Room pubbliche. Alloca solo lo schema Room successivo necessario e implementa entities/DAO/views/migration con FK e indici coerenti.
3. Preserva i concetti già definiti dai documenti: sample e collection precision, measurement/result state, unexpected-result lookup stabile, availability basis/turnaround difendibile, note/attachments metadata, AI snapshot/history e batch/group id.
4. Riusa il GitPatchEngine esistente: applicazione atomica, idempotenza, validation/FK, preview e rollback; non creare un secondo protocollo patch.
5. Migrazione lossless da schema precedente con fixture rappresentative, `quick_check` e `foreign_key_check`; test mirati repository/turnaround/patch/history. Compile solo consumer necessari.
6. Bump `version.txt` esattamente una volta rispetto al base perché questo task modifica il prodotto.
7. Push/PR; poi lease, refresh main una volta, integration_context/review semantica e solo gli instrumented DB gate indispensabili su `Pixel_8a`. Merge/delete branch dopo PASS; nessuna release/delivery.

# Acceptance / stop
PASS con schema/migration/FK, patch contract, grouping/turnaround, AI history e gate pertinenti PASS, un solo bump e main integrato. Finalizza PROMPT_ID 790233. Output max 8 righe.
