PROMPT_ID=684215 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STRICT

# Goal
Valida e chiudi SOLO l'implementazione già presente sul branch remoto PersonalHub `feature/shared-alerts-place-tags`: tag Places indipendenti dai tag Timer, Alert Engine condiviso Timer/Places, alert Places su check-in/check-out manuali per luogo o set di tag, tap diretto dei link-only e bridge Tasker opzionale. Dopo tutti i gate PASS, integra il branch in `main` e cancellalo: `main` deve tornare a essere l'unico branch persistente di questo lavoro.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`, project_id=49;
- inizio lavoro sul branch temporaneo `feature/shared-alerts-place-tags`; a fine task il branch DEVE essere mergiato in `main` e rimosso sia remoto sia locale;
- regola canonica PH: i branch non-`main` servono solo per isolamento temporaneo; appena il lavoro è verificato vanno integrati in `main` e cancellati;
- il branch remoto contiene già `:core:alerts`, `PlaceTagEntity`, `PlaceAlertEngine`, `PlaceAlertRepository`, UI Places Alerts, migration Room 15→16, `docs/ALERTS.md` e test mirati;
- baseline feature minima: `df76297e057cd5b8afd8cf2aaa46d231a33a9f41`;
- dopo la creazione del branch, PROMPT_ID=918274 ha completato il lavoro Profili su `main` con commit `73f0ed47f20fa06ba8302396153ba09cefd18e79`; quel commit va prima integrato **da main verso il branch feature**, senza perdere né resuscitare codice Timer rimosso dal lavoro Profili;
- schema target della feature: `PersonalHubDatabase.SCHEMA_VERSION=16`; `version.txt` NON va incrementato;
- usa prima `.codex/CODE_MAP.tsv` e `docs/ALERTS.md`; niente inventory/audit generale del repository;
- Timer e Places condividono l'evaluator, NON i tag e NON necessariamente la persistenza: Timer conserva le regole nello snapshot esistente; Places usa `place_tags` + `place_tag_cross_ref` e `alert_rules` + `alert_place_tag_targets`;
- gli alert Places devono dipendere SOLO da check-in/out espliciti/manuali. Il sottosistema Android Geofence esistente NON deve attivarli.

# Esecuzione minima
1. Acquisisci il lock PH con PROMPT_ID 684215. Fai un solo fetch iniziale mirato. Porta il checkout sul branch `feature/shared-alerts-place-tags` e fast-forward da `origin/feature/shared-alerts-place-tags`. Fissa `MAIN_BASE=origin/main`. Integra `origin/main` **nel branch feature**. Il merge remoto è già risultato conflittuale: gli overlap noti sono `.codex/CODE_MAP.tsv`, `core/database/.../PersonalHubDatabase.kt`, `feature/luoghi/build.gradle.kts`, `feature/multitimetracker/.../TimeFenceNotifier.kt`, `feature/multitimetracker/.../AlertsCapsuleViewModel.kt`. Risolvi solo i conflitti reali preservando entrambe le intenzioni: hardening Profili/de-promozione Timer da `main` + shared alerts/tag Places dal branch. Non ripristinare file Timer eliminati da `main`; riapplica la minima integrazione alert ai consumer ancora esistenti. Dirty non sovrapposto non blocca; niente stash/reset.
2. Preflight economico, in batch:
   - conferma branch, entrambe le baseline (`df76297…` feature e `73f0ed47…` main) antenate di RUN_HEAD, `SCHEMA_VERSION=16`, `:core:alerts` incluso in settings e dipendenze Timer/Places;
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
9. Quando host, migration e AVD sono tutti PASS, prepara la chiusura del branch:
   - commit/push sul branch feature degli eventuali schema/test/fix prodotti dal task;
   - fai UN solo fetch finale di `origin/main` per evitare una race prima del merge;
   - se `origin/main` è avanzato rispetto a `MAIN_BASE`, integralo nuovamente **nel branch feature**. Se non ci sono conflitti, riesegui solo i gate direttamente toccati dal nuovo diff; se compaiono conflitti, risolvili solo se sono chiaramente nello scope della feature e poi riesegui i gate pertinenti. Se l'integrazione diventa ambigua o richiede refactor fuori scope => BLOCKED, senza toccare `main`;
   - push del branch feature aggiornato;
   - passa a `main`, fast-forward a `origin/main`, quindi integra `feature/shared-alerts-place-tags` in `main` con fast-forward quando possibile; se il branch contiene l'ultimo `origin/main`, il merge deve essere lineare/fail-closed;
   - push `main`; solo dopo push riuscito elimina `origin/feature/shared-alerts-place-tags` e poi il branch locale;
   - non creare un branch sostitutivo.
10. Verifica finale minima: HEAD locale è `main`, `origin/main` contiene il commit finale della feature e `feature/shared-alerts-place-tags` non esiste più né localmente né su origin. `version.txt` invariato. Rilascia lock.
11. Solo ora dichiara PASS ed esegui il finalizzatore roadmap. Nessun audit successivo.

# Acceptance
PASS solo se: schema Room 16 è esportato e migration v15→v16 è lossless/FK-safe; host tests/compile/architecture gate PASS; Timer e Places condividono l'evaluator ma non i tag; alert Places per luogo/tags e check-in/out/both funzionano solo sugli eventi manuali; direct-tap link-only e Tasker bridge rispettano il contratto; QA AVD PASS; il risultato verificato è in `main`; `feature/shared-alerts-place-tags` è stato eliminato remoto+locale; `version.txt` non è stato incrementato.

# Non-goal
Migrazione delle regole Timer nelle tabelle Places/canoniche, background GPS, sostituzione del geofencing Android, redesign generale, refactor/cleanup fuori scope, release, installazione su device reali, Telegram/APK delivery, gestione di branch non correlati a questa feature.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 684215 --confirm-executed`

Output massimo 8 righe: RESULT, MAIN_HEAD, SCHEMA16, HOST_TESTS, MIGRATION, ALERT_CONTRACT, AVD_QA, BRANCH_CLEANUP.
