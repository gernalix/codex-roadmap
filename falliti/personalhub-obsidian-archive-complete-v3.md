PROMPT_ID=355842 | PARENT_PROMPT_ID=946238 | MERGED_FROM=528163,684930 | project_id=49 | campaign_id=ph-obsidian-archive | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Implementa in un solo task l'archivio Obsidian opzionale completo di PersonalHub, accorpando foundation + aggiornamento incrementale + copertura di tutti i moduli mantenuti. Deve restare una proiezione one-way, document-oriented, bounded e recuperabile dopo interruzioni.

# Precondizione
Esegui dopo 416826 PASS su `/home/daniele/projects/PersonalHub`.

# Esecuzione minima
1. Crea un solo branch dedicato. Riusa design/provider già presenti se esistono; usa CODE_MAP, niente audit repo-wide.
2. Foundation: export/projection via SAF con struttura stabile, frontmatter/properties, wikilink leggibili, manifest/state/versioning e sostituzione atomica; SQLite resta source of truth.
3. Incrementale: dirty generation/change journal o equivalente già previsto, resume dopo crash, idempotenza, delete/rename corretti, full rebuild solo quando necessario; niente polling o scansioni complete ad ogni update.
4. Copertura: People, Places, Timer, Soldi, Substances, WordPulse, Salute e superfici globali mantenute. Scegli grain documentale bounded; niente una nota per ogni riga tecnica ad alto volume.
5. Timestamp esatti possono essere properties; Obsidian non ricalcola relazioni temporali cross-module. Relazioni mostrate devono provenire da PH canonico.
6. Test in un solo ciclo: unit/integration del projector + recovery/incremental + determinismo/link/frontmatter + file-count bounded + architecture. Bump `version.txt` una sola volta per l'intera campagna accorpata.
7. Push/PR; poi lease, semantic review e QA `Pixel_8a` del flusso Settings/SAF/export/rebuild/resume. Non installare Obsidian nell'AVD. Merge/delete branch dopo PASS.

# Non-goal
Import Obsidian→PH, replacement Datasette, plugin Obsidian obbligatori, nuovo temporal engine, Logseq, release/delivery.

# Acceptance / stop
PASS con projection completa, incremental/recovery sicuri, tutti i moduli coperti in modo bounded, host+AVD PASS e un solo bump totale. Finalizza PROMPT_ID 355842. Output max 8 righe.
