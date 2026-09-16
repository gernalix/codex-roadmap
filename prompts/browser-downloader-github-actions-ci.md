[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=865147 | project_id=23 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
CI deterministica solo per i browser/downloader candidati alla pubblicazione:
- `gernalix/whatsapp-watcher`
- `gernalix/chatgpt_tab_watcher_v1`
- `gernalix/WindowTabNotes`
- `gernalix/yt_dlp_downloader`

`discord-exporter`, `amici_fb` e gli altri downloader volutamente PRIVATE sono fuori scope: non vale la pena spendere token/Actions per una campagna CI generica. Nessuna discovery di un ipotetico repo `project_id=50`.

# Routing minimo
Per repo leggi una volta: riga matrice visibility, manifest/package/requirements, test esistenti, `.github/workflows` e solo l'entrypoint/selector direttamente coinvolto. Niente esplorazione generale dei siti target.

# Test
- Browser/extension: fixture HTML locali; bootstrap/selector/listener e comportamento chiave in Chromium headless. WhatsApp: fixture `non letto -> doppia spunta blu -> un solo evento/notifica`. Valida manifest/caricamento extension quando pratico.
- `yt_dlp_downloader`: URL parsing, dedup/retry/state, filename/path safety e HTTP fixture/mock per success/404/410/timeout/rate-limit/media unavailable; niente download live/voluminosi.
- Trace/screenshot solo su failure; nessun account/cookie/sessione reale.

# CI
PUBLIC: hosted standard PR+push default branch. PRIVATE dopo audit: solo test veloci non-browser automatici; integrazione pesante manuale/locale, nessun schedule o nuovo self-hosted runner. Sempre path filter docs-only, concurrency, permissions minime e artifact failure-only <=3 giorni.

Chrome reale via CDP è ammesso **solo** se una failure concreta non è riproducibile con fixture e richiede browser autenticato; login/2FA/CAPTCHA => SKIPPED_LIVE, non blocker. Non esportare profile/cookie/localStorage/token.

# Ciclo / non-goal
Preflight minimo -> push -> singolo run GitHub; failure -> solo job/log fallito -> fix minimo -> nuovo run. Niente scraping live massivo, anti-bot bypass, refactor, feature, retry identici o audit post-PASS.

# Acceptance
Ogni repo in scope ha CI deterministica coerente con visibility; PUBLIC copre browser/network via fixture hosted; PRIVATE evita job pesanti ricorrenti.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 865147 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 865147`

Output massimo 6 righe: RESULT + una riga per repo + blocker.