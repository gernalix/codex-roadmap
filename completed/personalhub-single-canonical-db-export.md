PROMPT_ID=637985 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD
PARENT_PROMPT_ID=618338

# Goal
Dopo la chiusura di PROMPT_ID=914263, integra e verifica il fix già preparato in PR #21 affinché PersonalHub mantenga UN SOLO database auto-esportato canonico e non accumuli più copie locali `personalhub-backup-*.db`.

# Evidenza autoritativa
Sul backup reale Pixel acquisito prima dei marker UI:
- `personalhub.db` = 15,28 MiB; WAL ≈0,055 MiB; quick_check=ok;
- freelist reclaimable ≈1,86 MiB;
- i ~627 MiB osservati erano la directory `databases`, non il DB vivo;
- 38 file `personalhub-backup-*.db` occupavano complessivamente 608.894.976 B;
- snapshot_history=6 righe, legacy snapshot rows=0: NON è la causa del bloat.
PR #21 (`chatgpt/autoexport-single-db-618338`) contiene già il fix ChatGPT.

# Scope minimo
1. Attendi che 914263 sia terminale e parti dal main risultante.
2. Rebase/aggiorna PR #21 sul main corrente risolvendo solo eventuali conflitti pertinenti.
3. Verifica il contratto:
   - auto-export SAF: esiste solo il file canonico `personalhub.db` (o nome canonico del profilo attivo), nessun `.bak` permanente;
   - snapshot locale `backupCurrent()`: usa un solo file transitorio riutilizzato in cache, non crea UUID backup nel database directory;
   - all'avvio vengono rimossi i vecchi `personalhub-backup-*.db`;
   - NON eliminare `personalhub-pre-import-*.db` se protetti dal marker di rollback;
   - WAL/SHM non contano come auto-export e restano gestiti da SQLite.
4. Esegui solo test mirati/compile necessari per DatabaseVault e auto-export. Non rieseguire la matrice 88/88.
5. Sul Pixel, con backup già preservato:
   - installa la build risultante senza clear-data;
   - avvia una volta l'app;
   - conferma che i 38 legacy backup siano rimossi;
   - conferma `quick_check=ok` e che il DB vivo resti presente e leggibile;
   - esegui un auto-export e verifica che nella destinazione esista un solo DB canonico e nessun `.bak`;
   - non fare VACUUM aggressivo: 1,86 MiB di freelist non giustificano I/O/rischio aggiuntivi.
6. Se tutto PASS, integra PR #21 tramite il single-writer del repo e chiudi il task.

# Non-goal
Niente nuova diagnosi dei 627 MiB, niente refactor DB, niente cleanup di dati utente, niente riduzione forzata di word_entries/people_photos/sync_shadow, niente matrice emulator completa.

# Acceptance
PASS solo se:
- i 38 backup legacy non esistono più dopo startup;
- future chiamate a backupCurrent non fanno crescere il numero di file;
- auto-export esterno contiene un solo DB canonico;
- rollback pre-import resta protetto;
- quick_check=ok e dati Pixel preservati;
- test mirati PASS;
- PR #21 integrata senza interferire con le correzioni di 914263.

# Stop
Dopo PASS finalizza subito. Output: PROMPT_ID, RESULT, LOCAL_BACKUPS_BEFORE_AFTER, EXPORT_FILES, QUICK_CHECK, DATA_PRESERVED, TESTS, MERGE.
