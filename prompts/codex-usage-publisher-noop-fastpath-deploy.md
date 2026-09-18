PROMPT_ID=319311 | project_id=8 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Distribuisci SOLO il fast-path già presente su `gernalix/codex-usage-monitor/main` che evita il full scan di tutti i rollout quando i sorgenti Codex sono invariati, quindi verifica sul Fedora reale che un secondo run consecutivo del publisher termini come `noop_unchanged_sources`. Nessun redesign.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/codex-usage-monitor`, branch `main`;
- remoto: `gernalix/codex-usage-monitor`;
- baseline minima da includere: `cdcf6354508d9f08cb9f4cde01475070da70c976`;
- il fix remoto salva uno snapshot fail-safe di path/size/mtime/ctime dei rollout e lo invalida se cambia la semantica del publisher o resta stato non pubblicato;
- i test remoti coprono: no reparse/no repo-sync sui sorgenti invariati e invalidazione su cambio generation;
- runtime canonico: `/home/daniele/.local/lib/codex-usage-monitor/current`;
- prima del fix, PROMPT_ID=468205 ha mostrato ~30 s di lavoro publisher durante un run che ha pubblicato 0 prompt cycles;
- nessuna modifica source è richiesta in questo task.

# Esecuzione minima
1. In UNA shell call fail-fast nel repo:
   - richiedi `main` e worktree pulito;
   - `timeout 20s git fetch origin main` + `git merge --ff-only origin/main`;
   - richiedi `HEAD=origin/main` e `git merge-base --is-ancestor cdcf6354508d9f08cb9f4cde01475070da70c976 HEAD`;
   - esegui SOLO:
     `PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_repo.py tests.test_usage_publisher tests.test_publication_semantic_backfill`;
   - solo dopo PASS: `PYTHONDONTWRITEBYTECODE=1 python3 deploy_runtime.py --skip-fetch`.
2. Se test/deploy falliscono: `BLOCKED` e STOP. Non patchare codice, non fare retry equivalente.
3. In UNA seconda shell call, senza round-trip modello tra i due run:
   - esegui due volte consecutive `/home/daniele/.local/lib/codex-usage-monitor/current/codex_usage_publisher.py run`, misurando separatamente il wall time;
   - il primo run può fare il normale reconcile necessario dopo il cambio generation;
   - il secondo run DEVE restituire `status=noop_unchanged_sources`;
   - non avviare `codex-usage-publisher.service`: include anche chat-dump e GitHub-Actions watch e falserebbe il benchmark del solo publisher.
4. Verifica una sola volta che `codex-usage-publisher.timer` sia enabled e che l'ultimo risultato della relativa service non sia failed. Nessun journal dump ampio.
5. Dopo PASS esegui una sola volta:
   `python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 319311 --confirm-executed`.

# Acceptance
PASS solo se:
- test mirati PASS;
- runtime deploy PASS sulla baseline richiesta o successiva;
- secondo run consecutivo = `noop_unchanged_sources`;
- wall time dei due run riportato in forma compatta per confronto;
- timer ancora enabled e service non failed.

# Scope / stop
Niente audit generale, suite completa, modifiche source, ricostruzione archivio, benchmark di chat-dump/GitHub-Actions, tuning ulteriore o verifiche post-PASS.

Output massimo 6 righe: `RESULT`, `TESTS`, `DEPLOY`, `RUN1`, `RUN2`, `TIMER`.
