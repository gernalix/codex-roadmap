PROMPT_ID=416024 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST

# Goal
Attiva e valida SOLO sul Fedora reale il nuovo coordinamento già implementato da ChatGPT:
1. codex-roadmap usa GitHub Actions come unico writer canonico; `roadmap_result.py` / `roadmap_finish.py` devono consegnare mutazioni remote senza modificare/fetchare/mergiare/pushare il checkout locale;
2. PersonalHub consente implementazioni concorrenti su branch isolati, ma serializza integrazione/QA condivisa/release e richiede review semantica Codex prima di ogni merge.

Non progettare un sistema alternativo e non fare audit generali.

# Starting point autoritativo
- repo locali canonici: `/home/daniele/projects/codex-roadmap` e `/home/daniele/projects/PersonalHub`;
- baseline remota minima codex-roadmap: `f1a58deea31f43f21ff99d793c3cabc38141489f`;
- baseline remota minima PersonalHub: `ae498ba6c73015d86dedff90fc359326f9db3717`;
- codex-roadmap contiene già `tools/submit_mutation.py`, il nuovo `roadmap_result.py`/ `roadmap_finish.py`, documentazione single-writer e test mirati;
- PersonalHub contiene già le nuove regole in `AGENTS.md`, il lock ristretto a integrazione/QA/release, `tools/personalhub_integration_context.py` e `docs/CONCURRENT_WORK.md`;
- branch remoti PH osservati al momento dell'implementazione: `chatgpt/918274-runtime-restore`, `feature/shared-alerts-place-tags`, `feature/100-capsule-isolation`, oltre al branch canonico. NON presumere che siano pronti e NON mergiarli in questo task;
- `gh` deve essere autenticato senza stampare token/segreti.

# Esecuzione minima
1. Per ciascuno dei due repo fai un solo fetch e fast-forward del branch canonico se deterministicamente sicuro. Dirty non sovrapposto non autorizza stash/reset/cleanup; se il fast-forward toccherebbe lavoro locale, BLOCKED.
2. Verifica in una sola chiamata bounded che `gh` esista e sia autenticato per GitHub con accesso al repo `gernalix/codex-roadmap`. Non mostrare credential/token.
3. codex-roadmap: esegui solo:
   - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_apply_mutations tests.test_remote_single_writer -v`;
   - `python3 -m py_compile tools/submit_mutation.py tools/roadmap_result.py tools/roadmap_finish.py`.
   Se un test fallisce, correggi solo il failure domain single-writer e rilancia il leaf fallito.
4. Esegui un solo smoke end-to-end non distruttivo della inbox remota:
   - crea in `/tmp` una mutazione v1 che aggiunga al PROMPT_ID `416024` il tag `single-writer-e2e`;
   - inviala con `tools/submit_mutation.py --request-key activation-416024`;
   - verifica con GitHub API/CLI che `mutations/applied/activation-416024.json` compaia e che il relativo workflow sia PASS. Attendi in modo bounded; niente polling ravvicinato.
   - NON modificare direttamente `roadmap.sqlite`, Markdown generati o Git locale per questo smoke.
5. PersonalHub: esegui solo:
   - `PYTHONDONTWRITEBYTECODE=1 python3 tools/test_personalhub_task_lock.py`;
   - `python3 -m py_compile tools/personalhub_task_lock.py tools/personalhub_integration_context.py`;
   - `python3 tools/personalhub_task_lock.py status`;
   - una prova read-only di `tools/personalhub_integration_context.py` su UNO dei branch remoti non-main esistenti. Deve produrre contesto bounded e `automatic_merge_decision=false`; non integrare nulla.
6. Controlla una sola volta i worktree PH locali. Se trovi implementazioni correnti su branch dedicati, lasciale intatte. Se trovi una sessione attiva che sta lavorando direttamente sul branch canonico, riportala come rischio concreto ma NON spostare/stashare/resetare il suo lavoro in questo task.
7. Non creare/mergiare PR PH, non eliminare branch e non eseguire build Android/emulatore/device: questo prompt valida solo l'infrastruttura di coordinamento.
8. Dopo tutti i gate PASS, finalizza con il nuovo finalizzatore. La finalizzazione stessa deve confermare il comportamento single-writer: deve restituire richiesta queued/pending/applied senza creare commit locale nel repo roadmap.

# Acceptance
PASS solo se:
- entrambi i checkout locali includono le baseline remote minime senza perdita di lavoro;
- `gh` è autenticato e può scrivere la richiesta roadmap senza esporre secret;
- test/py_compile roadmap PASS;
- la mutazione `activation-416024` arriva in `mutations/applied/` tramite GitHub Actions;
- test/py_compile PH PASS;
- l'helper PH produce contesto bounded su un branch reale ma non prende alcuna decisione automatica di merge;
- nessun branch PH viene mergiato/eliminato;
- il finalizzatore del prompt usa la inbox remota e non modifica Git locale.

# Non-goal
Niente refactor, cleanup, branch merge, PR creation, Android build/QA, release, modifica di feature PH, branch protection GitHub, revisione generale della roadmap o conversione dei branch esistenti in PR.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 416024 --confirm-executed`

Dopo il finalizzatore verifica solo che il checkout locale roadmap non abbia ricevuto un nuovo commit dal comando; non fare altri audit. Output massimo 7 righe: RESULT, ROADMAP_SYNC, GH_AUTH, SINGLE_WRITER_E2E, PH_HELPERS, PH_WORKTREES, FINALIZER.
