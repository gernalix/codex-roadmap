PROMPT_ID=468205 | model=GPT-5.6 Luna | reasoning=low

# Goal
Distribuisci il fix già remoto del publisher e verifica che il ciclo di PROMPT_ID=742591 passi da `UNKNOWN` a `PASS`.

# Starting point autoritativo
- repo: `/home/daniele/projects/codex-usage-monitor`, branch `main`, remoto `gernalix/codex-usage-monitor`;
- commit minimo richiesto: `9650072daddcb5ba7198d02de9203db00aa5f0f0` (include parser/backfill già implementati + test mirati source-layout-safe);
- verifier canonico: `scripts/verify_repo.py`; non lanciare `unittest` diretto né impostare manualmente `PYTHONPATH`;
- runtime Fedora: `/home/daniele/.local/lib/codex-usage-monitor`;
- readback: `/home/daniele/projects/codex-usage/prompts/742591/cycles/220a18d0f267fc8be909e449/metrics.json`;
- nessuna modifica source è richiesta in questo task.

# Esecuzione minima
1. In UNA shell call nel repo monitor usa `set -euo pipefail`: richiedi branch `main` e worktree pulito; `timeout 20s git fetch origin main`; `git merge --ff-only origin/main`; richiedi `HEAD=origin/main` e `git merge-base --is-ancestor 9650072daddcb5ba7198d02de9203db00aa5f0f0 HEAD`; poi esegui:
   `PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_repo.py tests.test_publishing_status tests.test_publication_semantic_backfill`
   e SOLO se PASS:
   `PYTHONDONTWRITEBYTECODE=1 python3 deploy_runtime.py --skip-fetch`.
2. Se la shell precedente fallisce: `BLOCKED` e STOP. Nessun retry equivalente, nessuna patch, nessun deploy manuale.
3. In UNA seconda shell call fail-fast: avvia una sola volta `codex-usage-publisher.service`; attendi il completamento normale; fai al massimo un `git -C /home/daniele/projects/codex-usage pull --ff-only`; leggi SOLO il JSON indicato e richiedi `status == "PASS"`.
4. Solo dopo il readback PASS esegui nello stesso flusso:
   `python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 468205 --confirm-executed`.

# Scope / stop
Niente audit, suite complete, ricostruzioni archivio, MegaVault o verifiche post-PASS. Non modificare codice. Massimo 2 tool-call operative salvo un errore concreto che richieda riportare `BLOCKED`.

# Acceptance
PASS solo con test mirati PASS, deploy PASS, un solo publisher run completato senza errore e `status=PASS` nel metrics JSON.

Output massimo 5 righe: `RESULT`, `TESTS`, `DEPLOY`, `PUBLISH`, `STATUS_742591`.
