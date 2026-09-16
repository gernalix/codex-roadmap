[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=827614 | project_id=8 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Completare e distribuire sul Fedora il watcher GitHub Actions già aggiunto a `gernalix/codex-usage-monitor`, in modo che i fallimenti CI dei repo `gernalix` diventino incidenti deduplicati e consultabili anche da ChatGPT tramite il repo privato `gernalix/codex-usage`.

Comportamento richiesto:
- monitora i repo source non archiviati dell'owner `gernalix`;
- chiave incidente = `repo + workflow_id + branch`;
- primo failure apre l'incidente e genera **una sola** notifica Telegram;
- ulteriori run falliti dello stesso incidente aggiornano stato/conteggio ma **non** generano altre notifiche;
- il primo success successivo chiude l'incidente e genera una sola notifica di recovery;
- pubblica lo snapshot in `codex-usage/index/github-actions.json` con incidenti attivi e transizioni recenti;
- nessun commit remoto se lo stato semantico è invariato e cambiano solo timestamp/metadata di osservazione.

# Starting point verificato
- runtime canonico: Fedora locale, non Oracle VM;
- repo locale: `/home/daniele/projects/codex-usage-monitor`;
- `origin/main` contiene almeno:
  - `1e1f71ded8b491440efb54e201f4166a9485e563` — `github_actions_watch.py`;
  - `2e736eddc125a6ef5494a9a1e4bc3b09ac02b46c` — watcher incluso in `deploy_runtime.py`;
  - `2516d3e43dc29a5d89f0986e5696a0e1350f9bca` — watcher aggiunto come ultimo `ExecStart` del publisher service;
- il watcher usa `gh` per leggere Actions, lo stato locale sotto `~/.local/state/codex-usage-publisher/`, Telegram tramite `codex_usage_monitor`, e il repo privato locale `~/projects/codex-usage` per pubblicare lo snapshot;
- **hardening da verificare prima del deploy:** la versione iniziale può generare commit inutili se `generated_at_utc` o campi volatili come `last_observed_at` cambiano pur senza una variazione semantica. Correggi solo questo se ancora presente.

# Esecuzione minima
1. Una sola fotografia Git di `codex-usage-monitor`; dirty non riconducibile al task => BLOCKED, niente stash/reset.
2. `git pull --ff-only origin main` una volta. Verifica `gh auth status`; se l'account non può leggere i repo necessari, BLOCKED senza riconfigurare credenziali.
3. Ispeziona **solo** `github_actions_watch.py`, `deploy_runtime.py`, `systemd/codex-usage-publisher.service` e collaboratori diretti indispensabili. Nessun audit generale.
4. Se il problema dei commit volatili è presente, fai il minimo fix: lo snapshot remoto deve ignorare timestamp/metadata puramente osservazionali nel confronto semantico. Non cambiare la policy di deduplica.
5. Aggiungi solo test mirati per: apertura incidente, repeated failure senza nuova notifica, recovery, bootstrap aggregato e snapshot semanticamente invariato => nessun publish. Niente suite/test ridondanti.
6. Esegui i test mirati. Se PASS, commit/push delle sole modifiche task-related. Attendi il CI del nuovo HEAD una volta; se fallisce, leggi solo job/log pertinente e correggi solo una causa concreta del task. Massimo un retry con nuova evidenza.
7. Solo con CI verde, esegui `python3 deploy_runtime.py` una volta e verifica che `current` punti al nuovo HEAD e includa `github_actions_watch.py`.
8. Confronta `systemd/codex-usage-publisher.service` del repo con `~/.config/systemd/user/codex-usage-publisher.service`; installa la versione repo solo se differisce, poi `systemctl --user daemon-reload` una volta.
9. Esegui dal runtime un solo `github_actions_watch.py run --dry-run`: deve scansionare `>0` repo, senza auth/global error; non deve inviare Telegram né pushare.
10. Avvia una sola volta `systemctl --user start codex-usage-publisher.service`. Verifica exit 0 e che publisher + chat dump preesistenti restino funzionanti.
11. Verifica su `origin/main` di `~/projects/codex-usage` che esista `index/github-actions.json`, che il repo sia privato e che lo snapshot contenga `active_incident_count`, `active_incidents`, `recent_events`, `scan_errors`.
12. Esegui subito una seconda run **normale** del watcher solo per la deduplica: se nel frattempo non c'è stata una reale transizione CI, deve produrre `events=0`, nessuna nuova notifica e `publish.status=noop`. Se c'è stata una vera transizione, documentala invece di forzare il noop.

# Vincoli
- Non creare failure fittizi e non inviare notifiche di test.
- Il bootstrap può inviare **un unico riepilogo aggregato** degli incidenti realmente aperti; mai una notifica per ogni run storico fallito.
- Nessun refactor/cleanup/modernizzazione fuori scope.
- Nessuna modifica ai workflow CI dei repo monitorati.
- Nessuna modifica alla VM Oracle.
- Non indagare la causa dei singoli CI falliti in questo task: qui si implementa solo il canale di osservabilità/deduplica.
- Problemi collaterali: segnala senza investigarli salvo blocker.

# Acceptance
PASS solo se: test mirati + CI remoto PASS; runtime Fedora aggiornato; service user aggiornato e sano; scan live autorizzato; snapshot privato pubblicato e leggibile da GitHub; una seconda run invariata non crea né commit né notifica; repeated failure resta un solo incidente fino al recovery.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 827614 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 827614`

Output massimo 6 righe: RESULT, TEST/CI, DEPLOY/SERVICE, SCAN, SNAPSHOT/DEDUP, BLOCKER.