PROMPT_ID=724615 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Completa sul branch `feature/salute-canonical-domain` l'integrazione applicativa di Salute già resa canonica dal PROMPT_ID=418763: sostituisci l'attuale consumer di `salute.db` esterno con DAO/view di `personalhub.db`, aggiungi Hub/Temporal/Datasette e UI Android minimale read-only. **Non implementare Obsidian qui**: la proiezione Obsidian è stata promossa a feature globale PH nei prompt successivi.

# Precondizioni autoritative
- repo: `/home/daniele/projects/PersonalHub`;
- esegui SOLO dopo PROMPT_ID=418763 PASS/finalizzato;
- branch obbligatorio: `feature/salute-canonical-domain`, già contenente schema/migration/DAO/view health validati;
- usa come contratto `docs/HEALTH_MODULE.md`, `docs/health/HEALTH_DATA_MODEL.md`, `docs/health/android-minimal-ui.svg`, `docs/health/chatgpt-to-ph-workflow.svg`;
- `version.txt` resta 50: fase intermedia della campagna;
- l'Android UI Salute è read-only: niente Add/Edit/Delete/FAB, niente sync Salute separato;
- `personalhub.db` resta l'unico datastore canonico;
- nessun dato sanitario reale in fixture/source/log;
- `docs/OBSIDIAN_ARCHIVE.md` su main è il contratto della futura feature Obsidian globale: non duplicarne una variante Salute-only in questo task.

# Esecuzione
1. Acquisisci task lock PH con PROMPT_ID 724615. Preflight unico: branch corretto, 418763 finalizzato, worktree/remote safe. Usa CODE_MAP rows `health.root`, `health.data`, `health.workflow`, `hub.context`, `hub.temporal_search`, `database.datasette_sync`; niente audit repo-wide.
2. Consumer closure prima delle rimozioni:
   - usa `android_consumer_preflight.py` sui simboli `HealthRepository`, `GitReadOnlyArtifactClient` e qualunque API pubblica sostituita;
   - rimuovi il download/cache di `gernalix/salute/salute.db`;
   - rimuovi `GitReadOnlyArtifactClient` solo se il gate dimostra che non ha altri consumer;
   - nessun secondo SQLite/cache/sync Salute deve restare.
3. Repository/UI data path:
   - `:feature:salute` legge solo il DB canonico tramite `HealthDao`/view;
   - Recenti, Esami, Campioni, Diario;
   - sample detail: data/ora collection, luogo, count, anomalie, turnaround, sample AI, lista measurement;
   - measurement detail: risultato corrente, storico stesso analyte, commento AI, sample/evidence links; grafico opzionale, non richiesto;
   - journal detail: NOTA CLINICA / META-PARERE AI / EVIDENZE / ORIGINALE DANESE collassato;
   - nessun raw epoch/id/encoding tecnico visibile.
4. Cross-module navigation:
   - doctor chip → People;
   - place chip → Places;
   - medication/prescription link → Substances quando esiste evidenza canonica;
   - purchase link → Soldi solo quando esiste relazione reale;
   - nessuna inferenza per nome.
5. Hub Context:
   - implementa adapter Salute almeno per event, sample, measurement, journal;
   - capability/search/summary/open target coerenti;
   - nessuna feature→feature dependency;
   - Context può collegare note/sample a People/Places/Substances/Soldi tramite binding canonici.
6. Temporal Search:
   - aggiungi provider Salute;
   - health events ordinati da epoch-ms;
   - stesso evento non va duplicato se già rappresentato via Context/relazione esplicita secondo le regole globali;
   - People non viene inferito come “presente” solo perché un medico è citato in una nota.
7. Datasette:
   - assicurati che health_* e le view consumer siano incluse nel normale snapshot/replica senza special-case che le escluda;
   - le FK a People/Places devono risultare navigabili dal layer già esistente;
   - non implementare qui il runtime Datasette Lite: quello resta al prompt successivo dedicato.
8. UI/QA:
   - usa il wireframe SVG come limite superiore, non come invito al redesign;
   - Home tile Salute resta;
   - nessun pulsante “Aggiorna” Salute separato: stato dati segue PH;
   - unit/UI tests sintetici per tabs, sample detail, journal authorship separation, cross-links;
   - AVD Pixel_8a: Home→Salute, Recenti/Esami/Campioni/Diario, sample detail + turnaround, journal clinician-vs-AI, deep-link People/Places/Substances;
   - nessun dato reale.
9. Gate host finale: compile feature/app, Hub/Temporal tests, Datasette visibility test, `checkArchitectureBoundaries`. Failure => leaf correction, poi un solo aggregato finale.
10. Aggiorna `docs/HEALTH_MODULE.md`, CODE_MAP e CI Salute solo se differiscono dal comportamento implementato. Rimuovi documentazione obsoleta del DB esterno e ogni riferimento a una proiezione Obsidian Salute-only.
11. Push SOLO `feature/salute-canonical-domain`. NON mergiare in main e NON eliminare il branch: l'utente farà review/merge manuale prima della campagna Obsidian globale. Rilascia lock.

# Acceptance
PASS solo se Android Salute usa esclusivamente il DB canonico, nessun cache/sync `salute.db` esterno resta, Hub/Temporal/Datasette sono integrati, UI minima read-only + AVD PASS, architecture gate PASS e `version.txt` resta 50. Nessuna implementazione Obsidian Salute-only deve essere introdotta.

# Non-goal
Obsidian exporter, nuove tabelle/schema salvo fix strettamente necessario emerso dai test del modello 418763, Logseq, Data Explorer Lite runtime, release/install Pixel fisico/delivery, redesign PH.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 724615 --confirm-executed`

Output massimo 8 righe: RESULT, HEAD, CANONICAL_UI, HUB, TEMPORAL, DATASETTE, AVD_QA, BLOCKER.
