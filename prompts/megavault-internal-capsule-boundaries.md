PROMPT_ID=805417 | project_id=23 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal
Chiudi il solo gate locale rimasto di MegaVault: fast-forward del checkout Fedora a `origin/master`, preservando intatto qualsiasi lavoro locale non pertinente, quindi esegui due smoke read-only sul DB canonico. Non modificare codice o dati.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/MegaVault`, branch `master`, project_id `23`;
- i primi due tentativi `805417` sono entrambi `BLOCKED` senza modifiche: il primo per worktree dirty non pertinente, il secondo perché il prompt pretendeva erroneamente che `megavault.sqlite` restasse byte-identico durante una sync che deve invece recepire la sua versione tracked remota;
- nel secondo run il solo dirty path era `ai/repository-retention-checklist.md`; i file remoti cambiati erano `ai/megavault_core.py`, `ai/strict_tag_wrapper.py`, `megavault.py`, `megavault.sqlite`, `tests/test_megavault.py`, `tests/test_runtime_boundaries.py`; intersezione dirty/remoto = vuota;
- il remoto canonico contiene il refactor al commit minimo `ddf35223822359f6327ef5d6128ee2035bbea6e7`; GitHub Actions `Validate MegaVault` run `35124387697` è PASS;
- la modifica remota di `megavault.sqlite` è versionata e attesa: se il DB locale è pulito, il fast-forward DEVE portarlo alla versione di `origin/master`; non confrontare il suo hash con quello pre-sync;
- DB locale: `/home/daniele/projects/MegaVault/megavault.sqlite`.

Non leggere README/roadmap/MEMORY e non rieseguire refactor, validate, unittest o CI.

# Esecuzione minima
1. In un unico blocco bounded verifica branch `master`, assenza di merge/rebase/cherry-pick, `HEAD`, dirty paths; poi `timeout 20s git fetch origin master`.
2. Verifica che `HEAD` sia antenato di `origin/master`; calcola una sola volta i file cambiati `HEAD..origin/master`. `BLOCKED` solo se un dirty path interseca quei file o esiste altra ambiguità concreta. Nessuno stash/reset/checkout distruttivo.
3. Se `ai/repository-retention-checklist.md` è dirty, registra SOLO il suo SHA-256. Non registrare l'hash pre-sync di file tracked puliti che il remoto deve aggiornare, incluso `megavault.sqlite`.
4. Esegui UNA volta `git merge --ff-only origin/master`; verifica `HEAD == origin/master` e che includa `ddf35223822359f6327ef5d6128ee2035bbea6e7`. L'eventuale checklist deve avere lo stesso SHA-256 di prima. `megavault.sqlite` deve risultare pulito rispetto al nuovo `HEAD`.
5. Esegui solo:
   - `PYTHONDONTWRITEBYTECODE=1 python3 megavault.py project-show 23` → exit 0 e `project_id=23`;
   - `PYTHONDONTWRITEBYTECODE=1 python3 megavault.py project-path --status 23` → exit 0 e `LOCAL`.
6. Stop: niente ulteriori status/audit/test.

# Acceptance
PASS se il checkout è fast-forward all'attuale `origin/master` includendo `ddf3522...`, ogni dirty file locale disgiunto è preservato, `megavault.sqlite` coincide col nuovo stato tracked senza modifica locale, e i due smoke DB sono PASS.

# Non-goal
Niente modifica codice/schema/dati, migrate, validate, unittest, CI rerun, stash/reset, commit della checklist, audit MegaVault o altri repo.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 805417 --confirm-executed`

Dopo `status=completed|already_completed` nessun altro comando. Output massimo 5 righe: `RESULT`, `SYNC`, `LOCAL_DIRTY_PRESERVED`, `DB_SMOKE`, `BLOCKER`.
