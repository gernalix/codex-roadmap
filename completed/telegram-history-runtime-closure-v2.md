PROMPT_ID=966124

# Goal
Chiudi SOLO il residuo di PROMPT_ID 422308 dopo l'autorizzazione Telegram già completata: integra su main i fix già verificati del collector, conferma il runtime Fedora già funzionante e termina senza rifare l'implementazione.

# Evidenza già verificata
- 422308 è terminale BLOCKED storico; non riaprirlo.
- fedora-system-monitor task/422308 contiene i fix del collector già verificati e pushati, incluso commit 5d8ed32.
- Runtime reale già verificato:
  - sessione Telegram autorizzata;
  - target corretto = datasette_alerts_bot;
  - RUN1 PASS: 4244 messaggi, commit dati 99a9952479074f56095586a6ed3fb210111496db;
  - RUN2 PASS: new_messages=0 e remoto invariato;
  - telegram-notification-history.timer enabled+active, cadenza 15 minuti;
  - gernalix/telegram-notification-history verificato PRIVATE e leggibile dal connettore GitHub.
- Non leggere/stampare API ID/hash, session file, OTP, 2FA o bot token.

# Esecuzione minima
1. Claim 966124 con roadmap_start.py e usa il worktree restituito.
2. Porta nel nuovo task SOLO il diff funzionale di task/422308 rispetto a main, preservando main corrente. Preferisci cherry-pick dei commit del branch 422308 o equivalente minimo; nessun refactor.
3. Assicurati che siano inclusi:
   - login che chiama client.start() se TELEGRAM_PHONE è vuoto;
   - fallback peer via dialogs/real channel id;
   - verifica permessi config senza chmod runtime sotto ProtectHome=read-only;
   - log errore locale utile;
   - test del fallback peer.
4. Esegui solo:
   - python3 -m unittest tests.test_telegram_history_collector -v
   - python3 -m py_compile scripts/telegram_history_collector.py
   - git diff --check
5. Readback runtime una sola volta:
   - timer enabled+active;
   - ultimo service success;
   - data repo main pulito e origin/main contiene 99a9952479074f56095586a6ed3fb210111496db o successore;
   - non inviare notifiche Telegram di test.
6. Finalizza PASS con roadmap_finish.py e STOP. Non aspettare CI/integratore.

# Acceptance
PASS se il codice del collector è integrabile dal nuovo task senza perdere i fix live, i test PASS, il runtime resta sano, il timer è attivo e il repo dati privato è aggiornato.

# Report
Massimo 7 righe: RESULT, SOURCE_422308, TESTS, RUNTIME, TIMER, DATA_REPO, BLOCKER.