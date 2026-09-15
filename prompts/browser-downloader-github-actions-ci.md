[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=865147 | project_id=50 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Aggiungere test/CI ripetibili ai repository browser automation e downloader indicati:
- `gernalix/whatsapp-watcher`
- `gernalix/chatgpt_tab_watcher_v1`
- `gernalix/WindowTabNotes`
- `gernalix/yt_dlp_downloader`
- `gernalix/discord-exporter`
- `gernalix/amici_fb`
- gli eventuali downloader attivi collegati a `project_id=50`, ma solo se MegaVault li identifica esplicitamente come parte dello stesso progetto/campagna.

Usa Playwright/Chromium headless e fixture/mock come default. Chrome reale autenticato è solo fallback per uno smoke locale indispensabile.

# Routing minimo
Per ciascun repo:
- risolvi `project_id`/stato via MegaVault;
- leggi solo manifest/package/requirements, entrypoint, test esistenti e `.github/workflows`;
- per extension Chrome leggi `manifest.json`, background/content script e DOM selector direttamente usati;
- niente esplorazione generale dei siti target.

# Browser/extension tests
Per `whatsapp-watcher`, `chatgpt_tab_watcher_v1`, `WindowTabNotes`:
1. usa fixture HTML locali che rappresentino gli stati DOM necessari;
2. Playwright/Chromium headless deve verificare bootstrap, selector/event listener e comportamento chiave;
3. per WhatsApp simula almeno transizione messaggio non letto -> doppia spunta blu -> un singolo evento/notifica, senza login reale;
4. se è un'estensione, valida anche manifest e caricamento dell'estensione in Chromium test quando fattibile;
5. screenshot/trace Playwright solo su failure.

Non rendere la CI dipendente dal DOM live di WhatsApp/ChatGPT.

# Downloader/exporter tests
Per downloader/exporter:
- URL parsing, dedup, retry/state machine, filename/path safety e DB state con fixture;
- HTTP mock/fixture per success, 404/410, timeout/rate-limit e media non più disponibile;
- `yt-dlp` può essere smoke-testato contro una fixture/local HTTP server; niente dipendenza obbligatoria da un sito terzo live;
- non scaricare media voluminosi in CI;
- nessun account/cookie reale nei workflow PR.

# Chrome reale locale — solo se necessario
Dopo CI fixture PASS, Codex può fare **un solo** smoke sul Chrome Fedora già autenticato se serve a verificare un selector/integrazione che non può essere rappresentato ragionevolmente con fixture.
Preferisci CDP/Playwright locale. Non esportare cookie, localStorage, token o profilo Chrome; non automatizzare CAPTCHA/2FA. Se compare richiesta di login/2FA, `BLOCKED` per quello smoke ma non invalidare i test fixture già PASS.

# GitHub Actions
PR + push default branch; setup runtime minimo; Playwright browser cache se utile; concurrency cancel-in-progress. Per repo senza test, aggiungi soltanto i test di regressione ad alto valore descritti sopra. Usa `gh` per osservare i run; Chrome non deve essere usato per navigare GitHub se CLI/API bastano.

# Non-goal
- niente scraping massivo/live audit;
- niente modifiche funzionali non necessarie ai test;
- niente bypass anti-bot;
- niente credenziali o secret di produzione;
- niente refactor generale;
- niente test end-to-end fragili basati su layout live se una fixture copre la logica.

# Acceptance
Ogni repo attivo ha CI verde e deterministica; browser logic è coperta da Playwright/fixture; network logic da mock/fixture; eventuale smoke Chrome reale è limitato e secret-safe.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 865147 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 865147`

Output massimo 8 righe: RESULT + stato browser repos + downloader repos + eventuale smoke Chrome + blocker.
