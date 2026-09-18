PROMPT_ID=749621 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST
PARENT_PROMPT_ID=416024

# Goal
Attiva e valida SOLO sul Fedora reale il coordinamento single-writer già implementato da ChatGPT per codex-roadmap e il nuovo flusso concorrente di PersonalHub. Questo prompt sostituisce 416024 perché include anche il writer residuo `codex-roadmap-sync.timer`.

Risultato richiesto:
1. ChatGPT, finalizzatori Codex e sync `codex-usage` consegnano richieste remote; solo GitHub Actions modifica `roadmap.sqlite` e viste generate.
2. PersonalHub può avere implementazioni concorrenti su branch isolati, ma integrazione/QA condivisa/release restano una alla volta e ogni merge richiede review semantica Codex.

Non progettare un sistema alternativo e non fare audit generali.

# Starting point autoritativo
- repo: `/home/daniele/projects/codex-roadmap` e `/home/daniele/projects/PersonalHub`;
- baseline remota minima codex-roadmap: `5a09a5a31cb8713cabb16d8bc747be0a4938440f`;
- baseline remota minima PersonalHub: `ae498ba6c73015d86dedff90fc359326f9db3717`;
- codex-roadmap contiene già `tools/submit_mutation.py`, finalizzatori remote-only, `roadmap_sync.py` remote-only, mutazione `usage_execution`, documentazione e test mirati;
- PersonalHub contiene già regole concorrenti in `AGENTS.md`, lock limitato a integrazione/QA/release, `tools/personalhub_integration_context.py` e `docs/CONCURRENT_WORK.md`;
- branch remoti PH osservati: `chatgpt/918274-runtime-restore`, `feature/shared-alerts-place-tags`, `feature/100-capsule-isolation`, oltre al canonico. NON presumere che siano pronti e NON mergiarli;
- `gh` deve essere autenticato senza mostrare token/segreti.

# Esecuzione minima
1. Un solo fetch + fast-forward per ciascun repo sul branch canonico, solo se sicuro. Dirty non sovrapposto non autorizza stash/reset/cleanup; overlap con il fast-forward => BLOCKED.
2. Verifica in modo bounded che `gh` esista, sia autenticato e abbia accesso a `gernalix/codex-roadmap`. Non stampare credential.
3. codex-roadmap, gate mirati soltanto:
   - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_apply_mutations tests.test_remote_single_writer tests.test_usage_execution_single_writer -v`;
   - `python3 -m py_compile tools/submit_mutation.py tools/roadmap_result.py tools/roadmap_finish.py tools/roadmap_sync.py tools/roadmap_db.py`.
   Se fallisce, correggi solo il failure domain single-writer e rilancia il leaf fallito.
4. Smoke inbox non distruttivo: crea in `/tmp` una mutazione v1 che aggiunga a PROMPT_ID 749621 il tag `single-writer-e2e`; inviala con `tools/submit_mutation.py --request-key activation-749621`. Verifica bounded che finisca in `mutations/applied/activation-749621.json` e che il workflow relativo sia PASS. Nessuna modifica diretta a DB/Markdown/Git locale.
5. Verifica il sync metriche:
   - salva una sola snapshot di HEAD + `git status --porcelain` del repo roadmap;
   - esegui UNA volta `python3 tools/roadmap_sync.py --repo . --source ~/projects/codex-usage`;
   - è ammesso che accodi nuove `usage-*.json`; verifica bounded che le richieste nuove vengano applicate o restino chiaramente pending senza failure;
   - conferma che HEAD locale e dirty set siano identici alla snapshot: il sync non deve più fetchare, committare o pushare il checkout locale.
   - controlla SOLO l'unit/timer `codex-roadmap-sync` esistente e verifica che punti allo script aggiornato; non riscrivere systemd se il path è già canonico. Se serve daemon-reload/restart per recepire file già corretto, fallo.
6. PersonalHub, gate mirati soltanto:
   - `PYTHONDONTWRITEBYTECODE=1 python3 tools/test_personalhub_task_lock.py`;
   - `python3 -m py_compile tools/personalhub_task_lock.py tools/personalhub_integration_context.py`;
   - `python3 tools/personalhub_task_lock.py status`;
   - prova read-only di `python3 tools/personalhub_integration_context.py --branch <uno dei branch remoti non-main esistenti>`. Deve produrre contesto bounded e `automatic_merge_decision=false`; non integrare nulla.
7. Controlla una sola volta i worktree PH locali. Implementazioni correnti su branch dedicati restano intatte. Se una sessione attiva sta lavorando direttamente sul canonico, riportala come rischio ma NON spostare/stashare/resetare il suo lavoro.
8. Non creare/mergiare PR PH, non eliminare branch, non avviare build Android/emulatore/device.
9. Finalizza con il nuovo finalizzatore e conferma che esso accodi la richiesta remota senza creare commit/modifiche locali nel repo roadmap.

# Acceptance
PASS solo se:
- entrambi i checkout includono le baseline minime senza perdita di lavoro;
- `gh` autenticato;
- test e py_compile roadmap PASS;
- `activation-749621` applicata dal writer remoto;
- `roadmap_sync.py` importa/accoda metadata senza cambiare HEAD o dirty set locale;
- unit/timer locale usa lo script aggiornato;
- test e py_compile PH PASS;
- helper PH produce contesto bounded su un branch reale senza decisione automatica di merge;
- nessun branch PH è mergiato/eliminato;
- finalizzatore remote-only confermato.

# Non-goal
Niente refactor/cleanup, branch merge, PR creation, Android build/QA, release, feature PH, branch protection, audit generali, riscrittura di servizi già corretti.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 749621 --confirm-executed`

Dopo il finalizzatore controlla soltanto che HEAD/dirty set locale roadmap non siano cambiati. Output massimo 8 righe: RESULT, ROADMAP_SYNC, GH_AUTH, SINGLE_WRITER_E2E, USAGE_SYNC, PH_HELPERS, PH_WORKTREES, FINALIZER.
