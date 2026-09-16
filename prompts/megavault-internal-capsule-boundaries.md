PROMPT_ID=805417 | project_id=23 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | last_result=BLOCKED

# Goal
Fast-forwarda il MegaVault Fedora a `origin/master` preservando gli uncommitted locali disgiunti, poi fai due smoke read-only sul DB canonico. Nessuna modifica applicativa o dati manuale.

# Fatti già verificati
- repo `/home/daniele/projects/MegaVault`, branch `master`; ultimo HEAD locale osservato `6ccea25e6fd1b8cfc46370520fbc00512d327800`;
- ultimo run: unico dirty path `ai/repository-retention-checklist.md`; remote-changed = `ai/megavault_core.py`, `ai/strict_tag_wrapper.py`, `megavault.py`, `megavault.sqlite`, `tests/test_megavault.py`, `tests/test_runtime_boundaries.py`; intersezione = vuota;
- `origin/master` contiene almeno `ddf35223822359f6327ef5d6128ee2035bbea6e7`; `Validate MegaVault` run `35124387697` PASS;
- `megavault.sqlite` era pulito localmente ma è cambiato sul remoto: il fast-forward deve aggiornarlo alla versione tracked canonica. Non confrontare il suo hash pre/post. Va preservato byte-per-byte solo il dirty work locale disgiunto.

Non leggere README/roadmap/MEMORY e non eseguire refactor, migrate, validate, unittest o CI.

# Esecuzione
1. Usa **una sola tool-call shell bounded** per l'intero gate locale: verifica `master` e assenza di merge/rebase/cherry-pick; `timeout 20s git fetch origin master`; verifica `HEAD` antenato di `origin/master`; calcola dirty paths e `HEAD..origin/master`; se c'è overlap => `BLOCKED`. Nessun stash/reset/checkout distruttivo.
2. Nella stessa call, se il checklist è dirty salva il suo SHA-256; esegui una sola `git merge --ff-only origin/master`; verifica `HEAD == origin/master`, presenza di `ddf3522...`, checklist invariato e `megavault.sqlite` pulito rispetto al nuovo `HEAD`.
3. Sempre nella stessa call esegui soltanto:
   - `PYTHONDONTWRITEBYTECODE=1 python3 megavault.py project-show 23` → exit 0 + `project_id=23`;
   - `PYTHONDONTWRITEBYTECODE=1 python3 megavault.py project-path --status 23` → exit 0 + `LOCAL`.
4. Se tutto PASS, usa come unica tool-call successiva il finalizzatore. Nessun readback dopo.

# Acceptance
PASS = checkout all'attuale `origin/master` includendo `ddf3522...`; dirty locale disgiunto preservato; DB tracked pulito sul nuovo HEAD; entrambi gli smoke PASS.

# Stop
Su PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 805417 --confirm-executed`

Output massimo 5 righe: `RESULT`, `SYNC`, `LOCAL_DIRTY_PRESERVED`, `DB_SMOKE`, `BLOCKER`. Su blocker niente finalizzatore.
