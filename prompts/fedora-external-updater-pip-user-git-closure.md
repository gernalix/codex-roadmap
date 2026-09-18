PROMPT_ID=854653 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Chiudi SOLO la persistenza Git della feature/fix `pip_user` già implementata e verificata nella catena terminata con PROMPT_ID=537184 in `/home/daniele/projects/fedora-external-updater`. Non aggiungere feature, non rifare l'audit Python e non modificare il comportamento salvo che un test mirato dimostri un difetto bloccante.

# Evidenza già verificata
Alla fine di 537184:
- unit test: PASS 12/12;
- comando reale `apply --only pip_user --scope user`: PASS, exit 0;
- risultavano dirty questi 5 file:
  - `config/config.json`
  - `docs/human/README.md`
  - `tests/test_core.py`
  - `updater/core.py`
  - `updater/updaters.py`
- `config/config.json` e `docs/human/README.md` provengono dalla stessa feature `pip_user` precedente nella medesima sessione; gli altri file comprendono il fix 537184 per `TimeoutExpired bytes` e reboot-check DNF.
- Il report "Problemi residui: nessuno" era quindi incompleto: il lavoro non era ancora Git-closed.

# Esecuzione minima
1. Risolvi da MegaVault il project_id canonico del repo; non inventarlo e non fare discovery generale.
2. Nel repo target fai un solo preflight: branch, `git status --short`, remote configurati e diff SOLO dei 5 file sopra.
3. Verifica hunk per hunk che le modifiche ancora presenti appartengano alla feature/fix descritta. Preserva qualsiasi hunk estraneo o lavoro utente; se un file contiene modifiche miste, stage selettivo.
4. Esegui una sola verifica mirata:
   `python3 -m unittest tests.test_core -v`
   `python3 -m py_compile updater/core.py updater/updaters.py updater/cli.py`
   `git diff --check`
   Non rieseguire il comando reale pip salvo che lo stato attuale differisca materialmente dall'evidenza sopra.
5. Commit in un unico commit SOLO gli hunk intenzionali della catena `pip_user`/537184. Se esiste un remote Git canonico e writable, sincronizza in modo non distruttivo e push; se il repo è volutamente local-only, il commit locale è sufficiente.
6. Verifica che dopo il commit non restino modifiche della feature/fix non persistite. Modifiche estranee preesistenti possono restare dirty e vanno riportate senza toccarle.
7. Finalizza e stop. Niente audit post-PASS, refactor, cleanup, README extra o test equivalenti.

# Acceptance
PASS solo se:
- project_id canonico risolto;
- tutti e soli gli hunk intenzionali della feature/fix sono committati;
- test mirati, py_compile e diff-check PASS;
- nessun lavoro estraneo è incluso o perso;
- push completato se il repo ha un remote canonico writable, altrimenti è esplicitamente confermato local-only.

# Finalizzazione
PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 854653 --confirm-executed`

BLOCKED/FAIL:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 854653 --result BLOCKED --confirm-executed`
oppure `--result FAIL`.

Output massimo 6 righe:
`RESULT=PASS|BLOCKED|FAIL`
`PROJECT_ID=<id>`
`COMMIT=<sha|none>`
`TESTS=<PASS|...>`
`REMOTE=<pushed|local-only|...>`
`BLOCKER=<none|testo minimo>`
