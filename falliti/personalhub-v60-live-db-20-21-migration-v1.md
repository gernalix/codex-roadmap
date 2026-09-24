PROMPT_ID=383662
REPO=gernalix/PersonalHub

# Goal
Ripristina l'usabilità reale di PersonalHub v60 sul dispositivo fisico completando la migrazione ESTERNA del database canonico da schema 20 a 21 e validando poi l'apertura di Home + tutti i sei moduli. Non reintrodurre migration Room nell'APK.

# Fonti già implementate: usa queste, non riscoprirle
- AGENTS.md
- docs/DATABASE_SCHEMA_UPGRADES.md
- tools/migrate_personalhub_v20_to_v21.py
- tools/migrations/personalhub_20_21.sql
- tools/test_migrate_personalhub_v20_to_v21.py
- core/database/src/main/java/com/gernalix/personalhub/core/database/DatabaseStartupGate.kt
- schema Room corrente 21

# Esecuzione
1. Fai il claim canonico di 383662 e usa il worktree assegnato. Non fare audit repo-wide.
2. Esegui una sola volta i test mirati del migratore. Se PASS, non ripeterli senza nuova evidenza.
3. Risolvi il Pixel fisico con gli helper Android già canonici. Non usare comandi ADB non scoped al seriale.
4. Ferma PersonalHub prima di acquisire il DB. Copia in locale personalhub.db e gli eventuali sidecar -wal/-shm senza modificarli e conserva questa copia come rollback immutabile.
5. Leggi il DB copiato con SQLite. Se user_version=20, esegui il migratore già implementato verso un NUOVO file v21. Se è già 21, non rimigrare: valida il DB e passa alla QA. Se è diverso da 20/21 o l'identità Room non coincide con quella prevista, BLOCKED e non improvvisare.
6. Per una migrazione 20→21 richiedi il report PASS: source_version=20, target_version=21, identity hash target corretto, quick_check=ok, foreign_key_check vuoto, nessun residuo health_/salute e hash invariati per tutte le tabelle non intenzionalmente mutate.
7. Solo dopo PASS sostituisci il DB sul dispositivo in modo reversibile sotto run-as, preservando la copia originale. Rimuovi/ricrea i sidecar solo come parte della sostituzione controllata. Non usare uninstall, clear-data, fallback distruttivi o una semplice modifica di PRAGMA user_version.
8. Avvia la v60 già installata. Verifica Home e il primo ingresso in People, Timer, Places, Substances, WordPulse e Soldi. Per ciascuno verifica assenza di crash/FATAL EXCEPTION/Room migration error e presenza dei dati esistenti con uno smoke mirato.
9. Se la sostituzione o la prima apertura fallisce, ripristina il DB originale e BLOCKED con l'errore preciso. Non fare retry identici.
10. Non ricostruire né reinstallare l'APK salvo che sia strettamente necessario per verificare il gate anti-crash già presente su main. Non fare refactor/cleanup fuori scope. Termina appena gli acceptance criteria sono verificati.

# Acceptance
PASS solo se:
- il DB live è schema 21 valido e il rollback v20 è stato conservato;
- il report del migratore/validator è PASS;
- Home non entra più nello stato zombie;
- People, Timer, Places, Substances, WordPulse e Soldi si aprono tutti senza crash sul primo ingresso;
- nessun dato non-Salute risulta perso o alterato inaspettatamente;
- nessuna migration Room è stata reintrodotta nell'APK.

# Report finale
Massimo 12 righe: RESULT, DEVICE, SOURCE_SCHEMA, TARGET_SCHEMA, BACKUP, MIGRATION_REPORT, QUICK_CHECK, FOREIGN_KEYS, DATA_PRESERVATION, HOME, MODULES, BLOCKER.