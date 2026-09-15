[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=760587 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Ritirare definitivamente i repository standalone ormai sostituiti dai moduli di PersonalHub:
- `gernalix/Soldi`
- `gernalix/wordpulse`
- `gernalix/Sostanze`
- `gernalix/Luoghi`
- `gernalix/luoghi-app`

Elimina i repository remoti GitHub e le rispettive copie locali solo dopo i gate distruttivi sotto. Mantieni invece la storia operativa in MegaVault come **archiviata/superseded da PersonalHub**, non cancellare record storici né riusare `project_id`.

# Fatti autoritativi — non ridiscutere
- L'utente ha dichiarato i quattro repository sopra obsoleti perché le relative funzioni sono ora moduli di PersonalHub.
- PersonalHub è `project_id=49`.
- Non serve confrontare intere codebase o storie Git per decidere se mantenerli.
- Non fare audit generale di `~/projects` o di tutti i repository GitHub.

# Preflight distruttivo minimo
Per ciascuno dei cinque target, in batch:
1. risolvi il path locale tramite MegaVault/remote noto; non cercare directory omonime fuori `~/projects`;
2. `git status --short --branch` una sola volta;
3. `git fetch --prune origin` una sola volta;
4. verifica che non esistano modifiche non committate e che il branch locale non sia ahead di `origin/<branch>`;
5. verifica solo l'esistenza del corrispondente modulo/capsula in PersonalHub con lookup mirato per nome/package/entrypoint, senza confronto file-per-file.

Se uno dei cinque contiene lavoro locale non committato o commit non pushati, NON cancellarlo: `BLOCKED` con path+stato minimo e STOP prima di qualsiasi delete remoto.

# Esecuzione
Se tutti i gate sono PASS:
1. usa `gh`/GitHub API, non Chrome, per eliminare esattamente i cinque repository remoti;
2. verifica una sola volta che ciascuno restituisca not-found/non-accessibile come repo remoto;
3. elimina esattamente le cinque directory locali risolte, con guard `realpath` che imponga il prefisso `/home/daniele/projects/`; nessun glob e nessun `find -delete`;
4. aggiorna MegaVault con il meccanismo canonico già previsto per marcare i relativi progetti/repository `archived`/`superseded_by=49`. Se il comando esatto non è noto, usa solo `megavault.py --help`/`project-show` mirati; niente raw SQL finché esiste una API/CLI canonica;
5. registra un singolo evento MegaVault per progetto che dica che il repo standalone è stato ritirato perché assorbito da PersonalHub;
6. verifica solo riferimenti operativi esatti ai cinque slug in `github-autosync`/config runtime. Rimuovi allowlist/path statici che causerebbero errori `missing/no_upstream`; non modificare documentazione storica o report completati;
7. esegui i test mirati soltanto dei file/config effettivamente modificati.

# Non-goal
- non cancellare `PersonalHub` o altri repo simili;
- niente refactor dei moduli PH;
- niente migrazione dati: l'utente ha già dichiarato conclusa la sostituzione;
- niente backup permanente dei quattro repo salvo blocker concreto; non creare nuovi archivi che li mantengano artificialmente in vita;
- niente audit di branch storici, release, issue o PR;
- niente browser se `gh` funziona;
- niente retry identici.

# Acceptance
PASS solo se:
- i cinque repo GitHub indicati non esistono più;
- le cinque copie locali non esistono più;
- PersonalHub resta intatto;
- MegaVault conserva identità/storia ma li marca archiviati/superseded da `project_id=49`;
- github-autosync non li tratta più come repo attivi;
- nessun altro repo è stato eliminato.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 760587 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 760587`

`push_verified=git_push_exit_0` è terminale. Output massimo 7 righe: RESULT, repo remoti eliminati, path locali eliminati, MegaVault, github-autosync, test, blocker eventuale.
