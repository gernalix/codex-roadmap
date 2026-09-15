[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=865147 | project_id=50 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
CI deterministica per:
- `gernalix/whatsapp-watcher`
- `gernalix/chatgpt_tab_watcher_v1`
- `gernalix/WindowTabNotes`
- `gernalix/yt_dlp_downloader`
- `gernalix/discord-exporter`
- `gernalix/amici_fb`
- un eventuale repo remoto di `project_id=50` SOLO se MegaVault lo identifica direttamente; nessuna ricerca di downloader aggiuntivi.

Default: fixture/mock + Playwright/Chromium headless. Nessun sito/account reale nel gate CI.

# Routing minimo
Per repo risolvi una volta stato/project_id e leggi: riga matrice pubblico/privato, manifest/package/requirements, entrypoint direttamente testato, test esistenti, `.github/workflows`. Per extension leggi solo `manifest.json` e script/selector necessari. Niente esplorazione generale dei siti target.

# Test
Browser/extension:
- fixture HTML locali per gli stati DOM necessari;
- bootstrap, selector/listener e comportamento chiave in Chromium headless;
- WhatsApp: transizione fixture `non letto -> doppia spunta blu -> un solo evento/notifica`;
- valida manifest/caricamento extension quando fattibile;
- trace/screenshot solo su failure.

Downloader/exporter:
- URL parsing, dedup, retry/state, filename/path safety, DB state;
- HTTP fixture/mock per success, 404/410, timeout/rate-limit/media unavailable;
- `yt-dlp` solo contro fixture/local HTTP server quando possibile;
- niente download voluminosi/live.

# Visibility/costo
- PUBLIC: GitHub-hosted standard su PR + push default branch; Playwright automatico.
- PRIVATE: automatico solo test veloci non-browser; Playwright/download integration pesante `workflow_dispatch` o locale, senza schedule. Non installare self-hosted runner nuovi solo per questi repo.

Sempre: path filters per evitare docs-only, concurrency cancel-in-progress, cache solo se realmente utile, artifact failure-only con retention <=3 giorni, nessun cookie/account/production secret.

# Chrome reale — eccezione, non fase normale
NON fare smoke Chrome se fixture CI PASS. Usa una sola sessione Chrome Fedora via CDP/Playwright solo se una failure concreta non è riproducibile con fixture e il comportamento dipende necessariamente dal browser autenticato. Non esportare profile/cookie/localStorage/token; login/2FA/CAPTCHA => `SKIPPED_LIVE`, non blocker della CI fixture.

# Ciclo Codex
Preflight minimo -> push -> run GitHub canonico. `gh run watch --exit-status` una volta; failure -> solo job/log fallito -> fix minimo -> nuovo run. Niente full suite locale duplicata, retry identici o audit post-PASS.

# Non-goal
Niente scraping massivo/live, bypass anti-bot, refactor generale, modifiche funzionali non necessarie ai test o navigazione GitHub via Chrome.

# Acceptance
Ogni repo attivo ha CI deterministica coerente con visibility; PUBLIC copre browser/network in hosted CI; PRIVATE evita job pesanti ricorrenti. Chrome reale non è requisito se fixture PASS.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 865147 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 865147`

Output massimo 7 righe: RESULT, public/private strategy, browser repos, downloader repos, test aggiunti, live smoke eventuale, blocker.