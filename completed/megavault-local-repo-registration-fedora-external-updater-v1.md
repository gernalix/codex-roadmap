PROMPT_ID=936284 | PARENT_PROMPT_ID=417592 | project_id=23 | MODEL=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD
PRIMARY_REPO=gernalix/MegaVault
TARGET_WORKTREE=/home/daniele/projects/fedora-external-updater

# Goal
Sblocca SOLO 417592 introducendo in MegaVault il minimo contratto canonico e idempotente per registrare/risolvere un repository Git local-only dal worktree, poi usa quel contratto una sola volta per `fedora-external-updater` e chiudi la persistenza Git degli hunk `pip_user` già implementati. Non creare alcun repository remoto e non rifare feature/app logic.

# Evidenza autoritativa già verificata
- 417592 è canonically BLOCKED, senza fix/follow-up, con fix-packet: `MegaVault manca un contratto canonico per creare repo local-only dal path.`
- L'ultima execution 417592 è BLOCKED; il work applicativo precedente 537184 aveva già 12/12 unit PASS e `apply --only pip_user --scope user` PASS.
- Gli unici file applicativi noti da persistere sono `config/config.json`, `docs/human/README.md`, `tests/test_core.py`, `updater/core.py`, `updater/updaters.py`.
- `gernalix/fedora-external-updater` NON esiste su GitHub: il checkout va trattato local-only salvo prova contraria dal suo Git locale.
- MegaVault/master corrente espone `register-github-repo` con `--owner --name --remote-url --default-branch --worktree` obbligatori e valida che il remote corrisponda a GitHub; non esiste un comando equivalente local-only.
- Nessuna PR aperta MegaVault trovata per questo contratto.

# Esecuzione minima
1. Avvia SOLO 936284 con `roadmap_start.py`. Parti dai file MegaVault direttamente pertinenti: `ai/megavault_core.py`, `megavault.py`, `tests/test_megavault.py`, schema/protocollo solo se necessario. Niente audit repo-wide.
2. Ispeziona esclusivamente la rappresentazione canonica `projects`/repository index e il path di `register-github-repo`. Se lo schema attuale può già rappresentare un repo senza remote, NON fare migrazioni schema.
3. Aggiungi il contratto minimo, preferibilmente un comando esplicito tipo `register-local-repo --worktree PATH` (nome esatto libero se un pattern esistente è migliore), con queste invarianti:
   - deriva identità/nome, root reale, branch/default branch e remote solo dal checkout Git locale;
   - remote può essere assente; non inventare owner, URL, project_id o GitHub slug;
   - il `project_id` viene allocato esclusivamente da MegaVault/SQLite secondo il contratto esistente;
   - stesso worktree ripetuto => stesso project_id/no-op;
   - collisioni path/identity ambigue => fail-closed senza mutazioni parziali;
   - se il checkout ha già un remote canonico, riusa il percorso esistente anziché duplicare il progetto;
   - nessun delete/reuse di project_id.
4. Aggiungi SOLO regression test mirati per: local-only senza remote; idempotenza; checkout con remote già registrato; collisione ambigua/fail-closed. Esegui solo questi test + `python3 -m py_compile` dei file toccati + `git diff --check`; amplia solo se un failure lo richiede.
5. Integra la modifica MegaVault tramite il suo single-writer canonico e sincronizza il checkout operativo. Non fare refactor/cleanup.
6. Usa UNA volta il nuovo contratto su `/home/daniele/projects/fedora-external-updater`; registra il project_id restituito senza scegliere numeri manualmente. Se il checkout locale dimostra un remote esistente, rispettalo; altrimenti resta local-only. Non creare/configurare remote.
7. Nel target fai un solo preflight: branch, status, remote e diff SOLO dei 5 file noti. Preserva ogni hunk estraneo. Se gli hunk `pip_user` sono già committati, verifica containment e non duplicare.
8. Se restano hunk intenzionali: stage selettivo; esegui una sola volta `python3 -m unittest tests.test_core -v`, `python3 -m py_compile updater/core.py updater/updaters.py updater/cli.py`, `git diff --check`; crea UN commit locale contenente solo gli hunk in-scope. Push solo se il checkout aveva già un remote canonico writable; local-only => nessun push.
9. Tramite single writer registra la recovery minima di 417592 preservando la sua execution storica BLOCKED e collegandola a 936284. Verifica che un secondo `register-local-repo` sullo stesso path sia no-op. Finalizza 936284 e STOP.

# Acceptance
PASS solo se MegaVault risolve deterministicamente un repo local-only dal worktree con project_id canonico e idempotente; nessun remote/ID è inventato; i regression test mirati passano; gli hunk `pip_user` sono persistiti esattamente una volta senza lavoro estraneo; 417592 non resta blocker operativo; secondo register/reconcile è no-op.

# Report
Massimo 8 righe: RESULT, MEGAVAULT_CONTRACT, PROJECT_ID, MEGAVAULT_COMMIT, TARGET_COMMIT, TESTS, IDEMPOTENCE, BLOCKER.