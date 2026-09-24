PROMPT_ID=588376 | PARENT_PROMPT_ID=357862 | project=logseq_updates | MegaVault=STRICT

# Goal
Dopo la revoca manuale del PAT storico, bonifica la history di gernalix/logseq_updates e attiva/verifica l'updater Fedora già implementato. Non ridisegnare la feature.

# Starting point
- repo: /home/daniele/projects/logseq_updates, solo main;
- 30e22d50a6cbc9ba1440689d13a2c092044bc686 deve essere antenato; main può essere avanzato. Verificato remoto attuale: 8d0a752321e5b44e937df602aac81d32e3720598 con CI green e solo hardening CI sopra 30e22;
- finding storico noto: github-pat nel commit 41ff0d119e3c...; non stampare valore/fingerprint;
- helper: ~/projects/codex-roadmap/tools/ensure_git_filter_repo.py;
- il login/revoca PAT è prerequisito umano, non tentarlo.

# Esecuzione
1. Verifica PAT inactive prima di predisporre rewrite. active/unknown => BLOCKED e stop.
2. Su mirror fresco fai una sola scansione gitleaks all-refs redatta, riscrivi solo il secret target, verifica tree/tag preservati e gitleaks clean, quindi force-push solo main/tag necessari. Usa ensure_git_filter_repo e cleanup.
3. Sostituisci checkout canonico solo se clean; nessuno stash/reset distruttivo.
4. Aggiorna solo gli output MegaVault di publication audit già previsti dal workflow esistente, senza inglobare dirty work non correlato.
5. Esegui unittest/py_compile, installa le due user unit già presenti, enable timer, un E2E --reinstall-latest e una seconda invocation no-op. Nessun browser/web search.

# Acceptance
PASS solo con PAT inactive, history clean, solo/default main, checkout riconciliato, test PASS, timer enabled+active, E2E install PASS e seconda invocation no-op. Stop dopo PASS.
