PROMPT_ID=842617 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STRICT

# Goal
Valida e chiudi SOLO l'implementazione già presente sul branch remoto PersonalHub `feature/shared-alerts-place-tags`: tag Places indipendenti dai tag Timer, Alert Engine condiviso Timer/Places, alert Places su check-in/check-out manuali per luogo o set di tag, tap diretto dei link-only e bridge Tasker opzionale. Correggi soltanto failure direttamente causati da questa feature.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`, project_id=49;
- branch obbligatorio: `feature/shared-alerts-place-tags`;
- **eccezione esplicita alla regola PH sui branch temporanei:** questo branch DEVE restare remoto e separato da `main` a fine task perché Daniele lo mergerà manualmente più avanti. NON merge/rebase su `main`, NON eliminare il branch;
- il branch remoto contiene già `:core:alerts`, `PlaceTagEntity`, `PlaceAlertEngine`, `PlaceAlertRepository`, UI Places Alerts, migration Room 15→16, `docs/ALERTS.md` e test mirati;
- baseline minima: il commit `df76297e057cd5b8afd8cf2aaa46d231a33a9f41` deve essere antenato di RUN_HEAD;
- schema atteso: `PersonalHubDatabase.SCHEMA_VERSION=16`; `version.txt` NON va incrementato;
- usa prima `.codex/CODE_MAP.tsv` e `docs/ALERTS.md`; niente inventory/audit generale del repository;
- Timer e Places condividono l'evaluator, NON i tag e NON necessariamente la persistenza: Timer conserva le regole nello snapshot esistente; Places usa `place_tags` + `place_tag_cross_ref` e `alert_rules` + `alert_place_tag_targets`;
- gli alert Places devono dipendere SOLO da check-in/out espliciti/manuali. Il sottosistema Android Geofence esistente NON deve attivarli.

# Esecuzione minima
1. Acquisisci il lock PH con PROMPT_ID 842617. Fai un solo fetch mirato. Porta il checkout sul branch `feature/shared-alerts-place-tags` e fast-forward SOLO da `origin/feature/shared-alerts-place-tags`. Non integrare `main`. Dirty non sovrapposto non blocca; niente stash/reset.
2. Preflight economico, in batch:
   - conferma branch, baseline antenata, `SCHEMA_VERSION=16`, `:core:alerts` incluso in settings e dipendenze Timer/Places;
   - esegui `python3 tools/check_architecture_boundaries.py`;
   - cerca SOLO nei file toccati riferimenti zombie a `alert_timer_tag_targets` / `AlertTimerTagTargetEntity` e sequenze `\\n` letterali introdotte accidentalmente nei file Gradle. Devono essere assenti.
3. Genera lo schema Room corrente con il task KSP/compile più piccolo adeguato. Se manca o cambia `core/database/schemas/com.gernalix.personalhub.core.database.PersonalHubDatabase/16.json`, aggiungilo al branch. Non modificare schema/versione oltre 16.
4. Esegui test host mirati, prima i più economici:
   - `:core:alerts:testDebugUnitTest`;
   - test Timer pertinenti a alert/matching/link notification, non l'intera suite se non serve;
   - test Places pertinenti a check-in/out e UI/model alert;
   - `:core:database:testDebugUnitTest` limitando il loop ai migration test pertinenti se il runner lo permette;
   - compile dei moduli `:core:alerts`, `:feature:luoghi`, `:feature:multitimetracker` e infine `:app`.
   Se un task aggregato fallisce, leggi una volta il report, correggi in batch e rilancia il leaf fallito; un solo gate aggregato finale.
5. Dimostra con test automatici mirati, aggiungendoli SOLO se manca copertura:
   - `TimerTag` e `PlaceTag` restano namespace separati: stesso ID numerico non cross-matcha;
   - Places tag ALL/ANY funziona;
   - target luogo richiede UUID esatto;
   - `PLACE_CHECK_IN`, `PLACE_CHECK_OUT`, `PLACE_BOTH` funzionano;
   - one-time si disabilita dopo firing; cooldown impedisce duplicati;
   - check-in/out storico retroattivo non genera alert;
   - `PlaceGeofenceReceiver`/ENTER/EXIT del geofence Android non genera alert manuali;
   - link-only accetta soltanto `http`, `https`, `workflowy`; testo+link e `intent:`/`file:`/`content:` non prendono il direct-tap path;
   - Workflowy usa `com.workflowy.android` quando risolvibile e fallback sicuro quando non lo è;
   - bridge Tasker è esplicitamente scoped a `net.dinglisch.android.taskerm` e include rule_id/domain/trigger/entity_id/tag_ids/tags/title/message/fired_at_ms.
6. Migration gate v15→v16 su COPIA sintetica/fixture, mai sul DB personale:
   - dati v15 rappresentativi dei moduli esistenti restano invariati;
   - vengono create `place_tags`, `place_tag_cross_ref`, `alert_rules`, `alert_place_tag_targets`;
   - `PRAGMA quick_check` e `PRAGMA foreign_key_check` PASS;
   - crea due Places tags e relative associazioni/alert, chiudi e riapri DB, verifica persistenza/FK;
   - nessuna destructive migration/fallback.
7. Solo dopo host PASS, QA sull'AVD canonico `Pixel_8a`/package isolato QA; NON usare Pixel/TCL reali:
   - grant POST_NOTIFICATIONS al package QA se necessario;
   - crea due luoghi sintetici con tag sovrapposti, es. `Lidl` + `groceries` e `Netto` + `groceries`;
   - alert specifico per un luogo + alert `groceries`; verifica check-in manuale;
   - verifica check-out e un alert `PLACE_BOTH`;
   - verifica one-time;
   - verifica che una transizione della feature Geofence non produca questi alert manuali;
   - alert con solo `https://example.com`: il tap deve uscire direttamente verso il relativo handler, senza schermata/conferma PH intermedia;
   - mixed text+URL resta comportamento PH normale; unsafe scheme non auto-apre;
   - Workflowy: se l'app non è già installata sull'AVD, NON installarla solo per questo test; considera sufficiente il test host del routing esplicito + fallback.
8. Non configurare Tasker sull'AVD e non renderlo prerequisito. Il bridge è PASS con i test host del package esplicito/extras; Tasker deve restare opzionale.
9. Dopo tutti i PASS, aggiorna soltanto schema 16/test/fix strettamente necessari e CODE_MAP/docs solo se il codice reale li ha resi falsi. Commit/push **solo** `feature/shared-alerts-place-tags`. `version.txt` invariato. NON mergeare in `main`, NON eliminare il branch.
10. Rilascia lock. PASS => stop immediato; niente audit successivo.

# Acceptance
PASS solo se: schema Room 16 è esportato e migration v15→16 è lossless/FK-safe; host tests/compile/architecture gate PASS; Timer e Places condividono l'evaluator ma non i tag; alert Places per luogo/tags e check-in/out/both funzionano solo sugli eventi manuali; direct-tap link-only e Tasker bridge rispettano il contratto; QA AVD PASS; branch remoto resta `feature/shared-alerts-place-tags`; `main` e `version.txt` non sono modificati.

# Non-goal
Merge/rebase di `main`, migrazione delle regole Timer nelle tabelle Places/canoniche, background GPS, sostituzione del geofencing Android, redesign generale, refactor/cleanup fuori scope, release, installazione su device reali, Telegram/APK delivery.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 842617 --confirm-executed`

Output massimo 8 righe: RESULT, HEAD, SCHEMA16, HOST_TESTS, MIGRATION, ALERT_CONTRACT, AVD_QA, BRANCH_STATUS.
