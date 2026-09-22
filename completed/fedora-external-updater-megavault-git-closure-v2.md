PROMPT_ID=417592 | PARENT_PROMPT_ID=854653 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
WORKDIR=/home/daniele/projects/fedora-external-updater

# Goal
Recupera SOLO 854653: risolvi/crea l'identità canonica MegaVault di `fedora-external-updater` senza inventare valori, poi chiudi la persistenza Git delle modifiche `pip_user`/537184 già implementate e testate. Niente nuove feature, audit o refactor.

# Evidenza già verificata
- 854653 è BLOCKED esclusivamente perché MegaVault non identifica `fedora-external-updater`; nessun lavoro di codice è stato eseguito in quel run.
- Alla fine di 537184: unit 12/12 PASS e `apply --only pip_user --scope user` PASS.
- Gli unici file noti da chiudere sono: `config/config.json`, `docs/human/README.md`, `tests/test_core.py`, `updater/core.py`, `updater/updaters.py`.
- La ricerca GitHub corrente non trova `gernalix/fedora-external-updater`: trattalo come potenzialmente local-only finché il Git locale non dimostra il contrario. NON creare un repository remoto.

# Esecuzione minima
1. Esegui `roadmap_start` per 417592 e usa il worktree/contratto restituito.
2. Usa SOLO il meccanismo canonico MegaVault per risolvere il progetto dal path `/home/daniele/projects/fedora-external-updater`. Se manca, crea il record minimo canonico derivando nome/path/remote esclusivamente dal checkout Git locale. Non scegliere né inventare manualmente un `project_id`. Se MegaVault non supporta in modo non ambiguo un repo local-only, termina BLOCKED indicando il solo campo/contratto mancante.
3. Appena MegaVault restituisce un `project_id` canonico, fai un unico preflight nel repo target: branch, `git status --short`, remote e diff SOLO dei 5 file noti. Se le modifiche risultano già committate dopo 854653, verifica containment e non duplicare commit.
4. Preserva ogni hunk estraneo. Se resta lavoro intenzionale, stage selettivo e verifica SOLO: `python3 -m unittest tests.test_core -v`; `python3 -m py_compile updater/core.py updater/updaters.py updater/cli.py`; `git diff --check`. Non rieseguire il comando reale pip salvo evidenza che lo stato sia materialmente cambiato.
5. Crea un solo commit con tutti e soli gli hunk intenzionali `pip_user`/537184. Push SOLO se il checkout ha già un remote canonico writable; se è local-only, il commit locale è sufficiente. Non creare/configurare un remote nuovo.
6. Verifica che nessun hunk in-scope resti non persistito; lascia intatto eventuale dirty work estraneo. Finalizza 417592 e STOP.

# Acceptance
PASS solo se MegaVault risolve un project_id canonico, gli hunk intenzionali sono persistiti esattamente una volta, i tre gate mirati passano, nessun lavoro estraneo viene incluso/perso e nessun ID/remote viene inventato.

# Report
Massimo 6 righe: RESULT, PROJECT_ID, COMMIT, TESTS, REMOTE, BLOCKER.