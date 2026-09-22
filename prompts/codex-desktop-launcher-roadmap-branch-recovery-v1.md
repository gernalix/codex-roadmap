PROMPT_ID=403496 | PARENT_PROMPT_ID=989559 | project_id=23
MODEL=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST
REPO=gernalix/chrome-codex-switcher

# Goal
Recupera 989559 dal SOLO blocker di bootstrap `roadmap_pull_blocked:branch_mismatch:expected=main:actual=master`, poi completa il launcher desktop-first definito dal prompt canonico 989559. Il parent non ha eseguito modifiche applicative: non rifare audit o recovery inesistenti.

# Evidenza già verificata
- 989559 è canonically BLOCKED, senza fix/replacement.
- L'unica execution è durata ~9 s con 1 tool-call e si è fermata prima del worktree: `roadmap_start.py --prompt-id 989559` -> `branch_mismatch:expected=main:actual=master`.
- gernalix/codex-roadmap ha default branch canonico `main`.
- Dipendenza 472615 è già completed; il task 989559 può procedere dopo il bootstrap.
- Il prompt canonico 989559 contiene già scope/acceptance completi per gernalix/chrome-codex-switcher: riusalo, non riscriverlo né ampliararlo.

# Esecuzione minima
0. SOLO perché il claim è il blocker: prima di `roadmap_start`, ispeziona `/home/daniele/projects/codex-roadmap` con `git status --porcelain=v1 -b`, branch corrente e `origin/main`. Fai un solo fetch di origin.
1. Se il checkout è già su `main`, non mutarlo. Se è su `master` ed è CLEAN e senza commit locali/divergenza rispetto a `origin/main`, passa in modo non distruttivo a `main` tracking `origin/main`. Se è dirty o divergente, BLOCKED con la sola evidenza precisa; vietati reset/stash/clean/rebase distruttivi.
2. Ora esegui `roadmap_start.py --prompt-id 403496` e usa solo il worktree restituito. Non tentare di riaprire 989559.
3. Leggi UNA volta il prompt canonico 989559 e applicane esattamente scope, non-goal e acceptance correnti. Parti dai componenti AT-SPI/daemon già indicati; niente esplorazione repo-wide.
4. Riusa l'infrastruttura desktop-first già presente. Implementa solo il consumer operativo mancante per launch spec: exact project/repo + model + reasoning, prompt nel composer NON inviato, lifecycle/title binding fail-closed. Nessun clipboard/uinput/coordinate/image matching/Chrome ChatGPT.
5. Test: prima solo mirati ai file modificati; poi UNA suite repo finale. Un solo smoke Fedora reale sui gate non distruttivi. Niente retry identici senza nuova evidenza.
6. Appena acceptance 989559 è soddisfatta, finalizza 403496 PASS e STOP. 989559 resta BLOCKED storico ma è risolto dalla relazione fix.

# Acceptance
PASS solo se il branch mismatch roadmap è risolto senza perdere lavoro locale e il comportamento richiesto da 989559 è completato/testato end-to-end nel nuovo fix; nessuna nuova tab ChatGPT Chrome, prompt non inviato automaticamente, exact-match/fail-closed preservati.

# Report
Massimo 9 righe: RESULT, PARENT_989559, ROADMAP_BRANCH, DESKTOP, PROJECT, MODEL_REASONING, COMPOSER, TESTS, BLOCKER.