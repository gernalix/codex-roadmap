[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=835204 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Creare un unico `Registro attività` app-wide: audit semantico append-only, lettura paginata, undo compensativo sicuro e UI Home/history sopra LO STESSO modello. Un solo bump/versione e un solo QA finale.

# Stato già verificato — NON fare inventory generale
Non esiste ancora un journal globale. Timer e Places hanno già audit locali da riusare/bridgiare senza doppio logging.

## Audit esistente Timer
Parti direttamente da:
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/AuditLogSqlite.kt`;
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/model/AuditModels.kt`;
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/util/CapsuleAudit.kt`;
- `feature/multitimetracker/src/main/java/com/example/multitimetracker/util/CapsuleWriteApi.kt`;
- UI/access già esistenti: `capsules/auditlog/controller/AuditLogCapsuleViewModel.kt`, `capsules/auditlog/ui/AuditLogCapsuleUi.kt`, `capsules/auditlog/ui/AuditLogScreen.kt`, `capsules/system/AuditLogCapsuleAccess.kt`.

Non ridisegnare o censire tutto Timer: usa questi file per capire il bridge minimo e apri un write boundary Timer aggiuntivo solo se una mutazione rappresentativa non passa già da essi.

## Audit esistente Places
Le entity sono già localizzate in:
`contracts/database/src/main/java/com/gernalix/luoghi/data/PlaceEntities.kt`

Qui esistono già `HistoryAuditLogEntity` (`history_audit_log`, before/after JSON, action/entity/session/timestamp) e `HistoryActionEntity` (`history_actions`, action UUID/type, before/after, status). Il boundary operativo principale è:
- `feature/luoghi/src/main/java/com/gernalix/luoghi/data/PlaceRepository.kt`;
- check-in/visite: `feature/luoghi/src/main/java/com/gernalix/luoghi/capsules/checkin/CheckInCapsule.kt`.

Riusa/bridge queste strutture; non creare un secondo audit Places e non cercare altre tabelle history salvo una failure concreta.

## Write boundary autorevoli già localizzati
Per il primo pass apri **solo** questi file oltre al nuovo core globale che creerai:
- People: `feature/supercontacts/src/main/java/com/supercontacts/app/data/repository/ContactsRepository.kt`;
- Timer: i file audit sopra + `feature/multitimetracker/src/main/java/com/example/multitimetracker/persistence/SessionRepository.kt` e, per quick events, `core/quickevent/QuickEventExecution.kt` / `persistence/QuickEventRepository.kt` solo se necessari;
- Places: `PlaceRepository.kt` + `CheckInCapsule.kt` sopra;
- Substances: `feature/sostanze/src/main/java/com/gernalix/sostanze/data/SostanzeRepository.kt`;
- WordPulse: `feature/wordpulse/src/main/java/com/wordpulse/app/data/WordRepository.kt`;
- Soldi: `feature/soldi/src/main/java/com/gernalix/personalhub/core/database/capsules/soldi/FinanceCapsule.kt`;
- settings: `app/src/main/java/com/gernalix/personalhub/capsules/settings/HubSettings.kt`.

Non leggere interi moduli. Amplia da uno di questi file soltanto verso un collaborator diretto richiesto da compile/test o da una mutazione rappresentativa che non può essere catturata lì.

# Implementazione
1. Aggiungi il minimo persistence/read model globale con ID/timestamp, module/action, stable entity identity + label snapshot, origin, payload before/after versionato necessario all'undo, group relation, reversibility/status, app/payload version. Niente secrets o blob grandi.
2. Cattura mutazioni semantiche ai repository/domain boundary autorevoli sopra, non trigger SQLite. Audit+mutation atomici dove possibile; escludi bookkeeping e recursion.
3. Read API bounded/paged direttamente utilizzabile dalla UI.
4. Undo = nuova mutazione autorevole + nuovo audit collegato, mai history rewrite. Prima dell'inversione verifica current state contro after-state/version/hash; stale/FK/dependency => fail closed. Usa comandi domain, group undo all-or-nothing dove possibile, retry/double undo idempotente; system/non-reversible resta immutabile.
5. Home → `Registro attività`: lista lazy/paged, descrizioni umane, group detail, stato reverted/conflict/non-reversible, undo solo se valido. Filtri persistiti: Tutti + moduli + Impostazioni/Sistema; future category visibili di default.

# Scope discipline
L'inventory iniziale è già fatta sopra: **non ripeterla**. Usa la Room/migration infrastructure corrente senza costruire un secondo framework: il task database-safety successivo consoliderà e testerà l'intera catena finale. Non fare event-sourcing, generic row replay, analytics, Datasette/SAF redesign. Se scopri un write path secondario non coperto, aggiungilo solo se serve agli acceptance criteria; segnala gli altri senza investigarli.

# Verification
Representative coverage, non combinatoria: almeno un evento semantico per ogni modulo/settings; deleted identity leggibile e secret redaction; Timer/Places no double log; INSERT/UPDATE/DELETE/settings undo; stale/dependency/group/double/non-reversible; paging/filter persistence/future category. Una QA disposable: Home→registro→filter→group→azione reversibile→undo/compensating event. Una sola build/install/delivery finale.

PASS solo con un modello canonico per capture+undo+UI, nessuna recursion/export storm e test/QA PASS. Commit/push, roadmap, STOP.

Output: `PROMPT_ID`, `RESULT`, schema/coverage, Timer/Places bridge, undo/conflicts, paging/filters, no-recursion checks, test/QA, version/APK/delivery, SHA, blocker.
