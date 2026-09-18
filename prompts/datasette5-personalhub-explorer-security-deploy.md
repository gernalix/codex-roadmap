PROMPT_ID=527184 | project_id=10 | model=GPT-5.5 | reasoning=medium | MegaVault=STRICT

# Goal
Valida e distribuisci SOLO la proiezione Datasette PersonalHub già implementata su `main`: SQL read-only autenticato, FK cross-modulo native e bridge Context persona-centrico. Nessun redesign.

# Starting point autoritativo
- repo: `/home/daniele/projects/datasette5`, branch canonico `main`;
- `origin/main` atteso: `d836d13ece57d9c57d413fc6e4d815367809b3d8`;
- file pertinenti soltanto: `scripts/personalhub_projection.py`, `tests/test_personalhub_projection.py`, `README.md`;
- Datasette runtime canonico: 1.0a38;
- `personalhub_read`: browse + `execute-sql` solo actor umano `root`; anonimo negato; ogni write/schema mutation negata;
- FK logiche già codificate: finance transaction/recurrence → People/Places/finance, prescription → doctor/finance transaction, intake → prescription;
- `hub_person_relations` è derivata SOLO da Context esistenti e risolve binding tipizzati sullo stesso source device; non deve inferire per nome né scrivere nel DB Android;
- API mobile `personalhub-sync` resta separata e non può interrogare/modificare la proiezione.

# Esecuzione minima
1. Preflight unico: worktree + un solo fetch `origin main`; richiedi `origin/main == d836d13ece57d9c57d413fc6e4d815367809b3d8`; fast-forward locale. Mismatch/divergenza/dirty overlap => BLOCKED, niente stash/rebase.
2. Leggi SOLO i tre file sopra e gli helper deploy già nominati nel README se servono. Niente audit repo-wide.
3. Esegui in un solo batch i tre test mirati:
   - `test_cross_module_logical_relations_become_native_foreign_keys`
   - `test_context_memberships_materialize_person_centric_native_foreign_keys`
   - `test_datasette_native_clickable_fk_labels_and_read_only_permissions`
   Failure => correggi solo quel failure domain e rilancia solo il test fallito.
4. Dopo PASS mirato: una sola `python3 -m unittest tests.test_personalhub_projection -v` e una sola `python3 launch_datasette.py --check`.
5. Se hai dovuto correggere codice, commit/push `main` una sola volta; altrimenti nessun commit cosmetico.
6. Distribuisci col deploy Oracle canonico già documentato, senza stampare secret e senza cambiare nginx/auth/token non pertinenti.
7. Readback runtime bounded e read-only:
   - `personalhub_read` accessibile a `root`, anonimo negato;
   - SELECT innocua via SQL UI/API autenticata;
   - `PRAGMA foreign_key_list` conferma FK cross-modulo e FK di `hub_person_relations` verso contacts/contexts/bindings e target concreti;
   - se i dati reali contengono almeno una relazione persona→altro modulo, verifica che Datasette la esponga come backlink/foreign-key link; se non esiste alcun esempio reale, il test sintetico mirato è sufficiente e NON creare dati produzione;
   - write SQL/upsert/schema mutation sulla proiezione negati;
   - endpoint mobile sync ancora disponibile, senza inviare dati sintetici.
8. PASS => stop immediato. Nessun benchmark/plugin/tuning/audit successivo.

# Acceptance
PASS solo se test mirati + suite + launcher check PASS, runtime Oracle aggiornato, FK native integre, `hub_person_relations` valida e read-only, SQL autenticato funziona, anonimo/write negati, API sync invariata.

# Non-goal
Niente modifiche PH Android, nuovi token, dati sintetici produzione, redesign Context, plugin opzionali, query salvate, benchmark o refactor.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 527184 --confirm-executed`

Output massimo 6 righe: `RESULT`, `HEAD`, `TESTS`, `FK_GRAPH`, `DEPLOY`, `BLOCKER`.
