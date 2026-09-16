[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=467281 | project_id=15 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Diagnostica e correggi SOLO il monitor Uptime Kuma Push **“Fedora Software” (#43)**, attualmente giallo/**In attesa**. Determina la causa reale e ripristina un monitoraggio corretto con il minimo cambiamento necessario. Non forzare lo stato verde se esiste un problema reale.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/fedora-system-monitor`;
- MegaVault: progetto `15`, già esistente; non crearne duplicati;
- DB runtime canonico già noto: `/var/lib/fedora-system-monitor/monitor.sqlite3`;
- screenshot utente del 2026-09-16 03:36 mostra `kuma.danielegalati.com/dashboard/43`, monitor “Fedora Software”, stato **In attesa**, ping `N/D`, intervallo Kuma `5400 s (1 h 30 min)`;
- descrizione monitor: `Fedora software health: package transactions, pending updates and inventory changes.`;
- ultimo heartbeat verde visibile nello screenshot: `2026-09-15 13:00:26`, messaggio `software: collectors complete; active alerts=0`;
- gli altri monitor Fedora continuano a produrre heartbeat; il toast `[Fedora Host] [DOWN] system: collectors complete; active alerts=1` visibile nello screenshot può essere un evento separato: non confonderlo con la causa del monitor Software senza evidenza.

# Esecuzione minima
1. Fai una sola fotografia Git del repo e usa MegaVault FAST solo per i riferimenti già pertinenti. Niente audit generale del repository o del sistema.
2. Trova direttamente il codice/config/unit/timer che genera il Push `Fedora Software` cercando solo riferimenti pertinenti (`software`, Kuma push, monitor #43, scheduler/interval). Non esplorare gli altri collector salvo confronto minimo indispensabile.
3. Determina prima la semantica del giallo:
   - ultimo heartbeat ricevuto e sua età;
   - intervallo/grace/timeout attesi dal monitor #43;
   - se `In attesa` deriva da heartbeat mancante/scaduto oppure da uno status esplicitamente inviato.
4. Sul Fedora locale controlla SOLO il runner pertinente:
   - stato unit/timer/processo;
   - ultimo run e prossimo run;
   - exit status;
   - ultimi log pertinenti al software collector/push;
   - ultimo payload/status/message inviato a Kuma.
   Limita `journalctl` all'unit e alla finestra temporale necessaria.
5. Confronta una sola volta con un monitor Fedora funzionante soltanto se serve a distinguere problema comune vs specifico del collector Software.
6. Esegui UNA volta manualmente lo stesso check Software, in modalità sicura/non distruttiva, e osserva exit code + payload risultante. Non fare update/install/remove di pacchetti per provocare artificialmente eventi.
7. Identifica la root cause concreta, ad esempio solo se confermata: timer non attivo, schedule errato, collector bloccato/fallito, eccezione che salta il Push, intervallo locale incoerente con 5400 s Kuma, URL/token/config obsoleti, networking, timeout o logica status errata.
8. Applica SOLO il fix minimo nel boundary corretto. Se serve modificare Kuma/VM, fallo solo dopo evidenza che la causa è nella configurazione del monitor #43; non toccare gli altri monitor e non stampare Push URL/token/segreti.
9. Se il giallo è corretto perché il monitor è configurato per attendere un heartbeat che il job invia intenzionalmente più di rado, correggi l'incoerenza di scheduling/heartbeat senza indebolire il rilevamento di failure reali.

# Verifica
- test mirati solo sui file modificati;
- esegui una sola run del check Software dopo il fix;
- verifica che il Push venga ricevuto da #43 con stato/messaggio coerente;
- verifica che il prossimo run sia schedulato correttamente rispetto all'intervallo Kuma;
- PASS se #43 torna **UP/Operativo** quando non esistono alert reali, oppure resta non-UP con una causa reale e diagnostica corretta;
- verifica solo che gli altri monitor Fedora non siano stati alterati.

# Non-goal
Niente audit generale Fedora, aggiornamenti di sistema/pacchetti, refactor/cleanup, tuning degli altri monitor, analisi del toast Fedora Host se non blocca direttamente il Software Push, o modifiche cosmetiche a Kuma.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 467281 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 467281`

`push_verified=git_push_exit_0` è terminale. Output massimo 6 righe: RESULT, ROOT_CAUSE, FIX, KUMA_NOW, TEST, CHANGES/BLOCKER.