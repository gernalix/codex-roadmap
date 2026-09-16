PROMPT_ID=681247 | project_id=8 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal
Distribuisci sul Fedora reale il fix già verde del backfill semantico di `codex-usage-monitor`, esegui UNA sola run reale del publisher e chiudi il precedente failure `742615=UNKNOWN` verificando anche che il layout cycle-aware di `583214` resti integro.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/codex-usage-monitor`, branch `main`, project_id `8`;
- commit minimo richiesto: `87897b4372d5afd93a5c0cc68c5445cde7228494` o successivo;
- GitHub Actions run `35107271755` sul commit minimo è **PASS**: NON rieseguire test deterministici/lint localmente;
- il precedente run `681247` ha già provato: deploy precedente PASS, publisher PASS, timer enabled+active, `583214` cycle-aware PASS; unico failure: `742615` rimasto `UNKNOWN`;
- root cause già corretta sul remoto: la vecchia migrazione fingerprint poteva assorbire una modifica semantica senza ripubblicare record già esistenti. `PUBLICATION_SEMANTICS_VERSION=2` ora sala il fingerprint, quindi i record pubblicati attraversano una volta il normale percorso pending/publish e lo state DB non viene anticipato prima del push riuscito;
- il parser canonico riconosce già `FIXED`; NON modificarlo;
- runtime canonico: Fedora locale; Oracle VM NON è runtime;
- repo dati privato: `/home/daniele/projects/codex-usage`;
- `742615` può risultare già `FIXED` nel checkout dati a causa di publish successivi: non è un motivo per saltare deploy + singola run del nuovo runtime.

Prompt autosufficiente: niente README/roadmap/spiegazioni/MEMORY/MegaVault, audit repo-wide, modifica codice, test suite o discovery.

# Esecuzione minima — massimo 4 blocchi operativi
1. **Sync + deploy in un solo blocco bounded.** Nel checkout `codex-usage-monitor`: verifica branch/dirty state; se dirty non pertinente => `BLOCKED`. Altrimenti fai UNA `git fetch origin main`, UNA `git merge --ff-only origin/main`, verifica che `87897b4372d5afd93a5c0cc68c5445cde7228494` sia antenato di HEAD e lancia UNA volta `python3 deploy_runtime.py`. Nessun `rev-parse/status` duplicato dopo il deploy.
2. **Publisher + systemd in un solo blocco bounded.** Esegui `timeout 120s systemctl --user start codex-usage-publisher.service`; subito dopo, nello stesso blocco, leggi solo `Result`, `ExecMainStatus`, `ExecMainCode`, `InvocationID`; verifica `codex-usage-publisher.timer` enabled+active e cerca nel journal della sola invocation `traceback|error|exception|failed|fatal`. Non fare polling: `systemctl start` deve attendere la oneshot; se timeout/failure => `BLOCKED/FAIL`, stop.
3. **Verifica dati in un solo blocco** nel checkout `codex-usage`, preferibilmente con un unico Python/jq script compatto:
   - `583214`: almeno i 3 cicli già provati devono essere ancora presenti; path indice univoci e tutti `prompts/583214/cycles/<cycle_key>`; ciascun path deve avere `metrics.json` + `transcript.jsonl`; alias flat presente e riferito al ciclo cronologicamente più recente;
   - `742615`: tutte le righe correnti nell'indice per questo prompt e i relativi `metrics.json`, più alias flat, devono riportare `status=FIXED`; transcript del ciclo presente;
   - emetti solo due righe `583214=PASS|FAIL ...` e `742615=PASS|FAIL ...`, senza dump JSON completi.
4. Se 1–3 PASS, esegui una sola volta il finalizzatore race-safe:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 681247 --confirm-executed`

# Acceptance
PASS solo se il runtime Fedora include `87897b4...`, deploy e singola publisher run hanno successo senza errori, timer resta enabled+active, `583214` non perde cicli/layout e `742615` è `FIXED` in indice + ciclo + alias flat.

# Non-goal
Niente modifiche codice/formati, test CI locali, Telegram, quota monitor, analyzer, Oracle VM, cleanup, secondo publish, retry identici o audit post-PASS.

# Stop/output
Dopo `roadmap_finish.py` riuscito stop immediato. Nessun controllo Git successivo.
Prima riga finale `RESULT=PASS|BLOCKED|FAIL`; massimo 6 righe: `COMMIT/DEPLOY`, `PUBLISH`, `TIMER`, `583214`, `742615`, `BLOCKER`.
