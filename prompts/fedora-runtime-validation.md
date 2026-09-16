PROMPT_ID=847392 | project_id=15 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST

# Goal
Distribuisci UNA sola volta sul Fedora reale i fix già presenti in `fedora-system-monitor/main` e chiudi insieme i tre soli gate runtime rimasti: falso `user systemd ... status 1`, invio Telegram e riconciliazione Kuma con Fedora Storage ancora invertito.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/fedora-system-monitor`, branch `main`;
- runtime canonico: Fedora locale, non Oracle VM;
- `origin/main` contiene `8101273e476135c2ac7178b2cd1097c562fb49aa` o successivo;
- in quella storia sono già inclusi: Kuma WAL/session recovery (`c223f372...`), `DBUS_SESSION_BUS_ADDRESS` per `operator_external` (`7a5777a5...`), relativo test (`fa8af004...`), fix firma `telegram_notify.send_message()` (`047117dd...`) e CI deterministica;
- GitHub Actions su `8101273e...` è già PASS: NON rieseguire localmente unit test/suite coperti dalla CI;
- monitor Kuma canonici: #39 interval/retry `180/60`; #40 Fedora Storage `480/180` con `upside_down=1`;
- `/etc/fedora-system-monitor/config.toml` deve conservare `inverted_categories=["storage"]`.

Prompt autosufficiente: niente README/roadmap/MegaVault, audit repo-wide, aggiornamenti Fedora o discovery Oracle.

# Esecuzione minima
1. Una fotografia Git. Se worktree pulito: UNA `git fetch origin main` + `git merge --ff-only origin/main`. Se dirty non pertinente/divergente: `BLOCKED`, stop.
2. Verifica solo che `8101273e476135c2ac7178b2cd1097c562fb49aa` sia antenato di HEAD. Nessun test locale duplicato.
3. Esegui UNA volta `sudo scripts/deploy-runtime.sh`.
4. **user-systemd:** avvia una volta ciascuna le unità reali `fedora-system-monitor-collect@minute.service` e `fedora-system-monitor-collect@five_minute.service`; usa il readback canonico più stretto già disponibile per i due run. PASS del gate se non compare più il falso `user systemd: command exited with status 1`. Un vero servizio utente failed/missing va riportato come failure reale, non silenziato.
5. **Telegram:** invia UNA sola notifica di prova tramite il percorso Fedora System Monitor già esistente. PASS se non compare il precedente `TypeError`/errore di firma e l'invio risulta delivered. Non stampare token/chat id e non ispezionare secret.
6. **Kuma:** esegui UNA volta:
   `fedora-system-monitor kuma-configure --base-url https://kuma.danielegalati.com --chrome-profile /home/daniele/.var/app/com.google.Chrome/config/google-chrome`
   Se la sessione è ancora rifiutata, `BLOCKED` con `KUMA_AUTH=STALE_AFTER_WAL_FIX`; niente ricerca di altri profili o retry identici.
7. Se Kuma riesce, fai un solo readback autenticato/read-only di #39/#40 e verifica esclusivamente #39=`180/60`, #40=`480/180`, `upside_down=1`; verifica anche una volta il blocco `[notifications]` locale per `inverted_categories=["storage"]`.
8. Se uno dei tre gate fallisce per una causa NUOVA e locale, raccogli soltanto evidenza del leaf interessato. È ammesso al massimo un fix leaf + relativo test mirato + redeploy; niente nuova discovery generale. Se non è evidente/localizzato, `BLOCKED`.

# Acceptance
PASS se il runtime usa `8101273e...` o successivo, minute/five_minute non hanno più il falso errore user-systemd, Telegram consegna senza TypeError, `kuma-configure` riesce e #39/#40 + inversione Storage restano corretti.

# Non-goal
Niente Seagate/storage cleanup, soglie/timeout, refactor monitor, suite completa, CI rerun, update OS, Oracle VM o audit post-PASS.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 847392 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 847392`

Stop al primo blocker. Output massimo 7 righe: `RESULT`, `RUNTIME`, `USER_SYSTEMD`, `TELEGRAM`, `KUMA`, `STORAGE_INVERSION`, `BLOCKER`.