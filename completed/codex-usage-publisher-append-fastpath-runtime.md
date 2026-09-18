PROMPT_ID=519247 | PARENT_PROMPT_ID=817264 | project_id=8 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Distribuisci sul Fedora reale l'ottimizzazione già presente su `gernalix/codex-usage-monitor/main` e verifica che un rollout Codex attivo con soli append non terminali non causi più un rescan completo del publisher.

# Starting point autoritativo
- repo: `/home/daniele/projects/codex-usage-monitor`, branch `main`;
- baseline remota minima: `623ae3bb65fdf0a0dbd46a4d65a0aa46fb12fc43`;
- il remoto contiene già:
  - fast-path append-aware: legge solo i byte nuovi; `task_complete`/`turn_aborted`, truncation/replacement, generation change o pending state forzano il parser completo;
  - source snapshot schema v2 con inode/device;
  - test per append non terminale, terminale e marker spezzato sul boundary;
  - `verify_repo.py --fail-on-resource-warning` deterministico;
- 817264 ha già chiuso correttamente parser/backfill 918274 e runtime publisher; non ripetere quel debugging;
- questo task è solo deploy + validazione locale dell'ottimizzazione;
- usa una NUOVA chat Codex: non serve trascinare il lungo contesto di 817264.

# Autonomia
Goal + acceptance definiscono lo scope; i passi sono il piano iniziale. Se un test/helper/config direttamente collegato a questa ottimizzazione fallisce, correggilo autonomamente, rilancia il leaf e continua. BLOCKED solo per blocker esterno/safety non risolvibile localmente.

# Esecuzione minima
1. Sincronizza `main` in modo non distruttivo; richiedi che la baseline minima sia antenata di HEAD.
2. Esegui:
   `PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_repo.py --fail-on-resource-warning tests.test_usage_publisher tests.test_usage_publisher_regressions tests.test_session_archive tests.test_task_costs`
   Se fallisce, correggi solo questo failure domain e rilancia il leaf necessario.
3. Se hai modificato codice/test/config, un solo commit/push finale dopo PASS.
4. Deploy:
   `PYTHONDONTWRITEBYTECODE=1 python3 deploy_runtime.py --skip-fetch`
5. Esegui un primo publisher runtime con `run --wait-lock-seconds 90` e misura il wall time. Dopo il cambio di source-snapshot schema è ammesso che questo primo run faccia un reconcile completo.
6. NON batchare il secondo run nella stessa shell call. Dopo che il primo tool call è tornato e questa sessione Codex ha quindi aggiunto nuovi eventi non terminali al proprio rollout, esegui in una NUOVA tool call:
   `codex_usage_publisher.py run --wait-lock-seconds 90`
   misura wall time e richiedi `status=noop_unchanged_sources`. `source_change=nonterminal_append` è l'evidenza ideale; `source_change=none` è accettabile solo se il timer ha già avanzato lo snapshot.
7. Verifica una volta: timer user `enabled` + `active`, ultima service non failed.
8. PASS solo con evidenza esplicita dei punti sopra; se un output obbligatorio si perde, recuperalo una sola volta in modo robusto invece di inferire PASS.

# Finalizzazione
PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 519247 --confirm-executed`

BLOCKED:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 519247 --result BLOCKED --confirm-executed`

FAIL:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 519247 --result FAIL --confirm-executed`

Output massimo 6 righe:
RESULT=PASS|BLOCKED|FAIL
HEAD=<sha>
TESTS=<PASS|...>
DEPLOY=<PASS|...>
RUNS=<run1 status/wall; run2 status/source_change/wall>
TIMER=<enabled/active/result>
