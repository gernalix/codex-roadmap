PROMPT_ID=418763 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STRICT

# Goal
Su PersonalHub `main`, implementa SOLO il fondamento dati canonico di Salute dentro `personalhub.db`: schema Room, migration, view, contratto patch ChatGPT, sample grouping/turnaround e AI snapshot persistenti/history. Non toccare ancora UI Android, Hub/Temporal o Obsidian salvo ciò che serve per compilare.

# Precondizioni autoritative
- repo: `/home/daniele/projects/PersonalHub`;
- esegui SOLO dopo PROMPT_ID=461839 PASS/finalizzato; il relativo risultato deve essere già presente in `main`;
- branch obbligatorio: `main`; i documenti di design Salute sono già presenti su `main`. NON ricreare il vecchio branch `feature/salute-canonical-domain` né pubblicare altri branch remoti;
- contratti già presenti su `main`: `docs/HEALTH_MODULE.md`, `docs/health/HEALTH_DATA_MODEL.md`, `docs/health/CHATGPT_PATCH_CONTRACT.md`;
- `version.txt` resta 50: questa è una fase intermedia della campagna PH;
- nessun dato sanitario reale, screenshot, nota clinica, dump DB o fixture riconducibile all'utente può essere committato nel repo pubblico;
- `personalhub.db` resta l'unico DB runtime canonico/scrivibile;
- usa il patch format già implementato da `GitPatchEngine`; nessun secondo protocollo;
- UI/HUB/Obsidian sono il task successivo.

# Esecuzione
1. Acquisisci task lock PH con PROMPT_ID 418763. Un solo fetch `origin main` + fast-forward bounded. Usa CODE_MAP rows `health.data`, `health.workflow`, `database.schema`; niente audit repo-wide.
2. Prima della prima modifica a Room/API pubbliche esegui `python3 tools/android_consumer_preflight.py scan --symbol ...` per ogni simbolo pubblico toccato; per rimozioni usa il gate forbid prima di Gradle.
3. Alloca il prossimo schema Room libero post-461839 e implementa in `:contracts:database` + `:core:database`:
   - `health_import_batches`;
   - `health_source_metadata`;
   - `health_events`;
   - `health_samples`;
   - `health_examinations`;
   - `health_measurements`;
   - `health_journal_entries`;
   - `health_ai_snapshots`;
   - `health_ai_evidence`;
   - `HealthDao`.
   Segui esattamente `docs/health/HEALTH_DATA_MODEL.md`; nessun DB separato di feature.
4. FK/cross-domain di schema:
   - clinician_contact_id → contacts, nullable SET NULL;
   - place_id → places, nullable SET NULL;
   - non creare health_doctors/health_places/health_drugs;
   - i riferimenti a Substances/Soldi restano nei domini canonici esistenti e/o via Hub/evidence, senza feature dependency.
5. Sample identity:
   - stesso specimen fisico → stesso `sample_id`;
   - non raggruppare per sola data;
   - supporta blood/urine/swab/stool/saliva/other;
   - aggiungi vincoli/indici utili per source accession/hash quando disponibili.
6. Temporal/turnaround:
   - tutti i nuovi istanti INTEGER epoch-ms;
   - separa collection, result_available, received, import;
   - `availability_basis`: source_timestamp / minsp_notification / chat_received_proxy / unknown;
   - delta sangue valido solo con collection precision=datetime, availability difendibile e delta>=0;
   - display view in giorni+ore interi, nessun decimale;
   - implementa almeno: `v_health_timeline`, `v_health_samples`, `v_health_sample_measurements`, `v_health_measurements`, `v_health_journal`, `v_health_measurement_turnaround`, `v_health_sample_turnaround`, `v_health_turnaround_stats`, `v_health_ai_evidence`.
7. AI persistence:
   - measurement snapshot;
   - sample aggregate snapshot;
   - journal meta-assessment con stance concordant / partially_concordant / questioned / insufficient_evidence / not_applicable;
   - `as_of_ms` + `assessment_version`;
   - evidence links auditabili;
   - nessun vincolo DB deve mescolare testo AI con testo clinico originale.
8. ChatGPT patch/history:
   - usa `docs/health/CHATGPT_PATCH_CONTRACT.md`;
   - fixture SINTETICA con import_batch + blood sample + >=3 measurement + per-measurement AI + sample AI + journal + journal AI + source metadata;
   - unico `patch_id`/group_id;
   - applicazione atomica, FK PASS, idempotenza/dedup/precondition;
   - verifica che GitDataTracking produca eventi granulari ma raggruppati;
   - verifica preview/revert del singolo record e del gruppo quando il seam esistente lo consente senza duplicare i gate completi del task Git History successivo.
9. Migration:
   - production migration dalla versione post-461839;
   - fixture schema precedente → nuovo schema: quick_check/FK PASS, dati preesistenti invariati;
   - nessuna destructive fallback;
   - schema export Room aggiornato.
10. Legacy Salute reale:
   - NON inserire dati reali nel source tree;
   - se il repo privato `gernalix/salute` e la copia personale DB sono disponibili localmente, prepara/applica una migration/import fuori repo e verifica conteggi/valori/provenienza;
   - se non disponibili, lascia questa sola fase PENDING con tool/procedura bounded, senza bloccare schema/test sintetici.
11. Gate host: test migration + DAO/view + turnaround + sample grouping + AI/no-hindsight invariants + synthetic patch/history, poi compile highest affected consumer e `checkArchitectureBoundaries`. Failure => leaf correction, un solo aggregato finale.
12. Solo dopo i gate PASS, commit/push `main` una sola volta. Nessun branch remoto temporaneo, nessun AVD, nessuna release/delivery. Rilascia lock.

# Acceptance
PASS solo se il nuovo schema Room è valido e migrabile, Salute vive in `personalhub.db`, sample/turnaround/AI/history sintetica sono testati, schema export + compile + architecture gate PASS, nessun dato reale è nel repo e `version.txt` resta 50.

# Non-goal
UI Android Salute, Hub adapters, Temporal Search UI, Obsidian exporter, Datasette Lite mobile, Logseq, release/install, branch remoti temporanei.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 418763 --confirm-executed`

Output massimo 8 righe: RESULT, HEAD, SCHEMA, MIGRATION, HEALTH_MODEL, PATCH_HISTORY, HOST_GATES, BLOCKER.
