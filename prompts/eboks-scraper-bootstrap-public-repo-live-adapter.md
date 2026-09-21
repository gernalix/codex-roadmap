PROMPT_ID=218695 | PROJECT=MegaVault / e-Boks bootstrap | project_id=23 | MODEL=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST

# Goal
Crea e pubblica il repository pubblico `gernalix/eboks-scraper` dal seed già implementato, registralo canonicamente in MegaVault e calibra/verifica SOLO l'adapter UI reale di e-Boks sulla sessione Chrome autenticata di Fedora.

# Starting point
- seed carrier: `gernalix/codex-roadmap`, branch `seed/eboks-scraper-20260921`, file `seeds/eboks-scraper.zip.b64`, commit `13c104cf038d0f30dbe9366161c643e3a5869139`; NON mergiare questo branch in roadmap main.
- Il seed passa già 5 unit test Python + syntax check JS.
- Architettura già implementata: MV3 extension -> normale UI e-Boks “Save local copy” -> watcher Python localhost -> PDF/ZIP -> SHA-256 dedupe -> SQLite/FTS5 -> pdftotext, OCR opzionale -> systemd user service.
- Nessuna API privata e-Boks, cookie/session extraction, automazione MitID, CAPTCHA/rate-limit bypass.
- target checkout: `~/projects/eboks-scraper`; target remote pubblico: `gernalix/eboks-scraper`.
- La sessione e-Boks autenticata in Chrome è un prerequisito runtime da usare, non da automatizzare.

# Execution
1. Prima di altro lavoro esegui `python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 218695`. Rispetta il worktree_path restituito per MegaVault; il nuovo repo e-Boks va creato separatamente in `~/projects/eboks-scraper`.
2. Fai un solo fetch mirato del branch seed e decodifica il file esatto nel target checkout. Non esplorare o riscrivere il progetto già implementato.
3. Crea il repository GitHub PUBBLICO `gernalix/eboks-scraper` con il tooling GitHub già autenticato locale, inizializza/pusha `main`. Registra il nuovo progetto in MegaVault con il meccanismo canonico esistente; NON inventare un project_id.
4. Esegui una volta i test del seed. Installa/avvia il backend con `scripts/install.sh`; dipendenze Python/Fedora globali soltanto, MAI venv.
5. Carica l'estensione unpacked nel Chrome reale. Prima `dryRun=true`. Ispeziona SOLO il DOM necessario a `extension/adapter.js`; se confidence/selettori non bastano, modifica SOLO adapter/selettori e test direttamente pertinenti. Non fare reverse engineering di endpoint privati.
6. Smoke reale bounded su 1-3 messaggi max: UI ufficiale Save local copy -> download -> watcher -> archive -> estrazione testo -> SQLite. Verifica anche che re-ingest dello stesso file sia idempotente via SHA-256.
7. Se compare login scaduto, CAPTCHA, 429/throttling o altro anti-bot, STOP fail-closed: nessun bypass e nessun retry identico.
8. Commit/push SOLO i fix necessari al nuovo repo. Verifica repo pubblico e CI. Dopo conferma del target remoto, elimina il branch temporaneo `seed/eboks-scraper-20260921` da codex-roadmap senza toccare main.

# Acceptance
- `gernalix/eboks-scraper` esiste ed è pubblico, con seed + eventuali fix adapter validati;
- nuovo progetto registrato canonicamente in MegaVault;
- unit test/syntax check PASS e backend locale healthy;
- smoke reale archivia almeno 1 documento e-Boks con testo estratto in SQLite; se impossibile, BLOCKED solo per un prerequisito esterno concreto e non aggirabile in sicurezza;
- dry-run/fail-closed e divieti API privata/login automation/anti-bot bypass restano intatti;
- branch seed temporaneo rimosso dopo bootstrap riuscito.

# Non-goal
Export completo della inbox, refactor/cleanup/modernizzazioni, dashboard aggiuntive, audit repo/browser generali.

# Stop
Al PASS finalizza subito via roadmap_result/roadmap_finish e STOP. Output finale max 8 righe: PROMPT_ID, RESULT, REPO_URL, PROJECT_ID, TESTS, LIVE_SMOKE, CI, BLOCKER se presente.
