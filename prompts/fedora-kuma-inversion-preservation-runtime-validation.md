PROMPT_ID=528614 | project_id=15 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal

Chiudi SOLO la validazione runtime rimasta BLOCKED in `PROMPT_ID=936251`: prova sul Fedora reale il recupero sessione Kuma corretto e conferma che una riconciliazione reale preservi l'inversione di Fedora Storage.

# Starting point autoritativo

- repo locale: `/home/daniele/projects/fedora-system-monitor`, branch `main`, project_id `15`;
- `PROMPT_ID=936251` ha già dato PASS ai test mirati e distribuito `61753578e1a33963fba099e7fedc6124a9bfeeb8`; si è fermato SOLO perché `kuma-configure` recuperava una sessione Chrome rifiutata da Kuma;
- `origin/main` contiene ora `c223f372c21db625cd4d7a0637c05f770137f583` o successivo. I commit `bd369664880e518988be10be95811bb9b70ef11c` + `c223f372c21db625cd4d7a0637c05f770137f583` fanno leggere a `recover_chrome_session_token()` anche il WAL LevelDB `*.log` (non solo `*.ldb`) e accettano sia la root Chrome sia la directory `Default` diretta, con test sintetico dedicato;
- runtime/config di `fedora-system-monitor` sono LOCALI sul Fedora, non sulla Oracle VM;
- #40 Fedora Storage deve restare `upside_down=1`; valori canonici: #39 interval/retry `180/60`, #40 `480/180`;
- il vero alert spazio del Seagate UUID `22E02106E020E1B1` è fuori scope.

Non leggere README/roadmap/spiegazioni/MegaVault, non fare audit repo-wide e non riaprire la diagnosi heartbeat/storage.

# Esecuzione minima

1. Una sola fotografia Git; se pulito fai `git fetch origin && git pull --ff-only`. Se dirty non pertinente: BLOCKED.
2. Esegui UNA volta soltanto:
   `PYTHONPATH=src python3 -m unittest tests.test_kuma_admin`
3. Sul Fedora locale leggi soltanto `.source-revision` e il blocco `[notifications]` di `/etc/fedora-system-monitor/config.toml`. NON usare `oracle_ssh.sh`, non cercare unità/container/DB Kuma sulla Oracle.
4. Se il runtime è indietro rispetto a HEAD, esegui UNA volta `sudo scripts/deploy-runtime.sh`.
5. Esegui UNA volta:
   `fedora-system-monitor kuma-configure --base-url https://kuma.danielegalati.com --chrome-profile /home/daniele/.var/app/com.google.Chrome/config/google-chrome`
6. Se Kuma rifiuta ancora la sessione dopo il fix WAL: STOP immediato con `RESULT=BLOCKED` e `KUMA_AUTH=STALE_AFTER_WAL_FIX`. NON cercare altri profili, NON usare Browser Use per scoprire il profilo, NON creare script Socket.IO ad hoc e NON fare retry identici. Il passo successivo umano è rinnovare il login Kuma nel profilo Chrome locale indicato.
7. Se `kuma-configure` riesce, fai un solo readback autenticato e read-only di #39/#40 con il percorso già funzionante più diretto disponibile. Verifica SOLO: #39 `180/60`; #40 `480/180` e `upside_down=1`. Massimo due interazioni browser totali se serve la UI; niente `chrome://`, niente esplorazione del profilo.
8. Conferma che `[notifications]` continui a contenere `inverted_categories=["storage"]`. Fine. NON attendere tre cicli: a 480 s per #40 significherebbe ~24 minuti e non testa il difetto di session-recovery/inversion-preservation oggetto di questo task.

# Acceptance

PASS se il test mirato passa, il runtime usa `c223f372...` o successivo, `kuma-configure` completa, #39 resta `180/60`, #40 resta `480/180` con `upside_down=1`, e la config locale mantiene l'inversione Storage.

# Non-goal

Niente cleanup Seagate, soglie/timeout, `spd5118`, heartbeat multi-ciclo, update Fedora, audit generale, manipolazione manuale del DB Kuma o refactor.

# Stop

Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 528614 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 528614`

Output massimo 6 righe: `RESULT`, `TEST`, `RUNTIME_REV`, `KUMA_CONFIGURE`, `READBACK`, `BLOCKER/PUSH`.
