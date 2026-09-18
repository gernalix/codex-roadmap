PROMPT_ID=526713 | PARENT_PROMPT_ID=690049 | project_id=15 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST


# Autonomia operativa
Goal + acceptance criteria definiscono lo scope; i passi sono il piano iniziale, non una whitelist.
Per qualunque failure nello stesso dominio puoi fare discovery mirata e modificare codice, test, adapter, config, unit/script e documentazione tecnica necessari al goal, anche se non nominati esplicitamente. Puoi usare comandi/helper equivalenti più corretti se quelli indicati sono obsoleti, correggere più blocker dello stesso dominio in batch, commit/pushare fix in-scope e continuare automaticamente.
Non terminare BLOCKED/FAIL per test/compile failure, mismatch di file/helper, warning, remote advance riconciliabile, lock transitorio o necessità di toccare un file adiacente. BLOCKED solo per credenziale/permesso/decisione umana indispensabile, runtime esterno indisponibile senza alternativa, rischio dati/distruzione non autorizzata o conflitto semantico materialmente fuori goal. FAIL solo dopo recovery in-scope ragionevole realmente esaurito.

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
1. In un preflight compatto sincronizza il repo preservando lavoro utente, fissa RUN_HEAD, richiedi che `46235552ee292c96f6e4b00de39db2e520493b32` sia antenato e verifica l'helper deploy. Se qualcosa fallisce, diagnostica e correggi autonomamente Git/helper/unit/config nello stesso dominio; non bloccare per una semplice differenza dal vecchio starting point.
2. Esegui UNA sola volta, bounded:
   `timeout 180s fedora-system-monitor kuma-configure --base-url https://kuma.danielegalati.com --chrome-profile /home/daniele/.var/app/com.google.Chrome/config/google-chrome`
   Il codice può ritentare internamente solo se rileggendo Chrome trova un token realmente diverso.
3. Se Kuma rifiuta ancora la sessione canonica: termina subito `BLOCKED` con `KUMA_AUTH=LOGIN_REQUIRED_OR_STALE`. Nessun altro profilo, nessuna ispezione token, nessun retry identico.
4. Solo se `kuma-configure` riesce, fai UN solo readback autenticato/read-only limitato ai monitor #39/#40 e verifica #39=`180/60`, #40=`480/180`, #40 `upside_down=1`; poi UNA sola lettura mirata del config locale per `inverted_categories=["storage"]`.
5. Qualunque mismatch tecnico riproducibile => diagnostica il minimo necessario, applica il fix in-scope a monitor/unit/helper/config, ridistribuisci e verifica di nuovo. `BLOCKED` resta riservato soprattutto al caso Kuma che richiede davvero un login/credenziale utente o ad altro blocker esterno non aggirabile in sicurezza.

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
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 526713 --confirm-executed`

Non fare dry-run separati né verifiche equivalenti dopo finalizzazione. Stop al primo blocker. Output massimo 5 righe: `RESULT`, `RUNTIME`, `KUMA`, `STORAGE_INVERSION`, `BLOCKER`.
