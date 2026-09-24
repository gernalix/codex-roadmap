PROMPT_ID=913264
/goal
PROJECT_ID=49
REPO=gernalix/PersonalHub
MEGAVAULT=STRICT

# Goal
Porta il Pixel principale allo stato PersonalHub finale già validato: conserva rollback completo, migra UNA TANTUM il database reale dallo schema effettivamente installato allo schema richiesto dal main finale senza aggiungere migration permanenti all'APK, installa l'APK finale esatto e verifica Home + tutti i moduli con i dati preservati.

# Precondizione autoritativa
- Questo task parte solo dopo 788606 PASS. Quel task definisce commit main finale, schema target e release APK/AAB con shrink/preflight PASS.
- Non assumere target schema 21 o 22: leggi PersonalHubDatabase.SCHEMA_VERSION e Room identity dal commit finale.
- Non modificare sorgenti/app salvo che l'artefatto finale di 788606 non sia recuperabile per un problema puramente di build reproducibility; in quel caso ricostruisci lo stesso commit/config una sola volta, senza feature/fix.
- Usa SEMPRE seriale ADB esplicito. Vietati comandi install/adb generici con più device connessi.

# Esecuzione
1. Claim 913264. Verifica una volta main/commit = revisione release validata da 788606 e nessuna integrazione PH pendente.
2. Risolvi il Pixel fisico tramite helper canonici e blocca qualunque altra QA PH sul device durante questa operazione.
3. Prima di toccare app o DB, salva rollback immutabile:
   - APK attualmente installato o riferimento ripristinabile equivalente;
   - personalhub.db e sidecar -wal/-shm in snapshot coerente;
   - SHA-256 dei file e manifest minimale con package/version/schema.
   Non disinstallare, non clear-data.
4. Leggi sulla COPIA SQLite user_version, Room identity, quick_check, foreign_key_check e inventario/row-count/hash delle tabelle user-data. Se DB illeggibile o identità incompatibile con una versione PH nota => BLOCKED, nessuna modifica live.
5. Determina target schema/identity dal main finale. Costruisci la migrazione SOLO in staging locale:
   - riusa i migratori esterni versionati già esistenti quando coprono una transizione;
   - per transizioni successive usa i Room schema JSON/git diff come contratto e crea script temporanei sotto /tmp, non nuovo codice permanente;
   - una transizione ambigua/distruttiva/non rappresentabile con certezza => BLOCKED; mai risolvere con solo PRAGMA user_version o destructive fallback.
6. La staging finale deve avere target user_version + target Room identity esatti, quick_check=ok, foreign_key_check vuoto e preservazione verificata dei dati non intenzionalmente mutati. Confronta hash/row-count per tutte le tabelle non previste come mutate; per tabelle nuove verifica schema/index/FK.
7. Solo dopo MIGRATION_REPORT=PASS: ferma PH, sostituisci il DB live in modo reversibile con meccanismo canonico/scoped, gestisci sidecar in modo controllato e ri-verifica readback.
8. Installa l'APK finale firmato/minificato della revisione validata. Se serve rebuild, SHA/commit/config devono essere riportati e i gate release già verificati non vanno rieseguiti integralmente.
9. Avvia Home e primo ingresso in People, Timer, Places, Substances, WordPulse, Soldi e ogni altro modulo user-facing presente nella registry finale (incluso Salute se presente). Verifica dati esistenti, nessun crash/FATAL/Room mismatch e le nuove surface principali introdotte dai task P0.
10. Se DB replacement, installazione o primo avvio falliscono: ripristina APK/DB originali dal rollback e termina BLOCKED con errore preciso. Niente retry identico.
11. Dopo PASS, conserva il rollback locale finché non viene esplicitamente eliminato dall'utente. Nessuna modifica codice, nessun nuovo branch, nessun audit extra.

# Acceptance
PASS solo se DB live = schema/identity finali validi, rollback completo esiste, integrità/FK/preservazione dati PASS, APK finale corrisponde al main/preflight finale, installazione Pixel PASS e Home + tutti i moduli finali aprono con dati preservati e senza crash.

# Report
Massimo 12 righe: RESULT, DEVICE, FINAL_HEAD, APK_SHA256, SOURCE_SCHEMA, TARGET_SCHEMA, BACKUP, MIGRATION_REPORT, QUICK_CHECK/FK, DATA_PRESERVATION, MODULES, BLOCKER.