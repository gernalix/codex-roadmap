PROMPT_ID=362714 | project_id=15 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal
Chiudi l'unico gate Fedora rimasto dopo `847392`: distribuire l'ultimo `fedora-system-monitor/main`, ottenere una sessione Kuma valida dal SOLO profilo Chrome canonico e verificare che i monitor #39/#40 mantengano configurazione e inversione Storage corrette.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/fedora-system-monitor`, branch `main`;
- runtime canonico: Fedora locale, non Oracle VM;
- `847392` ha già verificato sul runtime reale: `USER_SYSTEMD=PASS` e `TELEGRAM=PASS`; NON ripetere quei gate;
- il fix user-systemd è già su remoto (`19ab9384acf3c7533dd3b4dfbd0e4a16d169dc2c`) e la regressione è ora coperta dalla CI;
- `main` remoto include almeno `d4edd4a672bacf58f28c6e4a4025187d63d23928`, con CI verde; include deploy systemd mirato fail-closed, rilevamento drift delle unità e login Kuma che non ripete lo stesso token senza nuova evidenza;
- profilo Chrome ammesso: `/home/daniele/.var/app/com.google.Chrome/config/google-chrome`; non cercare altri profili, cookie, password o secret;
- monitor attesi: #39 interval/retry `180/60`; #40 Fedora Storage `480/180` con `upside_down=1`;
- `/etc/fedora-system-monitor/config.toml` deve conservare `inverted_categories=["storage"]`.

Prompt autosufficiente: niente README/roadmap/MegaVault, niente audit repo-wide, niente test user-systemd/Telegram, niente Oracle.

# Esecuzione minima
1. Una fotografia Git (`status --short`, branch, HEAD). Se pulito: UNA `timeout 20s git fetch origin main` + `git merge --ff-only origin/main`; altrimenti `BLOCKED`. Nessun retry.
2. Salva `RUN_HEAD` e verifica localmente `RUN_HEAD == origin/main` e che `d4edd4a672bacf58f28c6e4a4025187d63d23928` sia antenato. La CI è già verde: nessuna suite locale duplicata.
3. Esegui UNA volta `sudo scripts/deploy-runtime.sh`. Se segnala drift systemd, sincronizza UNA sola volta esclusivamente le unità elencate con `sudo scripts/deploy-systemd-unit.sh <unit...>`. Non riavviare/riprovare minute, five_minute o Telegram.
4. Esegui UNA sola volta, bounded:
   `timeout 180s fedora-system-monitor kuma-configure --base-url https://kuma.danielegalati.com --chrome-profile /home/daniele/.var/app/com.google.Chrome/config/google-chrome`
   Il codice può ritentare internamente solo se rileggendo Chrome trova un token realmente diverso.
5. Se Kuma rifiuta ancora la sessione canonica, termina subito `BLOCKED` con `KUMA_AUTH=LOGIN_REQUIRED_OR_STALE`. Non cercare altri profili, non ispezionare/stampare token, non fare retry identici e non tentare credenziali.
6. Se `kuma-configure` riesce, fai UN solo readback autenticato/read-only limitato ai monitor #39/#40 e verifica: #39 `180/60`; #40 `480/180`; #40 `upside_down=1`. Poi leggi UNA volta solo il blocco locale necessario a confermare `inverted_categories=["storage"]`.
7. Qualunque mismatch nuovo => riporta solo il valore fallito e `BLOCKED`; niente patch o debugging esplorativo in questa sessione.

# Acceptance
PASS solo se:
- runtime Fedora usa `RUN_HEAD` sincronizzato a `origin/main` e include `d4edd4a...`;
- eventuale drift systemd segnalato dal deploy è stato sincronizzato con l'helper mirato;
- `kuma-configure` completa con exit 0 usando il solo profilo Chrome canonico;
- #39=`180/60`;
- #40=`480/180` e `upside_down=1`;
- config locale conserva `inverted_categories=["storage"]`;
- nessun gate già PASS in `847392` è stato rieseguito.

# Non-goal
Niente modifiche codice, user-systemd, Telegram, Seagate/storage cleanup, soglie diverse da quelle sopra, suite test, CI rerun, aggiornamenti OS, Oracle VM, altri profili Chrome o audit post-PASS.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 362714 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 362714`

Stop al primo blocker. Output massimo 5 righe: `RESULT`, `RUNTIME`, `KUMA`, `STORAGE_INVERSION`, `BLOCKER`.
