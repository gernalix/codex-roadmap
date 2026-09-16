PROMPT_ID=805417 | project_id=23 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal
Sincronizza il checkout Fedora reale di MegaVault al refactor boundary già completato e verificato sul remoto, preservando byte-per-byte qualsiasi lavoro locale non pertinente, quindi esegui SOLO lo smoke read-only sul DB canonico locale che GitHub non può verificare.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/MegaVault`, branch `master`, project_id `23`;
- il precedente tentativo `805417` non ha modificato nulla: si è fermato dopo un solo preflight perché il worktree era dirty su `ai/repository-retention-checklist.md`;
- in quel run HEAD locale era `6ccea25e6fd1b8cfc46370520fbc00512d327800`;
- il remoto ora contiene il refactor completo al commit minimo `ddf35223822359f6327ef5d6128ee2035bbea6e7`;
- GitHub Actions `Validate MegaVault` run `35124387697` su `ddf3522...` è PASS: wildcard import, re-export dinamico e monkey-patching sono già rimossi; strict incident/tag policy è posseduta dal core; il gate architetturale, `megavault.py validate` e la suite unittest sono già verdi;
- dal vecchio HEAD locale al remoto le modifiche versionate non includono `ai/repository-retention-checklist.md`; quindi quella modifica locale, se ancora presente, è attesa come lavoro utente non pertinente e NON è un blocker se resta disgiunta dai file aggiornati;
- DB canonico locale: `/home/daniele/projects/MegaVault/megavault.sqlite`.

Prompt autosufficiente: non leggere README/roadmap/spiegazioni/MEMORY, non rieseguire audit, refactor, test suite o CI. Non modificare codice, DB o checklist.

# Esecuzione minima
1. In UN solo blocco bounded: verifica branch `master`, raccogli `HEAD`, dirty paths e presenza di merge/rebase; poi `timeout 20s git fetch origin master`. Merge/rebase attivo o fetch failure => `BLOCKED`.
2. Calcola una sola volta i file versionati cambiati tra `HEAD` e `origin/master`. Il worktree dirty NON blocca automaticamente: blocca solo se un dirty path interseca quei file remoti o rende ambiguo/sicuro impossibile il fast-forward. Vietati stash, reset, checkout distruttivi o commit del lavoro utente.
3. Prima della sync registra SHA-256 di `megavault.sqlite` e, se esiste/modificato, di `ai/repository-retention-checklist.md`. Esegui UNA sola `git merge --ff-only origin/master`. Deve risultare `HEAD == origin/master` e includere `ddf35223822359f6327ef5d6128ee2035bbea6e7`; altrimenti `BLOCKED` senza retry equivalente.
4. Non rieseguire `validate`, unittest, gate architetturale o GitHub Actions: sono già PASS sul commit richiesto. Esegui soltanto questi smoke locali read-only sul DB reale:
   - `PYTHONDONTWRITEBYTECODE=1 python3 megavault.py project-show 23` → exit 0 e `project_id=23`;
   - `PYTHONDONTWRITEBYTECODE=1 python3 megavault.py project-path --status 23` → exit 0 e `LOCAL`.
5. Ricalcola gli hash: `megavault.sqlite` deve essere identico; l'eventuale checklist locale deve essere identico byte-per-byte e restare non committato. Nessun altro readback o audit.

# Acceptance
PASS solo se il checkout locale è fast-forward a `origin/master` e include `ddf3522...`, qualunque dirty work non pertinente è stato preservato intatto, il DB canonico non è cambiato, entrambi gli smoke locali PASS e nessun gate remoto già verde è stato ripetuto.

# Non-goal
Niente modifica codice/schema/dati, migrate, validate, unittest, CI rerun, stash/reset, commit della checklist, MegaVault audit, altri repo o cleanup post-PASS.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 805417 --confirm-executed`

Dopo `status=completed|already_completed` nessun altro comando. Output massimo 5 righe: `RESULT`, `SYNC`, `LOCAL_DIRTY_PRESERVED`, `DB_SMOKE`, `BLOCKER`.
