PROMPT_ID=418763 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Sul branch `feature/salute-canonical-domain`, sostituisci l'attuale Salute basato su `salute.db` esterno con un dominio Salute canonico dentro `personalhub.db`, mantenendo una UI Android read-only/minimale e integrando Salute nel workflow PH già esistente: Git semantic history/revert/Time Machine, Datasette, Hub Context/Temporal e proiezione Obsidian deterministica.

# Precondizioni autoritative
- repo: `/home/daniele/projects/PersonalHub`;
- esegui SOLO dopo PROMPT_ID=461839 PASS/finalizzato e dopo che il suo branch timestamp è stato integrato in `main`;
- branch di lavoro obbligatorio: `feature/salute-canonical-domain`; rebase/fast-forward sicuro sul nuovo `origin/main` preservando i commit di design già presenti;
- il branch contiene già `docs/HEALTH_MODULE.md`, `docs/health/HEALTH_DATA_MODEL.md`, `docs/health/CHATGPT_PATCH_CONTRACT.md`, `docs/health/chatgpt-to-ph-workflow.svg`, `docs/health/android-minimal-ui.svg`; questi sono il contratto di prodotto;
- `version.txt` deve restare 50 in questa fase intermedia della campagna PH: dopo il rebase risolvi eventuali conflitti senza bump; release/version bump resta al task Datasette Lite finale della campagna;
- NON committare dati sanitari reali, screenshot, note cliniche, dump DB o fixture riconducibili all'utente nel repo pubblico PH;
- `personalhub.db` resta l'unico DB runtime canonico/scrivibile;
- l'UI Salute resta senza Add/Edit/Delete/FAB; le write reali arrivano da patch Git PH trusted con provenance `author=chatgpt`, `source=remote_patch`;
- Obsidian è consumer rigenerabile, non source of truth; Logseq DB è fuori scope.

# Esecuzione
1. Acquisisci il task lock con PROMPT_ID 418763. Un solo fetch/rebase bounded del branch. Usa prima CODE_MAP rows `health.*`, `database.schema`, `hub.context`, `hub.temporal_search`, `database.datasette_sync`; niente audit repo-wide.
2. Prima di cambiare Room/API pubbliche esegui `tools/android_consumer_preflight.py` sui simboli coinvolti. Per rimozioni usa il gate forbid prima del primo Gradle.
3. Implementa il modello di `docs/health/HEALTH_DATA_MODEL.md` nel prossimo schema Room libero:
   - `health_import_batches`;
   - `health_source_metadata`;
   - `health_events`;
   - `health_samples`;
   - `health_examinations`;
   - `health_measurements`;
   - `health_journal_entries`;
   - `health_ai_snapshots`;
   - `health_ai_evidence`.
   Entità/DAO pubblici stanno in `:contracts:database`; builder/migration in `:core:database`; `:feature:salute` non possiede un DB.
4. FK/cross-domain:
   - clinician_contact_id → People/contacts, nullable SET NULL;
   - place_id → Places, nullable SET NULL;
   - non creare health_doctors/health_places/health_drugs;
   - prescrizione/rinnovo documentato deve poter essere applicato nella stessa patch alle tabelle Substances esistenti; acquisto farmaco resta Soldi e NON va inferito dalla prescrizione;
   - usa Hub Context per i collegamenti semantici N-ari; nessuna dipendenza feature→feature.
5. Sample:
   - un solo `sample_id` per stesso specimen fisico;
   - tutte le misure dello stesso prelievo puntano allo stesso sample;
   - grouping solo con evidenza sorgente, mai per sola data;
   - supporta blood/urine/swab/stool/saliva/other.
6. Temporal/turnaround:
   - tutti i nuovi istanti sono INTEGER epoch-ms;
   - separa collection, result_available/received e import;
   - `availability_basis` distingue source_timestamp / minsp_notification / chat_received_proxy / unknown;
   - turnaround sangue solo con collection precision=datetime e delta>=0;
   - formato display esatto giorni+ore interi, es. `1g 7h`;
   - crea view stabili: `v_health_timeline`, `v_health_samples`, `v_health_sample_measurements`, `v_health_measurements`, `v_health_journal`, `v_health_measurement_turnaround`, `v_health_sample_turnaround`, `v_health_turnaround_stats`, `v_health_ai_evidence`.
7. AI snapshots:
   - ogni measurement → commento longitudinale;
   - ogni sample → commento complessivo non concatenativo;
   - ogni journal → meta-parere AI longitudinale con stance normalizzato concordant / partially_concordant / questioned / insufficient_evidence / not_applicable + rationale + uncertainty;
   - no hindsight: evidenze cliniche <= as_of_ms;
   - `health_ai_evidence` rende auditabili le evidenze;
   - update di snapshot incrementa assessment_version; Git conserva la storia precedente.
8. ChatGPT→PH patch contract: usa `docs/health/CHATGPT_PATCH_CONTRACT.md` e il formato già implementato da `GitPatchEngine`; non inventare un secondo patch protocol.
   - aggiungi test/fixture SINTETICA di una patch unica con import_batch, sample, più measurement, commenti measurement+sample, journal+meta-comment e riferimenti cross-domain;
   - tutta la patch deve avere un unico group_id/import_batch e applicarsi atomicamente;
   - verifica dedup/preconditions/idempotenza e che GitDataTracking generi history semantica granulare ma raggruppabile;
   - pull non deve applicare automaticamente patch se il contratto corrente richiede review esplicita: rispetta il comportamento validato dal task Git History.
9. Hub:
   - implementa adapter Salute almeno per event, sample, measurement, journal;
   - aggiungi provider temporale Salute alla ricerca globale;
   - People/Places/Substances restano entità canoniche; le card/chip Salute aprono i target esistenti tramite contratti Hub.
10. UI Android: elimina il modello cache/download `salute.db` e rendi `HealthRepository` consumer del DB canonico/DAO. UI volutamente minima come SVG:
   - tab Recenti, Esami, Campioni, Diario;
   - niente sync Salute separato, niente CRUD;
   - sample detail: risultati + anomalie + turnaround + sample AI;
   - measurement detail: storico + commento AI; grafico NON necessario in v1;
   - journal detail: NOTA CLINICA / META-PARERE AI / EVIDENZE / ORIGINALE DANESE collassato;
   - cross-module chips navigabili.
11. Rimuovi il boundary esterno solo dopo consumer closure:
   - rimuovi download/cache di `gernalix/salute/salute.db`;
   - rimuovi `GitReadOnlyArtifactClient` solo se consumer preflight dimostra che Salute era l'unico consumer;
   - aggiorna/ritira la CI `salute-module.yml` coerentemente al nuovo boundary;
   - nessuna seconda sync/history.
12. Obsidian:
   - individua il workflow/proiezione Obsidian/Vault PH esistente con ricerca mirata;
   - aggiungi la proiezione Salute deterministica descritta nei docs: Samples, Journal, Esami, Dashboard;
   - canonical_id/data_ms/module/kind nelle properties; link verso People/Places/Substances;
   - rigenerazione idempotente; nessuna ingestione Markdown→PH in questo task;
   - se l'infrastruttura Obsidian generica non è ancora presente nel RUN_HEAD, implementa solo un exporter health bounded e documenta il punto di aggancio senza creare un secondo servizio di sync.
13. Migrazione dati reali:
   - NON incorporare dati reali nel source tree;
   - crea/usa una procedura locale o semantic patch fuori repo per trasferire l'attuale dataset dal repo privato `gernalix/salute` alla copia personale `personalhub.db`;
   - verifica conteggi/valori/provenienza e sample grouping;
   - se il source privato non è disponibile nel runtime Codex, marca questa sola fase BLOCKED/PENDING senza inventare dati: schema/codice/test sintetici possono comunque essere completati.
14. Test/gate:
   - Room schema export + migration fixture dalla versione post-461839 alla nuova;
   - quick_check/FK;
   - DAO/view tests, turnaround edge cases, sample grouping, no-hindsight snapshot fixture;
   - Git history single/group revert con dati health sintetici;
   - Hub adapters + Temporal Search;
   - Datasette domain visibility;
   - Obsidian deterministic golden test;
   - feature Salute unit tests;
   - compile highest affected consumer + `checkArchitectureBoundaries`;
   - nessun raw epoch/ID mostrato nella UI.
15. QA solo AVD canonico Pixel_8a:
   - Home→Salute;
   - Recenti/Esami/Campioni/Diario;
   - sample detail + turnaround;
   - journal distinction clinician vs AI;
   - deep-link People/Places/Substances;
   - History mostra e può preview/revertire una modifica health sintetica e un intero group import;
   - niente dati personali reali nel QA.
16. Push SOLO `feature/salute-canonical-domain`. NON mergiare in main e NON eliminare il branch: l'utente lo mergerà manualmente dopo review. Rilascia lock. PASS => stop.

# Acceptance
PASS solo se Salute usa esclusivamente `personalhub.db`, schema/migration/compile/architecture/AVD sono PASS, UI è read-only e minimale, sample grouping+turnaround+AI multilivello sono implementati, History/Hub/Temporal/Datasette/Obsidian sono integrati senza un secondo motore, nessun dato sanitario reale è committato nel repo pubblico e `version.txt` resta 50.

# Non-goal
Niente redesign generale PH, Logseq DB, secondo database, secondo Git sync, nuovo backend, diagnosi cliniche automatiche definitive, Play release/install Pixel/delivery.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 418763 --confirm-executed`

Output massimo 9 righe: RESULT, HEAD, SCHEMA, HEALTH_MODEL, GIT_HISTORY, HUB_TEMPORAL, OBSIDIAN, AVD_QA, BLOCKER.
