PROMPT_ID=181259

# Goal
Riprendi e completa SOLO il lavoro residuo di 354882 dopo che il login Grindr manuale è stato realmente completato, senza tenere Codex in attesa e senza ricreare il vecchio loop login.

# Stato già verificato
- 354882 è terminato BLOCKED perché il 2026-09-22 esisteva evidenza positiva di route /login e serviva un login manuale.
- Il vecchio task richiedeva erroneamente di mantenere il modello RUNNING durante l'attesa; la policy corrente vieta model-driven waiting.
- Repo canonico: /home/daniele/projects/grindr-web-exporter.
- Obiettivo tecnico da preservare: un solo Chrome dedicato/supervisor end-to-end, auth tri-state, UNKNOWN != UNAUTHENTICATED, discovery sidebar/scroll convergente, smoke top->bottom su una chat lunga, cleanup bounded senza orphan/lock.
- Non rifare login, profilo o discovery generale se lo stato corrente dimostra che sono già corretti.

# Esecuzione minima
1. Questo task è eseguibile solo dopo che il prerequisito manuale grindr-login è stato rimosso dalla roadmap. Se Grindr mostra ancora login reale, BLOCKED immediato e STOP: non aspettare, non creare heartbeat e non chiedere un secondo login nella stessa esecuzione.
2. Claim 181259 e usa il worktree assegnato.
3. Parti dal current main e dai test/codice del browser lifecycle, auth e discovery già toccati dalla catena 354882. Niente audit repo-wide.
4. Avvia/riusa una sola istanza Chrome dedicata col profilo canonico; non toccare Chrome predefinito. Prima di chiudere/riavviare un processo dedicato visibile, notify-send.
5. Verifica auth tri-state. AUTHENTICATED => continua. UNKNOWN => diagnostica solo il failure tecnico. UNAUTHENTICATED => BLOCKED e STOP, senza model waiting.
6. Completa/fixa solo ciò che resta per discovery finita e smoke reale su una chat lunga top->bottom con overlap/dedup/checkpoint. Discovery failure non deve mai diventare richiesta login.
7. Esegui test mirati e una sola conferma aggregata. Nessun refactor, T7, MegaVault history, dashboard o nuovo repo.
8. Dopo PASS finalizza e STOP; non attendere CI/merge in modello.

# Acceptance
PASS solo se il normale export usa un unico lifecycle browser, auth non produce falsi logout, discovery termina, una chat lunga completa top->bottom, test PASS e non restano processi/lock task-owned orfani.

# Report
Massimo 8 righe: RESULT, COMMIT, BROWSER_LIFECYCLE, AUTH_STATE, DISCOVERY, LONG_CHAT_SMOKE, TESTS, BLOCKER.