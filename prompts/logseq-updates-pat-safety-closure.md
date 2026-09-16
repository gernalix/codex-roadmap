[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=518264 | project_id=23 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Sanificare in modo fail-closed il finding gitleaks reale `github-pat` nella history di `gernalix/logseq_updates`, senza esporre mai il valore del token, quindi rivalutare la pubblicabilità del repo.

# Starting point autoritativo
`940316` ha trovato esattamente un finding gitleaks `github-pat` in history, path `logseq_updates.bat`, commit abbreviato `41ff0d119e3c`. `logseq_updates` è attualmente PRIVATE e baseline `PUBLIC_AFTER_AUDIT`. Non rieseguire discovery generale prima di agire.

Checkout canonici:
- `/home/daniele/projects/logseq_updates` se presente; altrimenti usa un mirror temporaneo autenticato tramite `gh`.
- `/home/daniele/projects/MegaVault`
- `/home/daniele/projects/codex-roadmap`

Output MegaVault da aggiornare SOLO per `logseq_updates`:
- `ai/repository-publication-audit.json`
- `ai/repository-ci-handoff.json`
- `ai/repository-public-private-matrix.md`

Non leggere README/roadmap/spiegazioni/MEMORY o altri repo salvo blocker concreto.

# Safety
- Il secret non deve apparire in prompt, shell argv, stdout/stderr, diff, commit message, report o risposta finale.
- Qualunque raw gitleaks JSON o replace-map contenente il secret deve vivere solo in una directory `/tmp` mode 0700; file sensibili mode 0600; rimuovili prima dello stop.
- Il repo resta PRIVATE fino a history pulita e stato credential non attivo/provato sicuro.
- Niente rewrite direttamente nel checkout canonico: usa un mirror fresco sotto `/tmp` e conserva il clone canonico intatto finché il remote rewrite non è verificato.

# Scope
1. Sincronizza fast-forward-only PRIMA delle modifiche e registra gli SHA remoti iniziali. Se il remoto avanza durante il task, STOP `BLOCKED`: niente merge/rebase del lavoro concorrente.
2. Esegui una sola gitleaks full-history/all-refs con `--redact` e report raw in `/tmp`. Conferma programmaticamente che il finding target esista; non stamparne il valore.
3. Se è possibile estrarre il valore dal raw report senza output, fai al massimo UNA verifica read-only verso GitHub in Python/in-memory (`Authorization` mai in argv/log) e registra soltanto `credential_state=active|inactive|unknown`. Non stampare identità/account restituiti. Se non è verificabile in sicurezza, usa `unknown`.
4. Se `git-filter-repo` non è già disponibile, STOP `BLOCKED`; non installare tool e non improvvisare rewrite. Se disponibile, nel mirror sostituisci SOLO il secret rilevato usando un replace-map temporaneo protetto; non fare cleanup non correlato.
5. Verifica nel mirror: gitleaks full-history/all-refs pulito, refs/branch/tag attesi preservati, e nessun valore secret nei file correnti. Solo allora force-push dei refs riscritti al remote PRIVATE. Se la credential risulta `active`, il rewrite può essere completato ma il repo DEVE restare PRIVATE e il risultato finale è `BLOCKED` con azione manuale `revoke/rotate credential`; non tentare endpoint di revoca non documentati.
6. Dopo push, crea un mirror fresco e fai UNA verifica gitleaks full-history. Registra `scanned_head_sha` nel report schema v2.
7. Se `credential_state=inactive`, history/tree sono puliti e non esistono altri blocker concreti, aggiorna report/matrix/handoff e puoi rendere PUBLIC il repo. Se `active|unknown`, resta PRIVATE con remediation esplicita; `unknown` non equivale a safe.
8. Riconcilia il checkout canonico solo dopo remote verification, senza perdere modifiche locali. Aggiorna SOLO l'entry `logseq_updates` in MegaVault. Parse JSON + `git diff --check`, un solo commit+push MegaVault.

# Non-goal
Nessun audit di altri repo, nessuna modifica CI generale, nessun refactor di `logseq_updates`, nessuna rotazione automatica di credenziali non supportata, nessun secondo scanner.

# Efficienza
Usa un solo mirror e un solo flusso Python/script per parsing+replacement; niente letture raw; niente retry identici; niente audit post-PASS. Obiettivo indicativo ≤12 tool-call salvo un failure reale del rewrite/push.

# Acceptance
- Il valore PAT non è mai comparso nel transcript/report.
- La history remota finale è gitleaks-clean oppure il task si ferma senza rendere pubblico il repo.
- `scanned_head_sha` finale è registrato.
- Se la credential è active/unknown, repo PRIVATE + remediation esplicita; se inactive e tutto pulito, publication decision coerente applicata.
- Nessun repo diverso da `logseq_updates` è modificato, salvo i tre output MegaVault e la finalizzazione roadmap.

# Stop
Dopo acceptance tecnica PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 518264 --confirm-executed`

Se resta necessaria revoca/rotazione manuale, NON completare la roadmap: `RESULT=BLOCKED`. Prima riga finale obbligatoria `RESULT=PASS|BLOCKED|FAIL`; massimo 6 righe, senza secret o fingerprint sensibili.
