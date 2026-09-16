[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=731845 | project_id=23 | model=GPT-5.5 | reasoning=low | MegaVault=STANDARD`

# Goal
Correggere SOLO i falsi blocker prodotti da `940316` e chiudere l'audit di pubblicazione per `codex-roadmap`, `codex-usage-monitor` e `PersonalHub`, senza riesplorare gli altri repository.

# Starting point autoritativo
`940316` ha già eseguito gitleaks full-history, ma il suo classificatore path/workflow ha prodotto falsi positivi: file sorgente/documentazione contenenti parole come `session`, `token` o `secret` sono stati marcati sensibili per nome; `actions/checkout@v4` e `actions/setup-python@v5` sono stati marcati erroneamente come third-party. Il report v1 inoltre non registra l'HEAD SHA realmente scansionato, quindi la freschezza corrente non è dimostrabile.

Usa come classificatore canonico:
`/home/daniele/projects/codex-roadmap/tools/repository_publication_policy.py`

Output autoritativi da aggiornare:
- `/home/daniele/projects/MegaVault/ai/repository-publication-audit.json`
- `/home/daniele/projects/MegaVault/ai/repository-ci-handoff.json`
- `/home/daniele/projects/MegaVault/ai/repository-public-private-matrix.md`

Non leggere README/roadmap/spiegazioni/MEMORY o altra documentazione salvo blocker concreto. Non fare audit generale dei tre codebase.

# Scope
1. Sincronizza PRIMA delle modifiche, solo fast-forward, i checkout canonici dei tre target, MegaVault e codex-roadmap; registra gli SHA remoti iniziali. Se un checkout ha modifiche locali non pertinenti, non toccarle.
2. Poiché manca `scanned_head_sha`, esegui UNA nuova scansione gitleaks full-history/all-refs SOLO sui tre target, in batch, con raw JSON esclusivamente sotto `/tmp`, `--redact`, mai `cat` del raw report e mai valori di secret nel transcript.
3. Per tree/history path heuristics usa SOLO `repository_publication_policy.py`: `ignore` non è finding; `advisory` non blocca; `review` richiede una sola ispezione mirata del contenuto; `block` blocca. Non creare un altro classificatore temporaneo.
4. Per Actions controlla soltanto i rischi concreti già previsti da `940316`. `actions/*` con tag mutabile è advisory, non `third_party_action_not_sha_pinned`; un vero action esterno mutabile resta review.
5. Per ciascun target registra nel report almeno `scanned_head_sha`, esito gitleaks, path/workflow findings effettivi, `history_clean`, `publication_ready`, `current_visibility` e `visibility_apply_status`. Aggiorna il report a schema v2 senza perdere le entry degli altri repo.
6. Se un target è PASS, history/tree puliti al suo `scanned_head_sha` corrente e non ha remediation obbligatorie, rendilo PUBLIC con `gh repo edit ... --visibility public --accept-visibility-change-consequences`. Altrimenti resta PRIVATE con blocker concreto. Non usare il solo nome di un file come blocker.
7. Non modificare sorgenti dei tre target. Non toccare `logseq_updates` né `salute`: hanno ownership separata (`logseq_updates` ha un finding gitleaks reale; `salute` è baseline PRIVATE).
8. Prima del commit MegaVault fai un solo fetch finale. Se il remoto è avanzato, STOP `BLOCKED`: niente rebase/merge. Poi parse JSON, `git diff --check`, un solo commit+push MegaVault e UNA inventory GitHub finale globale per verificare la visibility.

# Efficienza
Un solo batch scan; raggruppa i check read-only; riusa gli output; niente help/probe se il comando è già noto; niente retry identici; niente audit post-PASS. Obiettivo indicativo: ≤12 tool-call salvo finding reale nuovo.

# Acceptance
- I tre target sono stati rivalutati sul loro HEAD attuale con `scanned_head_sha` registrato.
- Nessun `*.py`, `*.kt`, `*.md`, `*.service`, `*.timer`, `.codex/CODE_MAP.tsv` o file equivalente è bloccato solo per keyword nel nome.
- `actions/checkout@v4` / `actions/setup-python@v5` non risultano third-party blocker.
- Ogni repo clean è PUBLIC; ogni repo non clean resta PRIVATE con evidenza concreta.
- Report v2, matrix e handoff sono coerenti e pushati una sola volta.

# Stop
Dopo acceptance PASS esegui:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 731845 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 731845`

Se il guard o il push obbligatorio falliscono usa `RESULT=BLOCKED`. Prima riga finale obbligatoria `RESULT=PASS|BLOCKED|FAIL`; poi massimo 6 righe con target PASS/BLOCKED, visibility finali e commit MegaVault.
