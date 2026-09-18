PROMPT_ID=518264 | project_id=23 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Bonifica fail-closed SOLO la vecchia history di `gernalix/logseq_updates` dal finding `github-pat`, porta il repo allo standard di un solo branch `main`, verifica la credential senza esporla e aggiorna la decisione di pubblicabilità.

# Starting point autoritativo
- repo remoto PRIVATE;
- stato branch verificato: `main` e `master` puntano entrambi a `712741b38ca41d090c14084d1859f23d35e9c728`, `master` è ancora il default e non esistono altri branch;
- il workflow one-shot tentato per rinominare il default branch è stato rimosso dal tree; non ricrearlo;
- finding noto: `github-pat` nella history, path `logseq_updates.bat`, commit abbreviato `41ff0d119e3c`;
- tree corrente già sanificato: usa `GITHUB_TOKEN` dall'ambiente; NON toccare codice applicativo;
- checkout canonici: `/home/daniele/projects/logseq_updates`, `/home/daniele/projects/MegaVault`, `/home/daniele/projects/codex-roadmap`;
- output MegaVault modificabili SOLO per `logseq_updates`: `ai/repository-publication-audit.json`, `ai/repository-ci-handoff.json`, `ai/repository-public-private-matrix.md`;
- helper già testato: `/home/daniele/projects/codex-roadmap/tools/ensure_git_filter_repo.py`; se necessario crea venv effimero in `/tmp` con `git-filter-repo==2.47.0`.

Prompt autosufficiente: oltre al bootstrap MegaVault STRICT imposto dalle istruzioni globali, non rileggere README/roadmap/spiegazioni/MEMORY, audit globali o capsule non necessarie.

# Safety
- Mai stampare secret, fingerprint, raw finding, Authorization header o replace-map.
- Artefatti sensibili solo sotto `/tmp` mode 0700/0600 e rimossi prima dello stop.
- Rewrite esclusivamente su mirror fresco; checkout canonico intatto fino alla verifica remota.
- Repo PRIVATE finché history e credential non sono provate sicure.
- Nessuna installazione globale.

# Esecuzione minima
1. **Canonicalizza il branch prima del rewrite.** In un unico preflight verifica che `origin/main` e `origin/master` siano entrambi esattamente `712741b38ca41d090c14084d1859f23d35e9c728` e che non esistano altri branch. Usa direttamente l'auth GitHub già disponibile: `gh repo edit gernalix/logseq_updates --default-branch main`. Solo dopo successo verificato del default `main` esegui `git push origin --delete master`. Se cambio default o delete falliscono => `BLOCKED`, niente rewrite. Nel checkout locale rinomina/aggancia il branch a `main` senza stash/reset distruttivi.
2. Esegui UNA volta `python3 /home/daniele/projects/codex-roadmap/tools/ensure_git_filter_repo.py`, parsea solo il JSON e conserva `executable`. Se fallisce => `BLOCKED`. Niente probe equivalenti.
3. Crea mirror fresco in `/tmp`; esegui UNA gitleaks full-history/all-refs con `--redact` e report protetto. Conferma programmaticamente il finding target senza stamparlo. Se il finding atteso non è dimostrato o emerge un blocker incompatibile col rewrite mirato => `BLOCKED`.
4. Se il valore target può essere estratto in-memory senza output, fai al massimo UNA verifica read-only verso GitHub e registra solo `credential_state=active|inactive|unknown`. `unknown` non è safe.
5. Usa direttamente l'eseguibile restituito dall'helper per riscrivere SOLO il secret target nel mirror, con replace-map temporaneo protetto.
6. Verifica UNA volta gitleaks all-refs pulito + `main`/tag preservati, quindi force-pusha il `main` riscritto e i tag necessari al remoto ancora PRIVATE. Nessun `master` deve essere ricreato.
7. Crea un mirror fresco post-push e fai UNA seconda/finale scansione gitleaks full-history; registra solo `scanned_head_sha` e pulito/non pulito. Verifica anche che il remoto abbia default `main` e **solo** il branch `main`.
8. Se `credential_state=inactive` e history/tree sono puliti, aggiorna SOLO le tre entry MegaVault di `logseq_updates` e applica la decisione di pubblicabilità coerente. Se `active|unknown`, repo resta PRIVATE e risultato `BLOCKED` con unica azione esterna revoke/rotate credential.
9. Riconcilia il checkout canonico solo dopo verifica remota; parse JSON + `git diff --check`; un solo commit/push MegaVault. Esegui una sola volta l'helper con `--cleanup` e rimuovi mirror/report/replace-map temporanei.

# Acceptance
PASS solo se il PAT non appare mai nel transcript, il repo remoto usa default `main` e non ha altri branch, la history remota finale è gitleaks-clean, `credential_state=inactive`, `scanned_head_sha` è registrato e report/matrix/handoff MegaVault sono coerenti. `active|unknown` => `BLOCKED`, repo PRIVATE.

# Non-goal
Niente modifica updater, CI generale, audit altri repo, secondo scanner, installazioni globali, dependency discovery ripetuta o cleanup non correlato.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 518264 --confirm-executed`

Non fare dry-run o controlli Git equivalenti dopo finalizzazione. Se BLOCKED dopo bootstrap, esegui comunque il cleanup effimero una sola volta.
Prima riga finale `RESULT=PASS|BLOCKED|FAIL`; massimo 7 righe: `RESULT`, `BRANCHES`, `HISTORY`, `CREDENTIAL_STATE`, `SCANNED_HEAD`, `MEGAVAULT`, `BLOCKER`.
