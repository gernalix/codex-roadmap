PROMPT_ID=518264 | project_id=23 | model=GPT-5.5 | reasoning=medium | MegaVault=STRICT

# Goal
Bonifica in modo fail-closed SOLO la vecchia history di `gernalix/logseq_updates` dal finding `github-pat`, verifica lo stato della credential senza esporla e aggiorna la decisione di pubblicabilità.

# Starting point autoritativo
- repo remoto attualmente PRIVATE, branch `master`;
- HEAD remoto minimo noto: `229e999ca6073d70cac01eedf520d5062843b04f`; il precedente tentativo `518264` ha verificato che il remoto era ancora esattamente a questo commit;
- finding noto: `github-pat` nella history, path `logseq_updates.bat`, commit abbreviato `41ff0d119e3c`;
- il tree corrente è già sanificato: il batch usa `GITHUB_TOKEN` dall'ambiente e non contiene più il PAT;
- nello stesso fix remoto lo updater usa state/download atomici e aggiorna `last_run_number` solo dopo successo: NON toccare codice applicativo in questo task;
- checkout canonici: `/home/daniele/projects/logseq_updates`, `/home/daniele/projects/MegaVault`, `/home/daniele/projects/codex-roadmap`;
- output MegaVault modificabili SOLO per `logseq_updates`: `ai/repository-publication-audit.json`, `ai/repository-ci-handoff.json`, `ai/repository-public-private-matrix.md`;
- helper già testato: `/home/daniele/projects/codex-roadmap/tools/ensure_git_filter_repo.py`. Se `git-filter-repo` non è nel PATH, crea un venv effimero SOLO sotto `/tmp`, installa la versione pin `2.47.0`, verifica l'eseguibile e restituisce il path senza modificare il sistema globalmente. Non fare una seconda probe manuale equivalente.

Prompt autosufficiente: oltre al bootstrap MegaVault STRICT imposto dalle istruzioni globali, non rileggere README/roadmap/spiegazioni/MEMORY, audit globali o file capsule non necessari all'esecuzione. Usa solo i file/output esplicitamente necessari sotto.

# Safety
- Mai stampare secret, fingerprint, raw finding, header Authorization o replace-map.
- Artefatti sensibili soltanto sotto `/tmp` mode 0700/0600 e rimossi prima dello stop.
- Rewrite esclusivamente su mirror fresco; checkout canonico intatto fino alla verifica remota.
- Repo PRIVATE finché history e credential non sono provate sicure.
- Nessuna installazione globale. Il bootstrap di `git-filter-repo` è l'unica installazione ammessa e resta confinato nel venv `/tmp` del helper.

# Esecuzione minima
1. **Fotografia + tool preflight, una volta.** In un solo blocco read-only fotografa i tre checkout interessati e il remote `logseq_updates`. Il remote deve essere ancora `229e999...`; se è avanzato, `BLOCKED`, niente merge/rebase. Subito dopo esegui UNA volta `python3 /home/daniele/projects/codex-roadmap/tools/ensure_git_filter_repo.py`, parsea solo il JSON e conserva in memoria il campo `executable`. Se il helper fallisce => `BLOCKED`. Non rieseguire `which`, `command -v`, `--version` o altre probe equivalenti.
2. **Scan iniziale.** Crea mirror fresco in `/tmp`; esegui UNA gitleaks full-history/all-refs con `--redact` e report raw protetto. Conferma programmaticamente il finding target senza stamparlo. Se il finding atteso non è dimostrato o emergono condizioni incompatibili col rewrite mirato => `BLOCKED`.
3. **Credential.** Se il valore target può essere estratto in-memory senza output, fai al massimo UNA verifica read-only verso GitHub e registra solo `credential_state=active|inactive|unknown`. `unknown` non è safe. Non ripetere la verifica.
4. **Rewrite.** Usa direttamente l'eseguibile restituito dal helper per riscrivere SOLO il secret target nel mirror fresco, con replace-map temporaneo protetto. Nessun secondo tool discovery e nessun altro history rewriter.
5. **Verifica + push.** Nel mirror verifica UNA volta: gitleaks all-refs pulito + refs/branch/tag preservati. Poi force-push dei refs riscritti al remote ancora PRIVATE. Se la verifica pre-push fallisce, non pushare.
6. **Verifica post-push.** Crea un mirror fresco post-push e fai UNA seconda/finale scansione gitleaks full-history; registra solo `scanned_head_sha` e stato pulito/non pulito.
7. **Pubblicabilità.** Se `credential_state=inactive` e history/tree sono puliti, aggiorna SOLO le tre entry MegaVault di `logseq_updates` e applica la decisione di pubblicabilità coerente. Se `active|unknown`, repo resta PRIVATE e risultato `BLOCKED` con unica azione esterna `revoke/rotate credential`; non modificare la visibility.
8. **Riconcilia + cleanup.** Riconcilia il checkout canonico solo dopo verifica remota. Parse JSON + `git diff --check`; un solo commit/push MegaVault. Esegui una sola volta `python3 /home/daniele/projects/codex-roadmap/tools/ensure_git_filter_repo.py --cleanup`; rimuovi anche mirror/report/replace-map temporanei. Nessun audit di altri repo.

# Acceptance
PASS solo se il PAT non appare mai nel transcript, la history remota finale è gitleaks-clean, `credential_state=inactive`, `scanned_head_sha` è registrato e report/matrix/handoff MegaVault sono coerenti. `active|unknown` => `BLOCKED`, repo PRIVATE.

# Non-goal
Niente modifica del codice updater, CI generale, audit altri repo, secondo scanner, installazioni globali, dependency discovery ripetuta o cleanup non correlato.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 518264 --confirm-executed`

Non fare dry-run separati né controlli Git equivalenti dopo finalizzazione. Se il risultato è BLOCKED dopo il bootstrap, fai comunque il cleanup effimero una sola volta prima dell'output finale.
Prima riga finale `RESULT=PASS|BLOCKED|FAIL`; massimo 6 righe: `RESULT`, `HISTORY`, `CREDENTIAL_STATE`, `SCANNED_HEAD`, `MEGAVAULT`, `BLOCKER`.
