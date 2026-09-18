PROMPT_ID=527184 | project_id=10 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STRICT

# Goal
Valida e distribuisci SOLO la proiezione Datasette PersonalHub già implementata su `main`: SQL read-only autenticato, FK cross-modulo native e grafo Context simmetrico peer-to-peer. Nessun redesign.

# Starting point autoritativo
- repo: `/home/daniele/projects/datasette5`, branch canonico `main`;
- `origin/main` atteso: `51462485da43849c8551da53b2fbc7abb4c678f7`;
- file pertinenti soltanto: `scripts/personalhub_projection.py`, `tests/test_personalhub_projection.py`, `README.md`;
- Datasette runtime canonico: 1.0a38;
- `personalhub_read`: browse + `execute-sql` solo actor umano `root`; anonimo negato; ogni write/schema mutation negata;
- FK logiche già codificate: finance transaction/recurrence → People/Places/finance, prescription → doctor/finance transaction, intake → prescription;
- `hub_entity_relations` è derivata SOLO da Context esistenti e deduplicata per coppia non ordinata; `hub_entity_relation_contexts` conserva provenance/duplicati senza replicare backlink;
- `hub_temporal_relations` contiene SOLO relazioni inferite non già spiegate da FK/Context; `hub_temporal_evidence` conserva anche i match soppressi; WordPulse usa burst <=5 min tra entry e non gli intervalli lunghi delle sessioni; People entra solo tramite eventi/initiative timestampati;
- soglie temporali già codificate: interval overlap >=50%; high solo >=80% con ratio durate <=4x; point-in-interval max 12h (high <=3h); point-point <=5 min (high <=60s); intervalli >24h esclusi;
- API mobile `personalhub-sync` resta separata e non può interrogare/modificare la proiezione.

# Esecuzione minima
1. Preflight unico: worktree + un solo fetch `origin main`; richiedi `origin/main == 51462485da43849c8551da53b2fbc7abb4c678f7`; fast-forward locale. Mismatch/divergenza/dirty overlap => BLOCKED, niente stash/rebase.
2. Leggi SOLO i tre file sopra e gli helper deploy già nominati nel README se servono. Niente audit repo-wide.
3. Esegui in un solo batch i cinque test mirati:
   - `test_cross_module_logical_relations_become_native_foreign_keys`
   - `test_context_memberships_materialize_deduplicated_symmetric_cross_module_foreign_keys`
   - `test_datasette_native_clickable_fk_labels_and_read_only_permissions`
   - `test_temporal_relations_are_inferred_separately_and_suppress_explicit_duplicates`
   - `test_temporal_confidence_downranks_long_or_imbalanced_windows`
   Failure => correggi solo quel failure domain e rilancia solo il test fallito.
4. Dopo PASS mirato: una sola `python3 -m unittest tests.test_personalhub_projection -v` e una sola `python3 launch_datasette.py --check`.
5. Se hai dovuto correggere codice, commit/push `main` una sola volta; altrimenti nessun commit cosmetico.
6. Distribuisci col deploy Oracle canonico già documentato, senza stampare secret e senza cambiare nginx/auth/token non pertinenti.
7. Readback runtime bounded e read-only:
   - `personalhub_read` accessibile a `root`, anonimo negato;
   - SELECT innocua via SQL UI/API autenticata;
   - `PRAGMA foreign_key_list` conferma FK cross-modulo, FK di `hub_entity_relations` e FK endpoint di `hub_temporal_relations`;
   - verifica che un pair già collegato via FK/Context NON compaia anche come backlink temporale visibile, ma lasci evidenza/sostegno aggregato;
   - verifica che `wordpulse_activity_bursts` raggruppi entry ravvicinate e che una sessione WordPulse lunga senza burst utile non generi associazioni;
   - se i dati reali contengono almeno un Context con membri di moduli diversi, verifica la navigazione in entrambe le direzioni partendo da almeno due moduli diversi; se non esiste alcun esempio reale, il test sintetico mirato è sufficiente e NON creare dati produzione;
   - write SQL/upsert/schema mutation sulla proiezione negati;
   - endpoint mobile sync ancora disponibile, senza inviare dati sintetici.
8. PASS => stop immediato. Nessun benchmark/plugin/tuning/audit successivo.

# Acceptance
PASS solo se test mirati + suite + launcher check PASS, runtime Oracle aggiornato, FK native integre, Context graph deduplicato, temporal graph separato/senza backlink duplicati e con WordPulse burst/People-event policy corretta, SQL autenticato funziona, anonimo/write negati, API sync invariata.

# Non-goal
Niente modifiche PH Android, nuovi token, dati sintetici produzione, redesign Context, plugin opzionali, query salvate, benchmark o refactor.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 527184 --confirm-executed`

Output massimo 6 righe: `RESULT`, `HEAD`, `TESTS`, `FK_GRAPH`, `DEPLOY`, `BLOCKER`.
