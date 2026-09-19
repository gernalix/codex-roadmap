PROMPT_ID=257387 | project_id=15 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST

# Goal
Attiva sul Fedora reale il Context Index già implementato e mergiato in `gernalix/fedora-system-monitor`: deve correlare ogni 15 minuti il DB di Fedora System Monitor con il mirror locale `activity-watch-data`, produrre timeline/summary/incident bundle consultabili e pubblicarli nel nuovo repository PRIVATO `gernalix/fedora-context-data`.

Fai SOLO attivazione/runtime validation. Il design e il codice remoto sono già conclusi: non riprogettarli e non fare audit generali.

# Starting point autoritativo
- repo target: `gernalix/fedora-system-monitor`, locale canonico `/home/daniele/projects/fedora-system-monitor`;
- baseline minima già CI-PASS e mergiata in main: `75378b8e4fa907f8eaea6e7f7edb8eaf07315117`;
- ActivityWatch mirror locale: `/home/daniele/projects/activity-watch-data`;
- output previsto: `/home/daniele/projects/fedora-context-data`;
- DB runtime: `/var/lib/fedora-system-monitor/monitor.sqlite3`;
- config runtime: `/etc/fedora-system-monitor/config.toml`;
- il codice contiene già `context sync|around|incident|latest`, schema `fedora-system-monitor.incident-bundle.v1`, service/timer 15 minuti e publisher Git fail-closed;
- `context.git_push` è intenzionalmente false di default finché il repo dati non è bootstrap-ato;
- GitHub CLI deve essere usato senza stampare token/segreti.

# Esecuzione minima
1. PRIMA di leggere/modificare il target esegui:
   `python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 257387`
   Procedi solo se il claim restituisce running. Usa il `worktree_path` restituito come checkout autoritativo per eventuali test/fix source.
2. Verifica con un solo fetch bounded che la baseline minima sia antenata del branch del worktree. Non fare discovery repo-wide.
3. Esegui solo i gate locali pertinenti alla differenza ambiente CI→Fedora:
   `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_context_index tests.test_app tests.test_architecture -q`
   e `python3 -m compileall -q src/fedora_system_monitor/capsules/context_index.py src/fedora_system_monitor/app.py`.
   Se falliscono per un bug del Context Index, correggi SOLO quel failure domain, rilancia il leaf fallito e poi questi gate. Nessun refactor/cleanup.
4. Distribuisci dal worktree con `sudo ./scripts/install.sh`. Non sovrascrivere la configurazione runtime esistente con la distribution config. Verifica che `fedora-system-monitor-context.timer` sia installato, enabled e active.
5. Prima della pubblicazione, esegui come utente daniele una sola sync locale senza push:
   `fedora-system-monitor context sync --no-push`
   Richiedi output ok e presenza di `metadata/last-sync.json`, `metadata/sources.json`, almeno una timeline giornaliera e relativo summary.
6. Bootstrap GitHub in modo fail-closed:
   - verifica con `gh` se `gernalix/fedora-context-data` esiste;
   - se non esiste, crealo PRIVATO; se esiste, richiedi esattamente quel nome e visibility PRIVATE;
   - trasforma `/home/daniele/projects/fedora-context-data` nel checkout `main` del repo senza perdere i file derivati già generati;
   - fai il primo commit/push esplicito in modo che `origin/main` esista;
   - remote diverso, repo pubblico, branch inatteso o file locali non gestiti che rendono ambiguo il bootstrap => non forzare/reset/delete: raccogli il minimo diagnostico e recupera solo se deterministico.
7. Abilita SOLO `context.git_push = true` in `/etc/fedora-system-monitor/config.toml`, con backup prima dell'edit e preservando ogni altra impostazione. Valida con `fedora-system-monitor config-check`.
8. Avvia una sola volta `sudo systemctl start fedora-system-monitor-context.service`. Verifica:
   - service concluso con successo;
   - timer ancora enabled/active;
   - repo locale pulito dopo la pubblicazione;
   - `origin/main` contiene i file managed aggiornati.
9. Esegui una verifica funzionale bounded:
   - `fedora-system-monitor context latest --type graphics --json`;
   - se esiste un incident_id reale recente, esegui `context incident <id> --json` e richiedi schema `fedora-system-monitor.incident-bundle.v1`, timeline non vuota e presenza dei record Fedora; richiedi anche record ActivityWatch se il mirror copre temporalmente quella finestra;
   - esegui `context around <timestamp-recente> --before-minutes 2 --after-minutes 1 --json` e verifica entrambe le sorgenti quando disponibili.
   Non creare incidenti finti e non modificare le sorgenti canoniche per far passare il test.
10. Se al punto 3 o durante lo smoke emerge un bug source realmente necessario al goal, correggilo nel worktree `task/257387`, testalo e lascia che il finalizzatore/integratore gestisca PR/main; non fare modifiche fuori scope. Se nessun bug, nessun commit source aggiuntivo.
11. Appena gli acceptance criteria sono soddisfatti, finalizza e STOP.

# Acceptance
PASS solo se:
- runtime installato include la baseline minima o un fix in-scope successivo;
- sync locale produce metadata + timeline + summary;
- `gernalix/fedora-context-data` esiste ed è PRIVATE, con checkout/remote/branch canonici;
- runtime config ha `context.git_push=true` senza alterare altre impostazioni;
- una run reale del service pubblica con successo sul repo dati;
- timer context enabled+active e service non failed;
- query `around` funziona e, quando esiste un incident_id reale, anche il bundle incident rispetta lo schema;
- nessun raw URL ActivityWatch viene materializzato nel repo derivato;
- nessuna sorgente canonica viene riscritta dall'indexer.

# Recovery / limiti
Un failure locale correggibile NON è BLOCKED: usa il minimo diagnostico, fix in-scope, leaf retest, continua. Non ripetere lo stesso tentativo senza nuova evidenza. BLOCKED solo per autorizzazione/credential indispensabile, ambiguità dati non recuperabile in sicurezza o risorsa esterna realmente indisponibile. Niente audit generali, suite complete dopo PASS, tuning, nuove metriche, nuove notifiche o refactor.

# Finalizzazione
PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 257387 --confirm-executed`

BLOCKED:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 257387 --result BLOCKED --confirm-executed`

FAIL:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 257387 --result FAIL --confirm-executed`

Output massimo 8 righe: RESULT, BASELINE, LOCAL_GATES, DEPLOY, CONTEXT_SYNC, DATA_REPO, SERVICE_TIMER, INCIDENT_QUERY.
