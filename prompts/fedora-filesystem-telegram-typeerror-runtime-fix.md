PROMPT_ID=427805 | project_id=15 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal

Risolvi il `TypeError` reale della notifica Telegram di variazione spazio filesystem osservato durante `PROMPT_ID=673914`, con diagnosi locale minima dell'API `telegram_notify` installata e fix strettamente limitato al sender Fedora.

# Starting point autoritativo

- repo: `/home/daniele/projects/fedora-system-monitor`, MegaVault project `15`;
- nei run `five_minute` reali il campo `telegram_free_space` ha mostrato `attempted=True`, `delivered=False`, `error=TypeError`, mentre i heartbeat Kuma erano consegnati;
- entrypoint: `src/fedora_system_monitor/capsules/notifications/__init__.py`, funzione `send_telegram_message()` chiamata da `notify_filesystem_free_changes()`;
- il codice attuale invoca `telegram_notify.send_message("Fedora System Monitor", redact_text(message), project_id=15)`; la firma effettiva del modulo installato è disponibile solo sul Fedora runtime ed è la prima cosa da verificare;
- credenziali Telegram canoniche già esistono localmente; non stamparle né leggerle nei log.

Prompt autosufficiente: niente README/roadmap/MEMORY/MegaVault, audit repo-wide o reinstallazione pacchetti.

# Esecuzione minima

1. Fotografia Git + fast-forward only se pulito. Nessun commit intermedio.
2. In **una sola** tool-call Python locale stampa soltanto `inspect.signature(telegram_notify.send_message)` e, se serve, il nome/versione/package path del modulo: niente source dump e nessun secret.
3. Confronta la firma con la singola call Fedora già nota. Se il mismatch è sufficiente a spiegare il `TypeError`, correggi solo `send_telegram_message()` e il test mirato. Se non basta, riproduci la chiamata con mock/local validation senza rete per ottenere il messaggio TypeError esatto; niente tentativi equivalenti.
4. Esegui una volta `PYTHONPATH=src python3 -m unittest tests.test_notifications`. Failure => leaf fix + una sola riconferma.
5. Solo dopo test PASS: commit/push una volta, quindi `sudo scripts/deploy-runtime.sh`.
6. Verifica il runtime con **una sola** chiamata reale `send_telegram_message()` contenente un messaggio chiaramente marcato `test PROMPT_ID=427805`; deve risultare `delivered=True`. Non alterare baseline spazio o DB per forzare un alert.
7. Controlla un solo run successivo pertinente per assicurarti che non compaia più `TypeError`; non aspettare più cicli se la chiamata reale è già PASS e il run non è dovuto entro un minuto.

# Acceptance

PASS se la firma installata spiega la failure, il sender è corretto senza esporre credenziali, test mirato PASS, runtime deployato e una notifica Telegram reale di test viene consegnata senza `TypeError`.

# Non-goal

Niente modifica soglie storage, cleanup Seagate, fix Kuma, refactor notifiche, update package o test globale.

# Stop

Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 427805 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 427805`

Output massimo 5 righe: `RESULT`, `ROOT_CAUSE`, `FIX`, `REAL_TEST`, `PUSH/BLOCKER`.
