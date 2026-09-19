PROMPT_ID=618338 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Diagnostica e correggi SOLO la crescita anomala di `personalhub.db` osservata sul Pixel 8a (~627 MB), preservando integralmente i dati utente. Parti dall'evidenza raccolta da PROMPT_ID=914263 e non rifare audit generali o la matrice di test di tutte le tabelle.

# Starting point autoritativo
Repo: `/home/daniele/projects/PersonalHub`.
Device reale: Pixel 8a usato da PROMPT_ID=914263.
Il codice corrente contiene:
- `snapshot` con lo snapshot JSON autorevole corrente;
- legacy `snapshot_history` e `snapshot_payloads`;
- compattazione a batch da 80 righe;
- scheduler che esegue al massimo 12 batch per run;
- retention a 720 history rows e 1500 audit events;
- VACUUM eseguito solo quando non restano legacy rows con `json` non vuoto.
Il salvataggio v56 corrente aggiorna la singola riga `snapshot` e non deve essere riscritto senza evidenza.

# Scope
1. Usa il backup non distruttivo del DB reale già creato/validato da 914263. Prima di qualunque mutazione sul DB reale verifica che il backup sia leggibile e che `PRAGMA quick_check` sia OK.
2. Attribuisci i byte, senza supposizioni:
   - dimensioni esatte `personalhub.db`, `-wal`, `-shm`;
   - `PRAGMA page_size`, `page_count`, `freelist_count`, `journal_mode`;
   - se disponibile, `dbstat` con top tabelle/indici per byte;
   - conteggi e byte logici almeno per `snapshot`, `snapshot_history` raggruppato per kind, legacy rows con json non vuoto, `snapshot_payloads`, `audit_events`, `hub_activity_log`, `history_audit_log`, `history_actions`, `sync_queue`, `sync_shadow`, `people_photos`.
3. Determina la causa primaria tra dati live, snapshot legacy duplicati, payload storici, freelist non reclamata, WAL o altro. Non fare DELETE/VACUUM finché questa attribuzione non è conclusa.
4. Correggi il minimo codice necessario perché la manutenzione converga autonomamente anche quando esistono >960 legacy snapshot rows. Non lasciare un limite di 12 batch che impedisca per sempre retention/VACUUM; usa lavoro bounded/resumable che non blocchi la UI e che riprenda finché la compattazione è completa.
5. Mantieni la retention prevista e non eliminare dati utente correnti. Sono eliminabili solo copie storiche oltre retention, payload orfani e pagine SQLite libere secondo il contratto già esistente.
6. Aggiungi test mirati che riproducano >960 legacy rows e dimostrino: compattazione completa/resumable, retention, rimozione payload orfani e raggiungibilità del VACUUM. Niente suite globale se i leaf mirati passano e il rischio non la richiede.
7. Esegui la bonifica prima su una COPIA del DB reale. Confronta prima/dopo: `quick_check`, row counts delle tabelle dominio, snapshot autorevole/hash equivalente e dimensione fisica.
8. Solo se la copia dimostra zero perdita logica e una riduzione coerente, applica la procedura sicura al DB reale del Pixel con app chiusa e backup preservato. Verifica poi apertura app e i percorsi Pixel già testati da 914263.
9. Se la causa reale è diversa dalla pista snapshot/freelist, correggi quella causa minima mantenendo gli stessi criteri di sicurezza.

# Non-goal
Niente refactor generale, cleanup architetturale, nuove feature, emulator matrix 88/88, modifica dei dati di dominio, reset/clear-data/reinstallazione distruttiva, retry identici senza nuova evidenza.

# Acceptance
PASS solo se:
- i ~627 MB sono attribuiti quantitativamente a file/oggetti SQLite;
- root cause documentata con byte/conteggi, non per inferenza;
- fix mirato impedisce che la stessa crescita resti irrisolta;
- test >960 legacy rows PASS;
- copia del DB reale mantiene integrità e dati logici;
- se la bonifica del DB reale è sicura, il Pixel mantiene dati e flussi funzionanti;
- dimensione prima/dopo e spazio effettivamente recuperato sono riportati.

# Stop
Dopo gli acceptance criteria, finalizza immediatamente. Report conciso, prima riga `PROMPT_ID=618338`, seconda riga `RESULT=PASS|BLOCKED|FAIL`, poi ROOT_CAUSE, SIZE_BEFORE_AFTER, DATA_INTEGRITY, FIX, TESTS.
