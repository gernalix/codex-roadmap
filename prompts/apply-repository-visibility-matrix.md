[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=643812 | project_id=23 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Applicare su GitHub la matrice pubblico/privato già validata dall'audit `PROMPT_ID=940316`, senza prendere nuove decisioni di sicurezza e senza modificare codice.

Sorgente autoritativa unica:
`/home/daniele/projects/MegaVault/ai/repository-public-private-matrix.md`

Questo task rende pubblici **solo** i repository esplicitamente `final_recommendation=PUBLIC` e realmente pronti alla pubblicazione; mette/lascia privati quelli classificati `PRIVATE`; ignora `RETIRE`.

# Precondizioni — fail closed
1. Leggi una sola volta la matrice e, solo se serve a risolvere un'incoerenza, il report `repository-publication-audit.md`.
2. Esegui una sola inventory GitHub con `gh repo list gernalix --limit 200 --json name,visibility,isArchived,url`.
3. Per rendere un repo PUBLIC devono essere contemporaneamente veri: `audit_status=PASS`, `final_recommendation=PUBLIC`, `history_clean=yes`, nessuna remediation obbligatoria pendente, `confidence=high`.
4. Se manca uno dei requisiti, NON pubblicare: lascia/porta PRIVATE e marca l'applicazione come `SKIPPED_NOT_READY` nella matrice.
5. `PASS_WITH_REMEDIATION`, `BLOCKED`, `UNKNOWN` o finding P0 non possono mai diventare PUBLIC in questo task.

Non rieseguire scanner, audit Git history o discovery delle codebase: l'audit precedente è autoritativo.

# Applicazione visibilità
Usa esclusivamente `gh`/GitHub API. Una singola `gh repo edit --help` è ammessa solo se serve confermare la sintassi della versione installata.

Per ogni riga non `RETIRE`:
- `PUBLIC` + precondizioni complete + repo private -> cambia visibility a public;
- `PUBLIC` + repo già public -> NOOP;
- `PRIVATE` + repo public -> cambia visibility a private;
- `PRIVATE` + repo già private -> NOOP;
- `RETIRE` -> SKIPPED, nessuna modifica;
- repo archived -> non riattivarlo.

Usa il flag esplicito richiesto da `gh` per accettare le conseguenze del cambio visibility. Non usare Chrome.

# Sicurezza
- nessuna modifica a branch, history, release, issue, workflow o settings non necessari alla visibility;
- nessuna rotazione/revoca credenziali in questo task;
- nessun secret value nei log;
- mai rendere pubblico un repo per "far passare" la CI se la matrice non lo autorizza;
- se un cambio PUBLIC fallisce, lascialo private e continua con gli altri;
- se un cambio PRIVATE fallisce su un repo che l'audit considera sensibile, registra P0/blocker ma continua: non fare workaround rischiosi.

# Verifica minima
Dopo tutti i tentativi esegui **una sola** nuova inventory GitHub e confrontala in memoria con il piano.
Aggiorna la matrice con `current_visibility`, `visibility_apply_status` (`APPLIED|NOOP|SKIPPED_NOT_READY|BLOCKED`) e timestamp, senza duplicare il report audit.
`git diff --check` sul solo file matrice, commit+push MegaVault una volta.

# Risparmio token
- due sole inventory GitHub totali: prima e dopo;
- nessuna lettura repo per repo;
- nessun `gh repo view` ripetuto;
- applica le modifiche in batch/loop;
- nessun retry identico: un secondo tentativo è ammesso solo dopo una causa concreta e un fix specifico;
- nessun audit post-applicazione.

# Acceptance
Completa il task anche come `APPLY_COMPLETE_WITH_BLOCKERS` se alcuni repo non sono modificabili, purché:
- nessun repo non autorizzato sia diventato pubblico;
- ogni repo autorizzato sia PUBLIC oppure abbia uno stato blocker esplicito;
- ogni repo `PRIVATE` sia private oppure abbia blocker esplicito;
- `RETIRE` non sia stato toccato;
- matrice aggiornata e pushata.

# Stop
Dopo `APPLY_COMPLETE` o `APPLY_COMPLETE_WITH_BLOCKERS`:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 643812 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 643812`

`push_verified=git_push_exit_0` è terminale. Output massimo 7 righe: RESULT, PUBLIC applied/noop/blocked counts, PRIVATE applied/noop/blocked counts, skipped-not-ready, RETIRE skipped, MegaVault commit, blocker P0 eventuale.