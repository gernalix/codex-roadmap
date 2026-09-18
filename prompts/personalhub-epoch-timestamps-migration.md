PROMPT_ID=461839 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Sul branch `feature/global-profiles-timestamp-normalization`, porta TUTTI gli istanti/timestamp persistiti dell'intera PersonalHub a Unix epoch milliseconds INTEGER e uniforma TUTTE le visualizzazioni human-facing al contratto `HubTimestamp`: `EEE d/M/yy hh:mm`. Dopo PASS completo, integra il branch in main e rimuovi il branch remoto.

# Starting point autoritativo
- esegui SOLO dopo PROMPT_ID=918274 PASS/finalizzato;
- repo: `/home/daniele/projects/PersonalHub`;
- branch iniziale obbligatorio: `feature/global-profiles-timestamp-normalization`;
- `version.txt=50`; non incrementarlo;
- già presenti: `contracts/database/.../HubTimestamp.kt`, aggiornamento di alcune superfici globali e `tools/check_timestamp_contract.py`;
- storage target: INTEGER epoch ms per ogni ISTANTE. Non convertire campi puramente calendar/date-only (es. day-of-month o data ricorrenza senza ora) solo per il nome del campo;
- UI target esatto di prodotto: `EEE d/M/yy hh:mm`, locale + timezone del device; niente epoch raw o ISO human-facing;
- migrazione DB è high-risk: preserva ogni valore e FK; nessun destructive migration/fallback.

# Esecuzione minima
1. Acquisisci task lock PH con PROMPT_ID 461839. Un solo fetch e fast-forward del branch se sicuro. Verifica che 918274 sia finalizzato. Niente repo-wide discovery: usa `tools/check_timestamp_contract.py` come scanner iniziale e apri solo i file consumer delle colonne segnalate.
2. Prima modifica: esegui lo scanner. Per ogni violazione reale identifica entity + DAO/repository + UI consumer con consumer preflight/symbol search mirato. Non indagare campi date-only esclusi dallo scanner.
3. Crea schema Room v16 e MIGRATION_15_16 (o equivalente packaged path) che converta senza perdita tutti i timestamp TEXT/ISO ancora presenti a INTEGER epoch ms:
   - Soldi: ogni occurred/created/updated/opened/reminder e altri veri istanti;
   - Hub Context/entity binding/resources: created/updated veri istanti;
   - Substances: timestamp/scheduled/sent/prescription instant quando semanticamente timestamp;
   - qualsiasi altra violazione trovata dallo scanner.
   Conversione legacy accetta ISO-8601 già salvato e valori numerici-stringa; formato invalido => fail closed con errore esplicito, non 0/null silenzioso.
4. Aggiorna entities/DAO/repository/domain models a `Long` / `Long?` per tali istanti. Nuove write usano epoch ms direttamente; vietato serializzare nuovi timestamp ISO nel DB.
5. Uniforma la UI dell'INTERA PH:
   - ogni timestamp human-facing passa da `HubTimestamp.format(...)` o wrapper che delega ad esso;
   - formato `EEE d/M/yy hh:mm`, locale/timezone device;
   - rimuovi formatter ad hoc incompatibili (DateFormat, SimpleDateFormat, pattern ISO o altri pattern) SOLO dove visualizzano timestamp;
   - input/parsing tecnico può mantenere un formato macchina separato se non è display finale;
   - export/JSON/protocollo può mantenere il formato richiesto dal protocollo esterno, ma il DB canonico resta epoch ms.
6. Test:
   - migration fixture v15 con valori reali rappresentativi di ogni colonna convertita → v16: stesso istante in epoch ms, conteggi/FK invariati, quick_check/FK PASS;
   - casi DST/timezone + EN/IT per `HubTimestamp.format`;
   - test statico scanner: `python3 tools/check_timestamp_contract.py` deve PASS con 0 violazioni;
   - grep/gate mirato: nessun entity persistito usa String per veri timestamp e nessuna UI mostra epoch raw/ISO;
   - import/restore di DB v15 migra in staging prima della sostituzione e rollback resta funzionante;
   - profili creati/clonati prima della migration migrano indipendentemente al primo switch/apertura.
7. Gate host finale una sola volta: schema export Room, migration tests, moduli toccati, app compile, `checkArchitectureBoundaries`. Failure => leaf correction, poi un solo aggregato finale.
8. QA AVD Pixel_8a con fixture sintetica:
   - apri timestamp in Home/Activity/Search e almeno People, Places, Timer, Soldi, Substances, WordPulse;
   - verifica visivamente/semanticamente il pattern richiesto e nessun epoch/ISO raw;
   - cambia timezone del solo emulatore e verifica stesso epoch mostrato nella nuova ora locale;
   - switch tra due profili e verifica migrazione/visualizzazione indipendente.
9. Solo dopo tutti i PASS:
   - aggiorna docs/CODE_MAP solo se ownership/contract è cambiato;
   - rebase/merge sicuro del branch su current `origin/main` senza perdere commit concorrenti;
   - esegui un ultimo compile/migration smoke SOLO se il merge ha prodotto modifiche/conflict resolution; se merge pulito non ripetere gate già PASS;
   - push main e elimina il branch remoto `feature/global-profiles-timestamp-normalization`;
   - deve restare solo main per PersonalHub.
   Nessuna release/install Pixel/delivery in questo task.
10. Rilascia lock. PASS => stop.

# Acceptance
PASS solo se schema v16 usa INTEGER epoch ms per ogni vero timestamp, migration v15→v16 preserva dati/FK, scanner=0, tutte le UI timestamp usano il formato richiesto, profili migrano correttamente, host+AVD PASS, main contiene il lavoro e il branch remoto è eliminato. version.txt resta 50.

# Non-goal
Cambiare campi date-only senza ora, nuove feature, Data Explorer Lite, release APK/AAB, redesign, audit generale.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 461839 --confirm-executed`

Output massimo 8 righe: RESULT, SCHEMA, MIGRATION, FORMAT, SCANNER, PROFILES, HOST_GATES, AVD_QA.
