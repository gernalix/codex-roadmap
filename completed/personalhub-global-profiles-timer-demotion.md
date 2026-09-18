PROMPT_ID=918274 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Completa SOLO PersonalHub `main`, che contiene già l'implementazione remota dei profili globali: rendi robusti i profili database e rimuovi definitivamente dal modulo Timer le feature già promosse a livello PersonalHub. NON fare la migrazione timestamp v16: è il task successivo.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`;
- branch obbligatorio: `main`; i vecchi branch feature sono già stati integrati/eliminati. NON ricrearli e non pubblicare nuovi branch remoti;
- baseline remota minima: `5f06b1bde2115bcb51156cf9c17edaaff669e7a0` deve essere antenata di RUN_HEAD;
- `version.txt=50`; non incrementarlo;
- usa prima `.codex/CODE_MAP.tsv`; niente audit repo-wide salvo failure concreto;
- già presenti su `main`: `DatabaseProfiles`, create empty/clone/rename/delete/switch, journal crash-consistent, UI Profili, active profile in Home, export separato per profilo con SAF root condivisa, Git/Datasette separati per profile_id, rimozione UI Timer di Time Machine/audit/import/export/Data Explorer/backup folder e cancellazione dello stub `MultiDbVaults`;
- il DB canonico resta UNO alla volta: `personalhub.db`; i profili inattivi sono snapshot completi e isolati. Non reintrodurre DB separati per modulo;
- la Timeline Timer RESTA: è cronologia specifica delle sessioni, non la Activity/Temporal Search globale PH.

# Esecuzione minima
1. Acquisisci task lock PH con PROMPT_ID 918274. Un solo fetch `origin main`; richiedi branch `main` e fast-forward solo se sicuro. Dirty non sovrapposto non blocca; niente stash/reset né branch remoto temporaneo.
2. Esegui subito leaf compile/test pertinenti a `:core:database`, `:app`, `:feature:multitimetracker`, `:feature:luoghi`. Usa i failure per correggere in batch errori introdotti dal branch; niente audit generale.
3. Chiudi il contratto Profili:
   - default `Personal` usa senza copia/perdita il DB oggi attivo;
   - EMPTY produce schema corrente vuoto; CLONE_CURRENT produce copia logicamente identica;
   - switch salva il profilo corrente, valida/migra staging, monta atomicamente il target e non permette a ViewModel vecchi di riscrivere dati;
   - fault injection prima/dopo snapshot, rename DB, update active_profile e ritiro marker: dopo recovery DB montato e active_profile devono sempre riferirsi allo stesso profilo;
   - rename/delete inactive funzionano; active non eliminabile;
   - Git Data config/status/manifest/applied patches e Datasette config/device clock/status sono separati per profile_id; nessuna tombstone/revision identity passa tra profili;
   - auto-export usa lo stesso SAF root device-local ma nome file/stato separati per profilo e non sovrascrive un altro profilo.
4. Rendi profile-aware il runtime Android esterno al DB con il minimo cambiamento:
   - widget Timer: salva anche profile_id; un widget del profilo A non deve eseguire un ID omonimo nel profilo B;
   - alarm/notifiche Timer e geofence Places: al cambio profilo cancella/reconcilia lo stato del profilo uscente e ricostruisci SOLO dal DB entrante;
   - WorkManager/background job non deve continuare con identità/config del profilo precedente dopo restart.
5. Completa la de-promozione Timer, usando compile come oracle:
   - elimina Time Machine Timer interna: `model/TimeMachine.kt`, overlay/projection/state/callback collegati e test specifici; usa solo History/Time Machine globale PH dove serve;
   - elimina Audit Log Timer come feature (screen/capsule/filter/undo). Le write Timer devono alimentare Registro/History globale tramite il boundary globale esistente; conserva solo adapter/migration strettamente necessari per dati legacy;
   - elimina Import/Export Timer e wrapper zombie `capsules/importexport`, `SqliteVault`, `AppRestarter`, Vault*/backup helper/CSV/ZIP quando non hanno più consumer. Import/export/backup/restore appartengono a `DatabaseVault`;
   - rimuovi stringhe, route, contract, test e CODE_MAP obsoleti; `timer.import_export` deve restare assente;
   - Data Explorer resta globale; nessun entry point Timer;
   - NON rimuovere Timeline Timer, Alerts, Quick Events, Tags, Since When, Chains, statistiche Timer-specifiche.
   Se un file legacy serve ancora al formato dati Timer, riducilo a un adapter persistence senza UI/ownership duplicata anziché cancellarlo alla cieca.
6. Test host mirati:
   - fixture multi-modulo Personale → clone → modifica clone → ritorno Personale: dati/FK isolati;
   - empty profile non eredita People/Places/Soldi/Timer/Substances/WordPulse;
   - fault injection switch ripristina coppia DB/profile coerente;
   - Git/Datasette/export profile isolation;
   - widget/alarm/geofence non crossano profile_id;
   - assenza compile-time di Timer TimeMachine/Audit/ImportExport/MultiDb/DataExplorer ownership.
7. Gate host finale UNA volta dopo leaf PASS: compile debug + test pertinenti + `checkArchitectureBoundaries`. Dopo failure rilancia solo il leaf coinvolto, poi un unico gate finale.
8. QA AVD canonico Pixel_8a SOLO se host PASS:
   - crea `Lavoro QA` clone e `Vuoto QA`;
   - verifica almeno People, Places, Timer e Soldi nei tre profili;
   - modifica clone e torna Personale;
   - verifica widget Timer configurato in Personale mentre è attivo Lavoro;
   - verifica alarm/geofence reconciliation;
   - kill-process durante switch controllato e recovery coerente.
   Solo fixture sintetiche, nessun dato personale.
9. Aggiorna CODE_MAP solo per ownership realmente cambiata. NON fare timestamp migration, release, APK delivery, refactor fuori scope.
10. Solo dopo tutti i gate PASS, commit/push `main` una sola volta con le modifiche del task. Non creare/pushare branch remoti temporanei. Rilascia lock. PASS => stop.

# Acceptance
PASS solo se host gate + AVD QA sono PASS; profili atomici/isolati; nessun sync/export/widget/alarm/geofence crossa profili; Timer non espone né possiede più Time Machine, multi-db, Audit Log, Import/Export o Data Explorer; Timeline Timer resta; nessun dato perso; version.txt resta 50; `main` contiene il risultato verificato.

# Non-goal
Migrazione timestamp v16, redesign UI, DB per modulo, release/install Pixel/delivery, audit generale.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 918274 --confirm-executed`

Output massimo 8 righe: RESULT, HEAD, PROFILES, CRASH_RECOVERY, TIMER_DEMOTION, RUNTIME_STATE, HOST_GATES, AVD_QA.
