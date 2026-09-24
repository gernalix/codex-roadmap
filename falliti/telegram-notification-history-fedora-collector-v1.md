PROMPT_ID=422308

# Goal
Crea sul Fedora un collector unattended della sola chat Telegram usata per le notifiche tecniche, con archivio Git privato leggibile successivamente da ChatGPT. Questa fase costruisce SOLO la raccolta affidabile: non riscrivere ancora i producer Telegram.

# Starting point verificato
- Baseline storica: PROMPT_ID 417826 ha già fatto una prima signal-hygiene, ma l'utente continua a ricevere notifiche verbose, incomprensibili, inutili o ripetitive.
- Il collector deve restare separato da `telegram_insert_bot`.
- Il codice/runtime Fedora può vivere in `gernalix/fedora-system-monitor`; i messaggi reali devono stare in un repo dati PRIVATO dedicato.
- La Bot API non è una fonte generale affidabile della cronologia dei messaggi già inviati dal bot: usa un client Telegram account-level supportato (preferibilmente Telethon) limitato alla singola chat target.
- Nessun token/session/API hash/chat secret deve finire in Git, log o output.

# Scope
1. Claim 422308 con `roadmap_start.py` e usa il worktree restituito per `gernalix/fedora-system-monitor`.
2. Leggi solo AGENTS/config/systemd già pertinenti; niente audit repo-wide.
3. Implementa un exporter incrementale della SOLA chat target:
   - configurazione esplicita del peer/chat;
   - conserva almeno message_id, data UTC, testo/caption e metadata minimi utili a distinguere media/documenti;
   - non scaricare media binari;
   - stato resumable; restart non duplica messaggi;
   - ordine stabile;
   - una seconda run senza nuovi messaggi è un vero no-op.
4. Credenziali/sessione Telegram:
   - env/config locale mode 600 fuori dal repo;
   - session file fuori dal repo;
   - example config senza valori reali;
   - comando di login/bootstrap esplicito e separato dal timer;
   - il servizio periodico NON deve mai chiedere input interattivo.
5. Crea, se non esiste, `gernalix/telegram-notification-history` come repo PRIVATO e usalo solo come data sink.
   - Nessun secret.
   - Archivio testuale diff-friendly, preferibilmente JSONL mensile + una vista `latest.md` limitata agli ultimi messaggi per audit umano/ChatGPT.
   - README/schema minimo che descriva i campi.
   - Un solo writer runtime: il sync Fedora.
6. Aggiungi nel repo codice service+timer `systemd --user`:
   - oneshot;
   - timer ogni 15 minuti, Persistent=true;
   - `flock`/lock equivalente contro overlap;
   - fetch/pull sicuro del data repo prima della scrittura;
   - commit+push SOLO se l'archivio cambia;
   - nessun commit vuoto e nessun push su run no-op.
7. Non usare un processo model-driven always-on e non inviare Telegram per dire che il collector Telegram ha girato.
8. Test mirati con fake client/fixture:
   - prima ingestione;
   - seconda ingestione identica => zero duplicati/zero commit;
   - nuovi messaggi => solo delta;
   - chat non target ignorata;
   - configurazione/segreti non serializzati;
   - errore rete/Git non avanza lo state come se fosse successo.
9. Gate minimo: test mirati + py_compile + unit syntax/verifica systemd pertinente.
10. Runtime:
   - se una sessione Telegram già valida è disponibile, completa due run reali consecutive e verifica il remoto Git;
   - se serve login/2FA, NON aspettare/pollare: installa tutto ciò che non richiede il segreto, lascia il timer disabilitato finché la sessione non esiste, termina BLOCKED con UNA sola azione manuale esatta per il login. Il follow-up dovrà riprendere da lì senza rifare implementazione/test già PASS.
11. Non modificare in questa fase i producer delle notifiche, i loro trigger, la vecchia policy project_id o le soglie quota/spazio disco. L'archivio servirà come evidenza per un audit successivo.

# Acceptance
PASS solo se:
- il collector legge esclusivamente la chat configurata;
- l'archivio privato remoto contiene i messaggi senza duplicati;
- nessun secret è versionato;
- timer/service sono installati, enabled+active e non interattivi;
- run #1 con nuovi dati pubblica un commit; run #2 senza nuovi dati è no-op;
- crash/rete/Git failure non perdono né duplicano stato;
- il data repo è privato e aggiornato.

Se il solo blocker rimasto è l'autorizzazione Telegram iniziale, BLOCKED è corretto dopo aver persistito codice+config+unit testati; non mantenere la sessione Codex viva in attesa.

# Report finale
Massimo 9 righe:
PROMPT_ID
RESULT
CODE_REPO
DATA_REPO
TELEGRAM_SCOPE
SYSTEMD
RUN1
RUN2
BLOCKER