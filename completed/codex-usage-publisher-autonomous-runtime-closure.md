PROMPT_ID=817264 | PARENT_PROMPT_ID=642815 | project_id=8 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST
Codex Desktop project: Fedora
last_result=BLOCKED

# Goal
Chiudi definitivamente il publisher Codex sul Fedora reale. Il remoto contiene già i fix emersi da 642815: l'adapter session-archive esporta `init_db` e tutte le connessioni SQLite note del session archive vengono chiuse esplicitamente. Verifica, correggi autonomamente eventuali residui nello stesso failure domain, distribuisci il runtime, pubblica correttamente il cycle storico di PROMPT_ID=918274 e conferma il fast-path finale.

# Autonomia operativa
Goal + acceptance criteria definiscono lo scope; i passi sotto sono il piano iniziale, NON una whitelist.
Se un test, adapter, API, helper, warning, config o servizio in questo stesso failure domain è sbagliato/incompleto, puoi leggere e modificare qualunque codice/test/config adiacente necessario, anche se non nominato qui; poi commit/push e continua.
NON terminare BLOCKED/FAIL per un simbolo mancante, test failure, ResourceWarning, helper obsoleto, lock transitorio, mismatch locale correggibile o necessità di toccare un altro file del repo. Diagnostica il minimo necessario, correggi, rilancia il leaf e riprendi il goal.
BLOCKED solo per credenziale/permesso/decisione utente indispensabile, runtime esterno realmente indisponibile senza alternativa o rischio concreto di perdita dati. FAIL solo dopo recovery in-scope ragionevole realmente esaurito.

# Starting point
- repo: `/home/daniele/projects/codex-usage-monitor`, branch canonico `main`;
- baseline remota minima: `f3eb60652a2384f673c0833b59402e8c3c7b1e62`;
- fix già remoti:
  - `4593ac67b3d699e824817c2a9fb17c27ef4f52d2`: esporta `init_db` dall'adapter;
  - `f3eb60652a2384f673c0833b59402e8c3c7b1e62`: chiude i restanti context SQLite noti;
  - publisher lock wait bounded già presente;
- target storico: sessione `01a0b571-34c1-77a0-873b-79aab0d23acf`, cycle `00a0f021a74b7246cbec3109`, PROMPT_ID=918274;
- runtime: `/home/daniele/.local/lib/codex-usage-monitor/current`;
- data repo: `/home/daniele/projects/codex-usage`;
- non rileggere roadmap/README/MegaVault salvo incoerenza concreta.

# Esecuzione
1. Sincronizza `main` in modo sicuro e richiedi che la baseline minima sia antenata di HEAD. Preserva eventuale lavoro utente; se serve usa una strategia Git non distruttiva invece di fermarti automaticamente.
2. Esegui per primo il leaf gate:
   `PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=error::ResourceWarning python3 scripts/verify_repo.py tests.test_session_archive tests.test_usage_publisher tests.test_task_costs tests.test_publication_semantic_backfill tests.test_usage_publisher_regressions`
   - se fallisce, identifica il minimo failure domain e correggilo autonomamente;
   - per ResourceWarning puoi usare tracemalloc/una query mirata per localizzare la connessione;
   - rilancia solo il leaf necessario finché PASS, poi una sola conferma aggregata.
3. Se hai modificato source/test/config, commit/push `main` una volta dopo i gate PASS.
4. Distribuisci il runtime una volta con `PYTHONDONTWRITEBYTECODE=1 python3 deploy_runtime.py --skip-fetch`.
5. Esegui il publisher installato con `run --wait-lock-seconds 90`.
   - se un lock persiste, identifica il processo/unit che lo detiene e gestisci il transitorio in modo bounded; puoi attendere, fermare/riavviare il timer publisher in-scope e riprovare dopo stato cambiato;
   - non classificare come BLOCKED un semplice overlap col timer.
6. Verifica che il target storico sia realmente pubblicato sotto `prompts/918274/` con sessione/cycle esatti. Se manca, diagnostica parser/backfill/source nel repo e correggi autonomamente lo stesso failure domain; ripubblica e continua.
7. Esegui un secondo publisher consecutivo: deve chiudere con `status=noop_unchanged_sources`.
8. Verifica una volta che `codex-usage-publisher.timer` sia enabled/active e l'ultima service non failed.
9. Dopo acceptance PASS, finalizza e stop; niente audit/benchmark/cleanup opzionali.

# Acceptance
PASS solo se:
- test mirati PASS con ResourceWarning trattati come errori;
- eventuali fix locali sono committati/pushati;
- deploy runtime PASS;
- target 918274 pubblicato con sessione/cycle corretti;
- secondo publisher = `noop_unchanged_sources`;
- timer publisher enabled/active e service non failed.

# Finalizzazione
PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 817264 --confirm-executed`

BLOCKED:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 817264 --result BLOCKED --confirm-executed`

FAIL:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 817264 --result FAIL --confirm-executed`

Output massimo 7 righe: RESULT, HEAD, TESTS, DEPLOY, BACKFILL_918274, RUNS, TIMER.
