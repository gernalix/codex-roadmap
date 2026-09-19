PROMPT_ID=462279 | PARENT_PROMPT_ID=790233 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Completa Salute end-to-end sul database canonico PersonalHub e riusa/adatta la UI Salute già esistente. Unifica i vecchi task data+UI; NON implementare Obsidian qui.

# Starting point
- repo: /home/daniele/projects/PersonalHub;
- docs autoritativi: docs/HEALTH_MODULE.md e docs/health/*;
- oggi HealthRepository legge una cache esterna read-only salute.db; HealthScreen ha già Timeline/Exams/Journal, dettagli e trend;
- PersonalHubDatabase corrente non include ancora le entità Health canoniche;
- dopo 697834 usa la nuova schema version come base.

# Esecuzione
1. Implementa nel personalhub.db il modello Health richiesto dai contratti esistenti: campioni/esami/misure, journal/note, evidenze/snapshot AI e relazioni necessarie. Riusa i nomi/semantica dei docs; niente secondo datastore runtime autorevole.
2. Crea una migrazione Room lossless e testata. L'eventuale salute.db/Git artifact può essere solo fonte esplicita di import/sync compatibile, non la source-of-truth parallela dopo l'integrazione.
3. Adatta HealthRepository e la UI esistente al DB canonico invece di riscriverle.
4. Integra Salute con Hub/Context/temporal search, Activity history/undo e patch/import ChatGPT secondo i contratti esistenti. Tocca solo adapter/registrazioni necessarie.
5. NON creare exporter Obsidian: lascia la proiezione Health al task 728918.
6. Leaf test Health+database+hub, migration/quick_check/FK, app compile e un solo smoke AVD del flusso Health. Un solo bump versione.

# Acceptance
PASS se tutti i dati Health runtime sono canonici in personalhub.db, la UI esistente funziona sul canonico, import/sync non crea autorità parallele, Hub/search/history sono integrati e migration+FK+AVD PASS. Stop dopo PASS.
