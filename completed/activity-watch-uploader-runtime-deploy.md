PROMPT_ID=424261 | PARENT_PROMPT_ID=286419 | project_id=15 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Chiudi SOLO il gate finale ActivityWatch già operativo: porta il checkout Fedora al codice remoto corretto, genera/verifica il nuovo riepilogo autorevole del full backfill e prova un heartbeat Kuma correlato. Nessun altro deploy/investigazione.

# Starting point autoritativo
- 286419 ha già PASS su Kuma DB/integrity/readiness, monitor push #45 presente, env 0600, lingering/systemd e una run uploader exit 0; il BLOCKED `historical_missing` era un falso positivo di verifica;
- il repo dati remoto contiene già il backfill storico: commit `044344e961bc235189e3d2cfa8a628d6ece9af45` ha aggiunto i dati completi iniziali, inclusi i bucket hostname=`unknown`; una run successiva del timer ha pushato anche `1902816fc0e2a85ce58c0b8862993342d5c2bc48`;
- `hostname="unknown"` NON significa bucket mancante/storico: `aw-stopwatch` e `aw-watcher-web-chrome` sono bucket presenti nell'export corrente;
- codice: `~/projects/activity-watch-uploader`, main, baseline minima `7e7beae16c0e6005e04a23726a3c185f63b8b775`;
- dati: `~/projects/activity-watch-data`, main, baseline minima `9a04d5134b7d9ea3e9628183c585f6f1cc66b22d`;
- il nuovo codice forza un full reconcile se manca `metadata/full-reconcile.json`; il file contiene solo bucket IDs/count/timestamp/hostname/type, non raw payload;
- NON leggere MegaVault/protocollo/schema: tutti i fatti necessari sono qui.

# Esecuzione
1. In UNA shell call fail-fast:
   - richiedi entrambi i repo su `main` e senza dirty path;
   - `git fetch` + `git merge --ff-only origin/main` in entrambi;
   - verifica le due baseline come antenati;
   - esegui SOLO `python3 -m unittest tests.test_activity_watch_uploader -v` e `python3 -m py_compile activity_watch_uploader.py`.
   Al primo failure: `RESULT=BLOCKED` e stop. Non rieseguire i gate già PASS di 286419.
2. Avvia UNA volta `systemctl --user start activity-watch-uploader.service` e attendi bounded la fine. Ricava solo dalla run corrente: `run_id`, mode, changed_files, exit.
3. In UNA verifica aggregata:
   - `metadata/full-reconcile.json` deve esistere e avere `bucket_ids` ESATTAMENTE uguali ai bucket `present_in_activitywatch=true` di `metadata/buckets.json`;
   - deve includere `aw-stopwatch` e `aw-watcher-web-chrome` in `unknown_hostname_bucket_ids`; `aw-stopwatch` può essere in `empty_bucket_ids`;
   - ogni bucket con `event_count>0` deve avere almeno un JSONL nel proprio path; non richiedere JSONL ai bucket con zero eventi;
   - il commit contenente il summary deve essere pushato a `origin/main`;
   - sul DB Kuma, l'ultimo heartbeat del monitor #45 deve essere `up` e il msg deve contenere ESATTAMENTE il `run_id` della run corrente;
   - `activity-watch-uploader.timer` deve restare enabled+active e la service non failed.
4. Se tutto PASS, finalizza UNA volta:
   `python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 424261 --confirm-executed`

# Non-goal / stop
Niente scritture Kuma, token/env, reinstall systemd, full suite, MegaVault discovery, audit generale, secondo run manuale, refactor o cleanup. Dopo PASS stop immediato.

Output massimo 6 righe e prima riga obbligatoria `RESULT=PASS|BLOCKED|FAIL`: `RESULT`, `TESTS`, `RUN`, `FULL_RECONCILE`, `KUMA`, `BLOCKER`.
