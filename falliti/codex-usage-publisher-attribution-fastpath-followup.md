PROMPT_ID=538642 | PARENT_PROMPT_ID=319311 | project_id=8 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Distribuisci SOLO le correzioni già presenti su `gernalix/codex-usage-monitor/main`: fast-path del publisher per sorgenti invariati + riconoscimento robusto di `PROMPT_ID` con underscore Markdown escaped. Verifica sul Fedora reale che PROMPT_ID=918274 venga attribuito correttamente e che un secondo run consecutivo del publisher termini come `noop_unchanged_sources`. Nessun redesign.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/codex-usage-monitor`, branch `main`;
- remoto: `gernalix/codex-usage-monitor`;
- baseline minima da includere: `34bd4adbfe8918f77cb9f4054b77c75ee61fd5b6`;
- il fix remoto salva uno snapshot fail-safe di path/size/mtime/ctime dei rollout e lo invalida se cambia la semantica del publisher o resta stato non pubblicato;
- il parser del publisher tollera `PROMPT\\_ID`; il parser costi ora applica la stessa normalizzazione e i test coprono esplicitamente il caso reale `PROMPT\\_ID=918274`;
- evidenza reale da riconciliare: sessione `01a0b571-34c1-77a0-873b-79aab0d23acf`, chat 285, cycle `00a0f021a74b7246cbec3109`, attualmente pubblicato sotto `prompts/unassigned` pur appartenendo a PROMPT_ID=918274;
- runtime canonico: `/home/daniele/.local/lib/codex-usage-monitor/current`;
- prima del fast-path, PROMPT_ID=468205 ha impiegato >50 s nella service completa; il benchmark deve isolare il solo publisher;
- nessuna modifica source è richiesta in questo task.

# Esecuzione minima
1. In UNA shell call fail-fast nel repo:
   - richiedi `main`; dirty non sovrapposto non blocca;
   - `timeout 20s git fetch origin main` + `git merge --ff-only origin/main`;
   - richiedi `HEAD=origin/main` e baseline `34bd4adbfe8918f77cb9f4054b77c75ee61fd5b6` antenata;
   - esegui SOLO:
     `PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_repo.py tests.test_usage_publisher tests.test_publication_semantic_backfill tests.test_usage_publisher_regressions tests.test_task_costs`.
2. Se test o deploy falliscono: `BLOCKED` e STOP. Non patchare codice, non fare retry equivalente.
3. Solo dopo PASS:
   `PYTHONDONTWRITEBYTECODE=1 python3 deploy_runtime.py --skip-fetch`.
4. In UNA shell call, senza round-trip modello fra le verifiche:
   - misura un primo run di `/home/daniele/.local/lib/codex-usage-monitor/current/codex_usage_publisher.py run`; può fare il normale reconcile dopo il cambio di runtime;
   - verifica ESATTAMENTE in `/home/daniele/projects/codex-usage` che l'indice contenga una riga con `prompt_id=918274` per il cycle `00a0f021a74b7246cbec3109` e che esista `prompts/918274/metrics.json` con la stessa sessione/cycle. Non ripulire eventuali file storici `unassigned`;
   - misura subito un secondo run consecutivo dello stesso publisher: DEVE restituire `status=noop_unchanged_sources`.
   Per processi lunghi usa attese >=30 s; niente polling da 5 s.
5. Verifica una sola volta che `codex-usage-publisher.timer` sia enabled e che l'ultimo risultato della relativa service non sia failed. Nessun journal dump ampio.
6. Dopo PASS esegui una sola volta:
   `python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 538642 --confirm-executed`.

# Acceptance
PASS solo se:
- test mirati PASS;
- runtime deploy PASS sulla baseline richiesta o successiva;
- cycle reale 918274 pubblicato/indexato con il PROMPT_ID corretto;
- secondo run consecutivo = `noop_unchanged_sources`;
- wall time dei due run riportato in forma compatta;
- timer ancora enabled e service non failed.

# Scope / stop
Niente audit generale, suite completa, modifiche source, scansione manuale di tutti i rollout, benchmark di chat-dump/GitHub-Actions, cleanup dello storico `unassigned`, tuning ulteriore o verifiche post-PASS.

Output massimo 7 righe: `RESULT`, `TESTS`, `DEPLOY`, `BACKFILL_918274`, `RUN1`, `RUN2`, `TIMER`.
