PROMPT_ID=773323
/goal
MODEL=GPT-5.6 Terra | REASONING=medium | MEGAVAULT=STANDARD | PROJECT_ID=49
REPO=gernalix/PersonalHub

# Goal
Chiudi e verifica la standardizzazione cross-module PH dei punti 3–8 già in gran parte implementati su current main. NON rifare da zero: usa il codice corrente come verità e correggi solo residui/regressioni.

# Esclusione assoluta
NON TOCCARE tag/facet/shared tag engine né foto/media/thumbnail/shared media engine: sono coperti da altri prompt.

# Scope 3–8
3. Notifications/alarms: core:alerts deve possedere il plumbing Android comune (permission check, channel creation, PendingIntent flags, schedule/cancel/fallback). Places/Timer/Soldi/Sostanze mantengono solo regole di dominio; Timer conserva full-screen/alarm behavior speciale. Non creare un secondo core.
4. Deep links: nessun feature costruisce manualmente personalhub://...; usa solo HubDeepLinkContract (moduleUri, featureUri, permalink versionati). Preserva compatibilità e architecture guard.
5. Search: HubSearchEngine orchestra cross-module; HubEntityAdapter.search() resta provider bounded; HubSearchQuery e HubSavedSearchStore sono i contratti comuni. Verifica modules/kinds/capabilities/lifecycle/ranking/dedup/round-trip. Non toccare Soldi photo/semantic search salvo compile fix.
6. Location: People + Places devono consumare core:location; provider locali canonici + Google Places unici; niente feature→feature dependency o ContentProvider mirror; assenza API key degrada correttamente.
7. Time: migra solo formatter UI equivalenti a HubTimeFormat (locale/timezone/DST/durate comuni). Non centralizzare codec UTC, DB timestamp o serialization.
8. UI: core:ui resta piccolo; centralizza solo primitive realmente duplicate (loading/message/empty/search field). Nessun mega design system o Utils dumping ground.

# Discovery
Prima leggi AGENTS.md, .codex/CODE_MAP.tsv, docs/ARCHITECTURE.md. Cerca solo pattern in-scope: NotificationChannel/Manager, AlarmManager, PendingIntent, personalhub://, DateTimeFormatter, AddressSuggestion/Google Places, shared search/saved-search, loading/error/search-field. Niente audit repo-wide.

# Autonomia
Correggi direttamente compile/lint/test stale, wiring Gradle, architecture violations, API mismatch e call-site residui in-scope. Se un test copre codice intenzionalmente rimosso, verifica Git history e aggiorna/rimuovi il test invece di reintrodurre codice zombie. Non aprire follow-up per failure tecnici correggibili.

# Verification
Esegui prima gate mirati: checkArchitectureBoundaries; test core:alerts pertinenti; core:hub-context search; core:location; core:ui time/DST; deep-link contract; compile consumer modificati.
Poi usa CI esistente: Architecture boundaries, Android unit CI, Play Store preflight, Android instrumentation CI.
Per failure billing/runner/network/dependency resolution: distingui infra da codice, non alterare codice per curare infra, retry massimo una volta con evidenza transient, usa test locale equivalente se disponibile. Preserva dati reali; niente destructive device test.

# Acceptance
PASS solo se:
- punti 1–2 restano intatti;
- plumbing notification/alarm comune non è duplicato;
- nessun feature costruisce manualmente URI PH;
- shared search + saved query funzionano;
- People/Places usano shared location engine senza feature dependency;
- formatter UI equivalenti convergono su HubTimeFormat;
- core:ui resta piccolo;
- CODE_MAP/ARCHITECTURE sono coerenti;
- architecture + test mirati PASS;
- nessuna regressione osservata;
- CI finale PASS, oppure ogni residuo non-PASS è provato puro blocker infrastrutturale indipendente dal codice con verifica locale equivalente PASS.

# Roadmap
Prima azione:
python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 773323
Procedi solo se lo stato diventa running.

Al PASS:
python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 773323 --confirm-executed
Per BLOCKED/FAIL usa roadmap_result.py con lo stesso PROMPT_ID.
Dopo PASS: STOP.

Output max 12 righe: PROMPT_ID, RESULT, HEAD, NOTIFICATIONS, DEEP_LINKS, SEARCH, LOCATION, TIME, UI, ARCHITECTURE, TESTS, BLOCKER.