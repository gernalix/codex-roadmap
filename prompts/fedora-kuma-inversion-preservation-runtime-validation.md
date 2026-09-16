PROMPT_ID=936251 | project_id=15 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST

# Goal

Valida sul runtime reale e distribuisci il fix già implementato in `fedora-system-monitor` che impedisce a `kuma-configure` di azzerare accidentalmente `upside_down` sui monitor Uptime Kuma esistenti. Chiudi il rischio di regressione emerso da `PROMPT_ID=673914` senza riaprire la diagnosi storage né cambiare soglie/timeout.

# Starting point autoritativo

- repo locale: `/home/daniele/projects/fedora-system-monitor`, branch `main`, MegaVault project `15`;
- `PROMPT_ID=673914` ha già risolto il falso `No heartbeat`: #39 Fedora Host era UP e #40 Fedora Storage restava correttamente DOWN per il vero alert spazio; #40 ha `upside_down=1` e `/etc/fedora-system-monitor/config.toml` ha `inverted_categories=["storage"]`;
- il vero filesystem quasi pieno è il Seagate UUID `22E02106E020E1B1`; cleanup dati è fuori scope;
- il vecchio `kuma_admin._monitor_payload()` hardcodava `upsideDown=False`, quindi una futura riconciliazione `kuma-configure` poteva annullare il fix live;
- `origin/main` contiene `61753578e1a33963fba099e7fedc6124a9bfeeb8` o successivo: `_monitor_payload(..., upside_down=...)`, `_monitor_upside_down()` e `tests/test_kuma_admin.py` preservano il flag esistente durante la riconciliazione.

Prompt autosufficiente: NON leggere README/roadmap/spiegazioni/MEMORY/MegaVault e non fare audit repo-wide.

# Esecuzione minima

1. Una sola fotografia Git. Se pulito, `git fetch origin` + `git pull --ff-only`; se dirty non pertinente, BLOCKED. Non creare commit intermedi.
2. Verifica che HEAD contenga il fix sopra; poi esegui una sola volta:
   `PYTHONPATH=src python3 -m unittest tests.test_kuma_admin tests.test_notifications tests.test_storage_heartbeat_policy`
3. Leggi in una sola tornata lo stato runtime strettamente necessario: `.source-revision`, `/etc/fedora-system-monitor/config.toml` limitato a `[notifications]`, e da Kuma #39/#40 `interval`, `retry_interval`, `upside_down` + ultimi heartbeat. Usa direttamente l'helper privilegiato noto `/home/daniele/projects/vm_oracle/scripts/oracle_ssh.sh`; niente probe non privilegiati e niente schema guessing: se serve una colonna incerta, una sola `PRAGMA table_info`.
4. Se il runtime è indietro rispetto a HEAD, usa soltanto `sudo scripts/deploy-runtime.sh`.
5. Esegui **una sola** riconciliazione canonica `fedora-system-monitor kuma-configure --base-url https://kuma.danielegalati.com`, usando il profilo Chrome già autenticato. Se il default non contiene la sessione, individua una sola volta il profilo Chrome reale e ripeti solo con quel path; niente manipolazione SQLite manuale del monitor.
6. Readback immediato: #40 deve conservare `upside_down=1`; interval/retry di #39/#40 devono restare invariati; `/etc` deve continuare a contenere l'inversione Storage.
7. Per la verifica temporale non fare loop manuali. Avvia **un solo verifier bounded** che attende il timer reale e termina appena prova 3 cicli schedulati consecutivi per #39/#40 senza nuovi `No heartbeat in the time window`. #40 deve restare DOWN con `active alerts=1` finché il Seagate è sotto soglia; #39 può riflettere il suo stato reale ma non heartbeat-missing.
8. Se il fix remoto richiede una correzione per una failure concreta, modifica solo `kuma_admin`/test direttamente coinvolti, rilancia solo il leaf fallito, poi un solo commit/push finale. Altrimenti nessun commit artificiale.

# Acceptance

PASS se il test mirato passa, il runtime usa la revisione validata, una riconciliazione reale `kuma-configure` non modifica `upside_down=1` di #40, interval/retry restano invariati e 3 cicli schedulati consecutivi non producono heartbeat-missing.

# Non-goal

Niente cleanup del Seagate, modifica soglie/timeout, fix `spd5118`, audit generale, update Fedora, reinstallazione completa o modifica manuale del DB Kuma.

# Stop

Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 936251 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 936251`

Output massimo 6 righe: `RESULT`, `TEST`, `RUNTIME_REV`, `KUMA_RECONCILE`, `THREE_CYCLES`, `PUSH/BLOCKER`.
