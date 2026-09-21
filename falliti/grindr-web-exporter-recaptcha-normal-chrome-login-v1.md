PROMPT_ID=515955 | PARENT_PROMPT_ID=601566 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST
WORKDIR=/home/daniele/projects/grindr-web-exporter

# Goal
Chiudi SOLO il blocker di login reCAPTCHA emerso dopo 601566. Il profilo Chrome dedicato esiste già e l'exporter è implementato/testato: correggi il launcher/browser lifecycle in modo che il login manuale Grindr avvenga in un Chrome stabile normale, con sandbox attiva e senza i flag di automazione Playwright non necessari; poi riusa lo stesso profilo persistente per discovery/export. Non bypassare, automatizzare o neutralizzare reCAPTCHA.

# Evidenza già verificata
- 601566: commit locale `3703835`, nessun remote; 8 test PASS.
- Profilo dedicato: `~/.local/share/grindr-web-exporter/chrome-profile`, mode 0700.
- Browser mode attuale: Google Chrome stabile via Playwright persistent context; CDP solo override esplicito.
- Runtime reale: il profilo apre `https://web.grindr.com/login`, detection = unauthenticated.
- Nella finestra reale Chrome compare il warning: `unsupported command-line flag: --no-sandbox`.
- La pagina Grindr mostra: `Recaptcha error, please disable your ad-blockers and try again`; il badge reCAPTCHA è visibile in basso a destra, quindi non assumere che il problema sia "captcha assente".
- Non ci sono blocker T7/recovery/CDP da riaprire. NON ripetere 285894/601566.
- Python globale; venv/virtualenv/poetry/uv vietati.

# Implementazione/diagnosi minima
1. Esegui `roadmap_start` per 515955. Parti da commit `3703835`. Ispeziona SOLO launcher/browser manager, CLI login/setup-browser e relativi test.
2. Determina con un singolo probe mirato quali argomenti effettivi vengono passati a Chrome da `setup-browser`. Il risultato richiesto è eliminare dal percorso di LOGIN almeno `--no-sandbox`, `--enable-automation` e ogni altro flag Playwright/Chromium non necessario che renda il browser anomalo. Non disabilitare web security, sandbox, site isolation o protezioni browser.
3. Se Playwright `launch_persistent_context` non permette un login sufficientemente "normale", separa i due lifecycle:
   - LOGIN/SETUP: avvia `/usr/bin/google-chrome-stable` direttamente come utente normale con il data-dir dedicato esistente e il MINIMO indispensabile di flag; sandbox attiva; niente Playwright injection; niente estensioni aggiunte dal tool.
   - SCRAPING: dopo che il login è persistito e il browser di setup è chiuso, riapri lo STESSO data-dir in un modo controllabile dal tool. È ammesso che l'exporter gestisca internamente una porta CDP locale sul data-dir NON standard (Chrome >=136 lo consente), purché non richieda all'utente di avviare manualmente :9222 e non tocchi il profilo Chrome predefinito.
   - Evita doppia apertura concorrente dello stesso profile dir; rileva il lock e fornisci una transizione chiara setup→close→export.
4. Diagnostica reCAPTCHA senza bypass:
   - conferma che il profilo dedicato non abbia estensioni/ad-blocker installati/attivi dal tool;
   - verifica solo se le risorse ufficiali reCAPTCHA/Google necessarie vengono richieste/caricate e registra status/errori tecnici sanitizzati, senza token/cookie/contenuto sensibile;
   - se il problema è causato dal launcher/flag, correggilo;
   - se resta dopo un Chrome normale, identifica il blocker più locale supportato dall'evidenza (es. risorsa bloccata da rete/DNS/policy) senza disabilitare protezioni e senza tentare elusione.
5. `grindr-export setup-browser` deve quindi:
   - aprire Chrome normale sul profilo dedicato;
   - NON mostrare più il warning `--no-sandbox`;
   - non richiedere CDP per il login;
   - lasciare all'utente il login normale nella UI Grindr;
   - conservare la sessione nel profilo dedicato.
6. Mantieni `export-all`/discovery compatibili col profilo persistente già implementato. Il normale flusso utente deve essere: `setup-browser` una tantum → login → chiudi Chrome di setup → `export-all --discovery-only`; nessuna gestione manuale di porte.
7. Aggiungi test mirati solo per: login launcher senza `--no-sandbox`/automation flags, stesso profile dir tra setup/export, lock/concorrenza, command construction sanitizzata e regressione degli 8 test esistenti.
8. Runtime gate:
   - avvia `setup-browser` e verifica che il warning `--no-sandbox` sia assente;
   - verifica che la pagina Grindr non mostri più l'errore reCAPTCHA causato dal launcher, se risolvibile senza azione utente;
   - se la pagina è pronta per il login, termina BLOCKED SOLO per l'inserimento manuale delle credenziali/2FA/captcha eventualmente richiesto dalla UI, con una singola istruzione;
   - dopo login disponibile, rilancia discovery e smoke top→bottom senza ulteriori modifiche codice.
9. Commit locale del fix. Nessun remote nuovo. Aggiorna README solo per il flusso setup/login/export.

# Safety / non-goal
- Vietato bypassare, automatizzare, risolvere programmaticamente o interferire con reCAPTCHA/anti-bot.
- Vietato copiare cookie/token dal profilo Chrome predefinito.
- Vietato disabilitare sandbox/web security o installare estensioni anti-detection.
- Niente T7, recovery, refactor scraper, dashboard, systemd o audit generale.

# Acceptance
PASS solo se il login launcher usa Chrome stabile con sandbox attiva e senza warning/flag anomali, il profilo dedicato è condiviso correttamente col runtime di export, i test sono PASS e una sessione autenticata permette discovery + smoke top→bottom. Se l'unico passo restante è un normale login manuale nella UI ora funzionante, BLOCKED con quella sola azione è corretto.

# Report
Massimo 8 righe: RESULT, COMMIT, LOGIN_LAUNCHER, PROFILE_DIR, RECAPTCHA_DIAGNOSIS, TESTS, REAL_VALIDATION, BLOCKER.
