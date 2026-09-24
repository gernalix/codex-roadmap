PROMPT_ID=354882 | PARENT_PROMPT_ID=515955 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST
WORKDIR=/home/daniele/projects/grindr-web-exporter

# Goal
Elimina definitivamente il loop di login e COMPLETA il goal originale con un unico lifecycle browser end-to-end: una sola istanza Chrome dedicata, stesso profilo, stesso processo dall'eventuale login fino a discovery e scraping. Un failure di discovery/DOM/CDP NON deve mai essere reinterpretato come "rifai login".

# Evidenza autoritativa
- Il profilo dedicato è già stato autenticato più volte: screenshot/UI hanno dimostrato che Grindr risultava loggato anche quando il detector dichiarava `unauthenticated`.
- Il vecchio detector era falso-negativo: cercava `ChatSidebar` anche quando `setup-browser` apriva Nearby/home.
- Il lifecycle setup -> chiudi Chrome -> riapri per export ha causato processi orfani, `SingletonLock` stale e falsi logout.
- Dopo il fix del detector, la discovery ha raggiunto il vero failure successivo: sidebar/scroll che non convergeva. Questo è un bug di scraping, NON autenticazione.
- Commit storico noto: `e21285b`; successivamente è stato aggiunto anche il fix "exit dedicated setup Chrome with its last window". PARTI DAL CURRENT HEAD locale: NON reset/revert a `e21285b`.
- Login launcher normale già corretto: Chrome stabile diretto, sandbox attiva, niente `--no-sandbox`/Playwright launch per il login.
- Python globale; venv/virtualenv/poetry/uv vietati.
- Prima di aprire/chiudere/terminare una finestra o processo Chrome dedicato che potrebbe disturbare il lavoro dell'utente, invia `notify-send`. Non toccare mai il Chrome predefinito.

# Architettura obbligatoria
1. Esegui `roadmap_start` per 354882. Leggi solo browser.py, cli.py, core/discovery pertinenti, test e README.
2. Sostituisci il lifecycle a due browser con UN SOLO supervisor:
   - avvia direttamente `/usr/bin/google-chrome-stable` una sola volta con `--user-data-dir=~/.local/share/grindr-web-exporter/chrome-profile`;
   - abilita fin dall'avvio un endpoint DevTools SOLO loopback su porta dinamica/non conflittuale, necessario al tool per attach successivo; nessun avvio Playwright di Chrome;
   - Playwright si collega via CDP a QUELLO STESSO processo Chrome già visibile/autenticato;
   - NON chiudere/reaprire Chrome tra login, auth-check, discovery e scraping;
   - nessuna porta manuale richiesta all'utente.
3. Il comando normale deve diventare autonomo: `grindr-export export-all [--discovery-only]` avvia/riusa il supervisor e porta avanti tutto. `setup-browser` può restare come diagnostica/compatibilità, ma NON deve essere richiesto nel percorso normale.
4. Implementa auth state TRI-STATE:
   - `AUTHENTICATED`: evidenza positiva dell'app autenticata, anche su Nearby/home; se serve, naviga a `/chat` e verifica lì.
   - `UNAUTHENTICATED`: SOLO evidenza positiva di login reale (es. route/login UI/form coerente), non semplice assenza di sidebar.
   - `UNKNOWN`: caricamento incompleto, timeout, DOM inatteso, CDP failure o discovery failure.
   Regola assoluta: `UNKNOWN != UNAUTHENTICATED`. Missing `ChatSidebar` da solo NON autorizza mai una richiesta login.
5. Se `AUTHENTICATED`: continua immediatamente. Vietato chiedere login.
6. Se `UNAUTHENTICATED`: massimo UNA richiesta manuale di login per l'intero task:
   - mantieni la STESSA finestra/processo aperto;
   - monitora passivamente lo stato fino a `AUTHENTICATED`;
   - appena autenticato, continua automaticamente a `/chat`, discovery e scraping SENZA chiedere chiusura della finestra, senza rilanciare comandi e senza un secondo login.
   - non terminalizzare BLOCKED solo perché il login è in corso: resta nello stesso task/handoff.
7. Se `UNKNOWN`: diagnostica/fixa il failure tecnico; NON aprire login e NON chiedere credenziali.
8. Lifecycle robusto:
   - massimo una finestra Chrome dedicata visibile per questa esecuzione, salvo crash reale;
   - niente raffiche open/close;
   - Ctrl+C/SIGTERM devono eseguire cleanup bounded del browser task-owned e dei lock senza lasciare orfani;
   - shutdown finale deve essere graceful e consentire a Chrome di flushare il profilo;
   - lock stale viene ripulito solo se il PID proprietario è realmente morto;
   - lock vivo di un altro processo non viene killato senza verificare che sia il Chrome dedicato task-owned; prima `notify-send`.
9. Correggi il vero bug discovery:
   - identifica il contenitore scrollabile reale sotto `[data-testid="ChatSidebar"]` dalla geometria/overflow, non assumere che il root sia scrollabile;
   - scroll fino a convergenza con progresso misurabile (nuovi chat stable keys / scrollTop/scrollHeight) e limite temporale/iterazioni;
   - timeout/convergenza fallita deve riportare `DISCOVERY_FAILURE`, mai `UNAUTHENTICATED`;
   - nessun loop infinito.
10. Dopo discovery, esegui uno smoke reale su una chat lunga: raggiungi il top reale, poi percorri top->bottom con overlap/dedup/checkpoint fino al fondo. Se emerge un bug DOM/scroll, correggilo nello STESSO prompt; non tornare al login.
11. Aggiungi regressioni:
   - home/Nearby autenticata => AUTHENTICATED, non false logout;
   - missing sidebar + app in loading/unknown => UNKNOWN;
   - login form reale => UNAUTHENTICATED;
   - auth già presente => zero richieste login;
   - una richiesta login => stesso PID/processo continua dopo auth senza restart;
   - discovery timeout => DISCOVERY_FAILURE e zero login request;
   - sidebar scroll target reale/convergenza;
   - Ctrl+C cleanup no orphan/stale-live lock.
12. Aggiorna README con un solo flusso utente normale: `grindr-export export-all`. Niente istruzioni setup->login->close->rerun.
13. Commit locale finale; nessun remote nuovo. Non riaprire T7/recovery/MegaVault history.

# Runtime strategy
Prima di creare una nuova finestra, verifica se il Chrome dedicato corrente è già vivo. Se è task-owned e autenticato, riusalo e NON rilanciarlo. Se serve chiuderlo/riavviarlo una sola volta per migrare al nuovo supervisor, invia prima una notifica Fedora e preserva il profilo.

# Acceptance
PASS solo se:
- il percorso normale usa una sola istanza Chrome end-to-end;
- nessuna chiusura/riapertura è necessaria tra login e scraping;
- auth tri-state impedisce falsi logout;
- discovery reale termina con un conteggio finito di chat;
- smoke top->bottom su una chat lunga termina;
- test PASS;
- nessun processo Chrome dedicato orfano/lock vivo residuo;
- nessun contenuto/chat/credenziale Grindr finisce in Git/log/report.

Se serve davvero un login perché esiste evidenza positiva UNAUTHENTICATED, chiedilo UNA volta soltanto e mantieni il task RUNNING finché l'utente lo completa; poi continua automaticamente. Non creare un altro follow-up per il login.

# Stop
Dopo PASS, finalizza 354882 e STOP. Nessun refactor generale, dashboard, systemd, T7, nuovo profilo, nuovo repo o remote.

# Report
Massimo 9 righe: RESULT, COMMIT, BROWSER_PID/LIFECYCLE, AUTH_STATE, LOGIN_REQUESTS_COUNT, DISCOVERY, LONG_CHAT_SMOKE, TESTS, BLOCKER.