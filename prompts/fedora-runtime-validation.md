PROMPT_ID=690049 | project_id=15 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal
Chiudi SOLO il gate Kuma rimasto da `362714`, usando il runtime Fedora reale e il profilo Chrome canonico. Non ripetere deploy/test già conclusi.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/fedora-system-monitor`, branch `main`;
- `362714` ha già sincronizzato correttamente runtime Fedora e il drift di `fedora-system-monitor-collect@.service`; si è fermato esclusivamente con `KUMA_AUTH=LOGIN_REQUIRED_OR_STALE`;
- dopo l'analisi di `362714`, il remoto è stato corretto: `scripts/deploy-systemd-unit.sh` è ora eseguibile e la CI impedisce regressioni del bit `+x`;
- baseline remota verificata: commit `46235552ee292c96f6e4b00de39db2e520493b32`, GitHub Actions run `35110456948` PASS;
- tra la baseline runtime già distribuita `d4edd4a672bacf58f28c6e4a4025187d63d23928` e `46235552...` non ci sono modifiche al codice/runtime/systemd da distribuire: solo mode `+x` dell'helper e guard CI. NON rieseguire `deploy-runtime.sh` né deploy systemd;
- profilo Chrome ammesso: `/home/daniele/.var/app/com.google.Chrome/config/google-chrome`; non cercare altri profili, cookie, password o secret;
- monitor attesi: #39 interval/retry `180/60`; #40 Fedora Storage `480/180` con `upside_down=1`;
- `/etc/fedora-system-monitor/config.toml` deve conservare `inverted_categories=["storage"]`.

L'utente deve lanciare questo prompt solo dopo aver effettuato nuovamente il login a Kuma nel profilo Chrome canonico. Il login umano non è un task Codex.

# Esecuzione minima
1. Usa UNA sola shell call nel repo per: verificare checkout pulito e branch `main`; fare `timeout 20s git fetch origin main` + `git merge --ff-only origin/main`; fissare `RUN_HEAD`; verificare `RUN_HEAD == origin/main`, che `46235552ee292c96f6e4b00de39db2e520493b32` sia antenato e che `scripts/deploy-systemd-unit.sh` sia eseguibile. Nessuna suite locale, nessun CI rerun, nessun comando Git equivalente separato. Se fallisce, `BLOCKED` e stop.
2. Esegui UNA sola volta, bounded:
   `timeout 180s fedora-system-monitor kuma-configure --base-url https://kuma.danielegalati.com --chrome-profile /home/daniele/.var/app/com.google.Chrome/config/google-chrome`
   Il codice può ritentare internamente solo se rileggendo Chrome trova un token realmente diverso.
3. Se Kuma rifiuta ancora la sessione canonica: termina subito `BLOCKED` con `KUMA_AUTH=LOGIN_REQUIRED_OR_STALE`. Nessun altro profilo, nessuna ispezione token, nessun retry identico.
4. Solo se `kuma-configure` riesce, fai UN solo readback autenticato/read-only limitato ai monitor #39/#40 e verifica #39=`180/60`, #40=`480/180`, #40 `upside_down=1`; poi UNA sola lettura mirata del config locale per `inverted_categories=["storage"]`.
5. Qualunque mismatch => riporta il valore fallito e `BLOCKED`; niente patch, audit o debugging esplorativo.

# Acceptance
PASS solo se:
- checkout locale pulito e sincronizzato a `origin/main`, includendo `46235552...`;
- helper mirato è eseguibile dopo il pull;
- `kuma-configure` exit 0 col solo profilo Chrome canonico;
- #39=`180/60`;
- #40=`480/180` e `upside_down=1`;
- config locale conserva `inverted_categories=["storage"]`;
- nessun deploy/test/gate già concluso viene ripetuto.

# Non-goal
Niente modifiche codice, deploy runtime/systemd, user-systemd, Telegram, suite test, CI rerun, README/MegaVault, Oracle, altri profili Chrome o audit post-PASS.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 690049 --confirm-executed`

Non fare dry-run separati né verifiche equivalenti dopo finalizzazione. Stop al primo blocker. Output massimo 5 righe: `RESULT`, `RUNTIME`, `KUMA`, `STORAGE_INVERSION`, `BLOCKER`.
