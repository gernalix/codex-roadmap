[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=518264 | project_id=23 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Bonifica in modo fail-closed SOLO la vecchia history di `gernalix/logseq_updates` dal finding `github-pat`, verifica lo stato della credential senza esporla e aggiorna la decisione di pubblicabilità.

# Starting point autoritativo
- repo remoto attualmente PRIVATE, branch `master`;
- finding noto: `github-pat` nella history, path `logseq_updates.bat`, commit abbreviato `41ff0d119e3c`;
- il tree corrente è già sanificato su `229e999ca6073d70cac01eedf520d5062843b04f` o successivo: il batch usa `GITHUB_TOKEN` dall'ambiente e non contiene più il PAT;
- nello stesso fix remoto lo updater usa state/download atomici e aggiorna `last_run_number` solo dopo successo: NON toccare codice applicativo in questo task;
- checkout canonici: `/home/daniele/projects/logseq_updates`, `/home/daniele/projects/MegaVault`, `/home/daniele/projects/codex-roadmap`;
- output MegaVault modificabili SOLO per `logseq_updates`: `ai/repository-publication-audit.json`, `ai/repository-ci-handoff.json`, `ai/repository-public-private-matrix.md`.

# Safety
- Mai stampare secret, fingerprint, raw finding, header Authorization o replace-map.
- Artefatti sensibili soltanto sotto `/tmp` mode 0700/0600 e rimossi prima dello stop.
- Rewrite esclusivamente su mirror fresco; checkout canonico intatto fino alla verifica remota.
- Repo PRIVATE finché history e credential non sono provate sicure.

# Esecuzione minima
1. Fotografia Git dei tre checkout interessati. `logseq_updates` deve includere `229e999...`; se il remoto avanza durante il task, `BLOCKED`, niente merge/rebase.
2. Nel mirror `/tmp` esegui UNA gitleaks full-history/all-refs con `--redact` e report raw protetto. Conferma programmaticamente il finding target senza stamparlo.
3. Se il valore può essere estratto in-memory senza output, fai al massimo UNA verifica read-only verso GitHub e registra solo `credential_state=active|inactive|unknown`. `unknown` non è safe.
4. Se `git-filter-repo` non è già disponibile: `BLOCKED`, non installare. Se disponibile, riscrivi SOLO il secret target usando replace-map temporaneo protetto.
5. Nel mirror verifica UNA volta: gitleaks all-refs pulito + refs/branch/tag preservati. Poi force-push dei refs riscritti al remote ancora PRIVATE.
6. Crea un mirror fresco post-push e fai UNA seconda/finale scansione gitleaks full-history; registra solo `scanned_head_sha` e stato pulito/non pulito.
7. Se `credential_state=inactive` e history/tree sono puliti, aggiorna SOLO le tre entry MegaVault di `logseq_updates` e applica la decisione di pubblicabilità coerente. Se `active|unknown`, repo resta PRIVATE e risultato `BLOCKED` con azione manuale `revoke/rotate credential`.
8. Riconcilia il checkout canonico solo dopo verifica remota. Parse JSON + `git diff --check`; un solo commit/push MegaVault. Nessun audit di altri repo.

# Acceptance
PASS solo se il PAT non appare mai nel transcript, la history remota finale è gitleaks-clean, `credential_state=inactive`, `scanned_head_sha` è registrato e report/matrix/handoff MegaVault sono coerenti. `active|unknown` => `BLOCKED`, repo PRIVATE.

# Non-goal
Niente modifica del codice updater, CI generale, audit altri repo, secondo scanner o cleanup non correlato.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 518264 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 518264`

Output massimo 6 righe: `RESULT`, `HISTORY`, `CREDENTIAL_STATE`, `SCANNED_HEAD`, `MEGAVAULT`, `BLOCKER`.