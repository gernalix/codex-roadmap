# Retained repositories — GitHub CI completion

`HANDOFF_ID=483921` · executor: **ChatGPT + GitHub** · not a Codex roadmap task

## Goal
Per tutti i repository esistenti e non `RETIRE` già elencati nell'handoff MegaVault, più `adb-device-keeper` se non ancora presente, rendere GitHub Actions la sede canonica di tutto il testing deterministico/sandboxabile ragionevolmente disponibile, senza duplicare CI già adeguata.

Sorgente autoritativa:
`/home/daniele/projects/MegaVault/ai/repository-ci-handoff.json`

Usa sempre la versione corrente del file. Lo scope è esattamente `repositories` + `adb-device-keeper` se assente, deduplicato per `name`. Non rifare inventory globale, audit segreti/pubblicabilità o decisioni PUBLIC/PRIVATE: la visibility dell'handoff è autoritativa per questa campagna.

## Principio
Un check appartiene a GitHub Actions se può girare senza dati personali, hardware fisico, account/sessioni reali, secret di produzione o infrastruttura live, eventualmente tramite fixture/mock/temp dir.

Quando applicabile copri:
- unit/integration/regression test;
- compile/build/lint/typecheck/static analysis;
- parser/DB con fixture o DB temporanei;
- Android build/unit/lint e instrumentation/emulator sandboxabile;
- browser/extension con Chromium headless + fixture locali;
- HTTP/network con mock/local server;
- shell/systemd/YAML/Compose/nginx/config validation;
- backup/restore solo in temp dir.

## Esecuzione minima per repository
1. Leggi solo manifest/build/packaging, test e `.github/workflows` necessari a capire copertura e invocation canonica.
2. Se la CI esistente copre già tutto il testing sandboxabile disponibile: `NOOP_COMPLETE` e passa oltre.
3. Altrimenti modifica il minimo, riusando test/comandi esistenti. Nessun refactor, dependency upgrade o cleanup collaterale.
4. Usa path filter docs-only, concurrency/cancel-in-progress, permissions minime, cache solo se utile e artifact failure-only con retention breve quando pertinenti.
5. Push una volta; verifica il singolo run GitHub canonico. Su failure apri solo job/log fallito, correggi quel failure domain e non fare retry identici.
6. Chiudi il repository appena raggiunge `COMPLETE`; non riaprirlo nella stessa campagna.

## Fast path già verificati
- `adb-device-keeper`: baseline minima `912a436174b9f655607cdd4f9e3ad0a4d650d14a`, run `35110215967` PASS. Se HEAD è quel commit o un discendente e non ci sono modifiche pertinenti a workflow/test/runtime, `NOOP_COMPLETE`; niente test locali.
- `PersonalHub`: riusa la Play Store preflight esistente (`lintPlay`, merged-manifest policy check, AAB `play` minified/shrunk e `tools/check_play_bundle.py`). Non creare un secondo workflow Play e non portare signing/keystore reali su Actions. Il gate firmato/emulatore locale resta separato nel prompt Codex `294731`.
- repository con CI già completa, inclusi eventuali `codex-roadmap`, `codex-usage-monitor` e `fedora-system-monitor`: verifica solo l'evidenza minima e usa `NOOP_COMPLETE` quando appropriato.

## Limiti
Restano locali solo test che richiedono davvero hardware fisico, browser/account autenticato reale, secret di produzione, VM/host/dischi/rete live non simulabili o comportamento umano non riducibile a fixture affidabile. Per ogni esclusione registra una motivazione tecnica concreta.

Per repository PRIVATE definisci comunque in Actions tutto il testing sandboxabile; se un job pesante consumerebbe minuti senza valore continuo, preferisci `workflow_dispatch` anziché rinunciare alla copertura. Non creare runner general-purpose.

## Output
Al termine crea/aggiorna in MegaVault `ai/repository-ci-coverage.json` con:
- `schema_version: 1`;
- `generated_by_handoff_id: 483921`;
- `generated_at_utc`;
- una entry per ogni repository dello scope effettivo con `status: COMPLETE|NOOP_COMPLETE|PARTIAL_BLOCKED`, workflow/gate principali ed eventuale test rimasto locale con motivo tecnico.

Ordina le entry per `name`. Non creare un secondo report Markdown.

## Acceptance
La campagna è completa quando ogni repository dello scope ancora esistente ha tutto il testing deterministico/sandboxabile ragionevolmente disponibile in GitHub Actions oppure un blocker tecnico esplicito; i workflow modificati sono verdi; non esistono CI duplicate introdotte dalla campagna; ciò che resta locale richiede realmente risorse non sandboxabili; `repository-ci-coverage.json` è parseabile e completo.
