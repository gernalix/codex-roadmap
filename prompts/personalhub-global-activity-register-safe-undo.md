[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=835204 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Creare un unico `Registro attività` app-wide: audit semantico append-only, lettura paginata, undo compensativo sicuro e UI Home/history sopra LO STESSO modello. Un solo bump/versione e un solo QA finale.

# Stato da riusare
Non esiste ancora un journal globale. Timer ha `TimerAuditEvents`/`AuditLogSqlite`; Places ha `HistoryAuditLogEntity/HistoryActionEntity`. Riusa/bridge questi meccanismi senza doppio logging; non ridisegnarli prima di vedere il boundary necessario.

# Implementazione
1. Aggiungi il minimo persistence/read model globale con ID/timestamp, module/action, stable entity identity + label snapshot, origin, payload before/after versionato necessario all'undo, group relation, reversibility/status, app/payload version. Niente secrets o blob grandi.
2. Cattura mutazioni semantiche ai repository/domain boundary autorevoli (People, Timer, Places, Substances, WordPulse, Soldi, settings), non trigger SQLite. Audit+mutation atomici dove possibile; escludi bookkeeping e recursion.
3. Read API bounded/paged direttamente utilizzabile dalla UI.
4. Undo = nuova mutazione autorevole + nuovo audit collegato, mai history rewrite. Prima dell'inversione verifica current state contro after-state/version/hash; stale/FK/dependency => fail closed. Usa comandi domain, group undo all-or-nothing dove possibile, retry/double undo idempotente; system/non-reversible resta immutabile.
5. Home → `Registro attività`: lista lazy/paged, descrizioni umane, group detail, stato reverted/conflict/non-reversible, undo solo se valido. Filtri persistiti: Tutti + moduli + Impostazioni/Sistema; future category visibili di default.

# Scope discipline
Una sola inventory dei write boundary indicati; segui solo collaborator diretti. Usa la Room/migration infrastructure corrente senza costruire un secondo framework: il task database-safety successivo consoliderà e testerà l'intera catena finale. Non fare event-sourcing, generic row replay, analytics, Datasette/SAF redesign.

# Verification
Representative coverage, non combinatoria: almeno un evento semantico per ogni modulo/settings; deleted identity leggibile e secret redaction; Timer/Places no double log; INSERT/UPDATE/DELETE/settings undo; stale/dependency/group/double/non-reversible; paging/filter persistence/future category. Una QA disposable: Home→registro→filter→group→azione reversibile→undo/compensating event. Una sola build/install/delivery finale.

PASS solo con un modello canonico per capture+undo+UI, nessuna recursion/export storm e test/QA PASS. Commit/push, roadmap, STOP.

Output: `PROMPT_ID`, `RESULT`, schema/coverage, Timer/Places bridge, undo/conflicts, paging/filters, no-recursion checks, test/QA, version/APK/delivery, SHA, blocker.
