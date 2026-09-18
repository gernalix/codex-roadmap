PROMPT_ID=445388 | parent_prompt_id=255325 | project_id=23 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STRICT

# Goal
Dopo che il PAT storico esposto è stato revocato/disattivato manualmente, completa SOLO la bonifica della history di `gernalix/logseq_updates` e il deploy/verifica locale dell'updater Fedora già implementato. Non ridisegnare né riscrivere la feature.

# Starting point verificato
- Il run parent `255325` si è fermato correttamente con `credential_state=active`.
- Quel run ha già reso `main` il default remoto ed eliminato `master`; sul remoto deve esistere solo `main`. NON ripetere rename/delete branch.
- ChatGPT ha già implementato il nuovo updater Fedora e i test in `gernalix/logseq_updates`; HEAD atteso prima del rewrite: `30e22d50a6cbc9ba1440689d13a2c092044bc686`.
- Tree corrente autorevole: `logseq_updates.py`, `test_logseq_updates.py`, `requirements.txt`, `systemd/logseq-updater.service`, `systemd/logseq-updater.timer`, `.github/workflows/ci.yml`. BAT/XML/state Windows sono già rimossi dal tree corrente.
- Upstream verificato il 2026-09-18: `logseq/logseq/.github/workflows/build-desktop-release.yml` produce l'artifact `logseq-linux-x64-builds`.
- Finding storico noto: `github-pat` nel commit `41ff0d119e3c...`; non stamparne mai valore, fingerprint o raw finding.
- Checkout canonici: `/home/daniele/projects/logseq_updates`, `/home/daniele/projects/MegaVault`, `/home/daniele/projects/codex-roadmap`.
- MegaVault aveva già una modifica utente non correlata in `ai/repository-retention-checklist.md`: non modificarla, non stagearla e non includerla in commit.
- Output MegaVault consentiti SOLO per `logseq_updates`: `ai/repository-publication-audit.json`, `ai/repository-ci-handoff.json`, `ai/repository-public-private-matrix.md`.
- Helper rewrite: `/home/daniele/projects/codex-roadmap/tools/ensure_git_filter_repo.py`. Eseguilo direttamente; NON leggerne/cattarne il sorgente.

# Efficienza obbligatoria
- Risolvi `project_id=23` con UNA query diretta a `projects`; niente `PRAGMA`/schema discovery.
- Nessun browser/Computer Use, nessuna web search e nessuna ricerca su come revocare token.
- NON tentare mai revoca/rotazione del PAT: è un'azione manuale esterna e fuori scope.
- Verifica `credential_state` PRIMA di predisporre `git-filter-repo`. Se è `active|unknown`, cleanup e STOP immediato.
- Niente probe di tool già noti salvo il comando che serve davvero al gate.
- Nessun audit generale, nessun secondo scanner, nessun refactor/cleanup non necessario.

# Gate 1 — credenziale, prima di qualsiasi rewrite
1. Verifica in un batch: remote `main` unico/default, HEAD esattamente quello atteso, worktree target e roadmap; non modificare nulla.
2. Crea un solo mirror fresco protetto in `/tmp/logseq-rewrite-445388`. Esegui UNA scansione gitleaks full-history/all-refs redatta e conferma machine-only il finding target.
3. Verifica UNA sola volta lo stato della credenziale senza stamparla e registra solo `credential_state=inactive|active|unknown`.
4. Se `active|unknown`: NON eseguire/helper/provisionare `git-filter-repo`, NON cercare vie di revoca. Elimina il mirror con Python/`shutil.rmtree` (mai `rm -rf`), riporta `BLOCKED: revoke PAT manually` e STOP.
5. Solo se `inactive`, continua.

# Gate 2 — rewrite history
6. Esegui UNA volta `ensure_git_filter_repo.py`, parsea solo il JSON e usa l'`executable` restituito. Nessun probe equivalente.
7. Nel mirror già scansionato riscrivi SOLO il secret target. Verifica UNA gitleaks finale all-refs + preservazione tree/tag e force-pusha esclusivamente `main` e gli eventuali tag necessari. Non creare altri branch.
8. Clona un mirror fresco post-push e fai UNA sola scansione gitleaks finale. PASS security solo con history pulita e remote default/solo `main`.
9. Esegui `ensure_git_filter_repo.py --cleanup` una volta. Cleanup mirror/temp con Python, non shell destructive glob/rm.

# Gate 3 — checkout e MegaVault
10. Il rewrite cambia gli SHA. Prima di sostituire il checkout canonico, richiedi `git status --porcelain` vuoto per `logseq_updates`. Se dirty => BLOCKED senza stash/reset. Se clean, rinomina temporaneamente il vecchio checkout, clona fresco `main` nello stesso path canonico, verifica tree/remote e poi elimina il backup con Python.
11. Aggiorna SOLO i tre output MegaVault consentiti con history clean, default branch `main`, nuovo head e decisione di pubblicabilità coerente. Preserva la modifica utente già dirty; stage esplicitamente solo quei tre file. `git diff --check` + validazione minima MegaVault pertinente, un solo commit/push.

# Gate 4 — deploy Fedora già implementato
12. Nel checkout fresco esegui una sola volta:
   - `python3 -m unittest -v`
   - `python3 -m py_compile logseq_updates.py test_logseq_updates.py`
   - import di `requests` e del notifier Telegram canonico.
   Se un test fallisce, correggi SOLO il blocker concreto, riesegui il leaf test e committa/pusha il fix; niente refactor.
13. Verifica una sola discovery locale del launcher Logseq/AppImage usando il codice già presente. Non fare filesystem scan generale. Non toccare graph, `~/.logseq` o configurazione Logseq.
14. Installa i due file già presenti in `systemd/` sotto `~/.config/systemd/user/`, `daemon-reload`, quindi `enable --now logseq-updater.timer`. Non creare unit alternative o loop.
15. Esegui UN E2E reale con `python3 logseq_updates.py --reinstall-latest`: deve risolvere la latest successful build, scaricare `logseq-linux-x64-builds`, sostituire/verificare atomicamente l'AppImage e consegnare Telegram SUCCESS.
16. Avvia poi UNA volta `systemctl --user start logseq-updater.service`: deve essere un no-op exit 0 sulla stessa build. Verifica una volta timer `enabled` e `active`. I failure path sono già coperti dai test automatici: non generare un falso FAIL Telegram live.

# Acceptance
PASS solo se: PAT `inactive`; history remota gitleaks-clean; solo/default `main`; checkout canonico riconciliato; tre output MegaVault coerenti senza inglobare dirty work altrui; test locali PASS; timer user enabled+active; E2E install/verify PASS con Telegram SUCCESS; seconda invocation no-op exit 0.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 445388 --confirm-executed`

Se BLOCKED/FAIL non finalizzare. Output finale max 8 righe: `RESULT`, `CREDENTIAL`, `HISTORY`, `HEAD`, `MEGAVAULT`, `TESTS`, `SYSTEMD`, `TELEGRAM/BLOCKER`.
