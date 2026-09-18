PROMPT_ID=461839 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Sul branch `feature/global-profiles-timestamp-normalization`, fai un audit fail-closed dei timestamp dell'intera PersonalHub: conferma che i timestamp già persistiti come epoch milliseconds INTEGER restino invariati, migra SOLO gli eventuali veri istanti ancora salvati come TEXT/ISO a INTEGER epoch-ms, e uniforma tutte le visualizzazioni human-facing al contratto `HubTimestamp`: `EEE d/M/yy HH:mm`.

Nota formato: usa il pattern Java/Kotlin corretto `EEE d/M/yy HH:mm` (`M`=mese, `yy`=anno a 2 cifre, `HH`=24h). Non usare `m` per il mese né `hh` senza AM/PM.

# Starting point autoritativo
- esegui SOLO dopo PROMPT_ID=918274 PASS/finalizzato;
- repo: `/home/daniele/projects/PersonalHub`;
- branch iniziale obbligatorio: `feature/global-profiles-timestamp-normalization`;
- `version.txt=50`; non incrementarlo;
- già presenti/attesi: `contracts/database/.../HubTimestamp.kt`, aggiornamento di alcune superfici globali e `tools/check_timestamp_contract.py`;
- assunzione operativa da verificare, non da reinventare: People, Places, Timer e gran parte di PH dovrebbero già salvare i timestamp come `Long`/INTEGER epoch-ms. NON convertire o toccare campi già corretti solo perché hanno nomi temporali;
- storage target: INTEGER epoch ms per ogni vero ISTANTE. Non convertire campi puramente calendar/date-only o ricorrenze senza ora solo per il nome del campo;
- UI target esatto di prodotto: `EEE d/M/yy HH:mm`, locale + timezone del device; niente epoch raw o ISO human-facing;
- se lo scanner non trova veri timestamp TEXT/ISO residui, NON creare una migration Room inutile: limita il task a formatter, consumer/UI, gate statico e QA;
- se invece esistono residui TEXT/ISO, la migrazione DB è high-risk: preserva ogni valore e FK; nessun destructive migration/fallback.

# Esecuzione minima
1. Acquisisci task lock PH con PROMPT_ID 461839. Un solo fetch e fast-forward del branch se sicuro. Verifica che 918274 sia finalizzato. Niente repo-wide discovery: usa `tools/check_timestamp_contract.py` come scanner iniziale e apri solo i file consumer delle colonne segnalate.
2. Prima modifica/verifica: esegui lo scanner e produci una classificazione compatta:
   - `already_epoch`: timestamp già `Long`/INTEGER da lasciare invariati;
   - `date_only`: campi data/calendario/ricorrenza da NON convertire;
   - `technical_protocol`: export/API/protocollo esterno che può restare nel formato richiesto dal protocollo;
   - `violation`: veri istanti persistiti come TEXT/ISO da correggere.
   Non indagare campi esclusi dallo scanner salvo evidenza concreta.
3. Per ogni `violation` reale identifica entity + DAO/repository + UI consumer con consumer preflight/symbol search mirato. Non fare audit generale del repo.
4. Solo se ci sono `violation` persistenti, crea schema Room successivo e relativa migration (es. v15→v16, salvo che il branch abbia già avanzato schema) che converta senza perdita i veri istanti TEXT/ISO residui a INTEGER epoch ms:
   - Soldi: eventuali occurred/created/updated/opened/reminder o altri veri istanti ancora TEXT;
   - Hub Context/entity binding/resources: eventuali created/updated veri istanti ancora TEXT;
   - Substances: eventuali scheduled/sent/prescription instant quando semanticamente timestamp;
   - qualsiasi altra violazione trovata dallo scanner.
   Conversione legacy accetta ISO-8601 già salvato e valori numerici-stringa; formato invalido => fail closed con errore esplicito, non 0/null silenzioso.
5. Aggiorna entities/DAO/repository/domain models SOLO per le violazioni reali. Nuove write usano epoch ms direttamente; vietato serializzare nuovi timestamp ISO nel DB canonico.
6. Uniforma la UI dell'INTERA PH:
   - ogni timestamp human-facing passa da `HubTimestamp.format(...)` o wrapper che delega ad esso;
   - formato `EEE d/M/yy HH:mm`, locale/timezone device;
   - rimuovi formatter ad hoc incompatibili (DateFormat, SimpleDateFormat, pattern ISO o altri pattern) SOLO dove visualizzano timestamp;
   - input/parsing tecnico può mantenere un formato macchina separato se non è display finale;
   - export/JSON/protocollo può mantenere il formato richiesto dal protocollo esterno, ma il DB canonico resta epoch ms.
7. Test:
   - scanner classification test: i campi già epoch non vengono segnalati né modificati;
   - se esistono violazioni migrate: fixture legacy con valori rappresentativi di ogni colonna convertita → schema corrente: stesso istante in epoch ms, conteggi/FK invariati, quick_check/FK PASS;
   - casi DST/timezone + EN/IT per `HubTimestamp.format`;
   - `python3 tools/check_timestamp_contract.py` deve PASS con 0 violazioni non classificate;
   - grep/gate mirato: nessuna entity persistita usa String per veri timestamp e nessuna UI mostra epoch raw/ISO;
   - import/restore di DB legacy migra in staging prima della sostituzione e rollback resta funzionante quando una migration è stata necessaria;
   - profili creati/clonati prima dell'eventuale migration migrano indipendentemente al primo switch/apertura.
8. Gate host finale una sola volta: schema export Room solo se schema cambiato, migration tests se esiste migration, moduli toccati, app compile, `checkArchitectureBoundaries`. Failure => leaf correction, poi un solo aggregato finale.
9. QA AVD Pixel_8a con fixture sintetica:
   - apri timestamp in Home/Activity/Search e almeno People, Places, Timer, Soldi, Substances, WordPulse;
   - verifica semanticamente il pattern richiesto e nessun epoch/ISO raw;
   - cambia timezone del solo emulatore e verifica stesso epoch mostrato nella nuova ora locale;
   - switch tra due profili e verifica migrazione/visualizzazione indipendente.
10. Solo dopo tutti i PASS:
   - aggiorna docs/CODE_MAP solo se ownership/contract è cambiato;
   - rebase/merge sicuro del branch su current `origin/main` senza perdere commit concorrenti;
   - esegui un ultimo compile/migration smoke SOLO se il merge ha prodotto modifiche/conflict resolution; se merge pulito non ripetere gate già PASS;
   - push main e elimina il branch remoto `feature/global-profiles-timestamp-normalization`;
   - NON eliminare `feature/salute-canonical-domain`: è il branch dedicato del task Salute successivo e verrà rebased su questo nuovo main.
   Nessuna release/install Pixel/delivery in questo task.
11. Rilascia lock. PASS => stop.

# Acceptance
PASS solo se tutti i veri timestamp persistiti risultano INTEGER epoch ms oppure sono stati migrati senza perdita; i campi già epoch non sono stati riscritti inutilmente; gli eventuali date-only/protocol fields sono classificati e motivati; scanner=0 violazioni non classificate; tutte le UI timestamp usano `EEE d/M/yy HH:mm`; profili migrano/visualizzano correttamente; host+AVD PASS; main contiene il lavoro e il branch remoto è eliminato. `version.txt` resta 50.

# Non-goal
Conversione indiscriminata di timestamp già epoch, cambiare campi date-only senza ora, nuove feature, Data Explorer Lite, release APK/AAB, redesign, audit generale.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 461839 --confirm-executed`

Output massimo 8 righe: RESULT, AUDIT, SCHEMA_OR_NOOP, MIGRATION, FORMAT, SCANNER, PROFILES, HOST_AVD.