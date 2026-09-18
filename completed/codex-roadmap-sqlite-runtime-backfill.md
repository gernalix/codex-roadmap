PROMPT_ID=813383 | project_id=23 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Attiva SOLO il nuovo backend SQLite di `gernalix/codex-roadmap` sul Fedora reale: importa lo storico disponibile da `~/projects/codex-usage`, installa il sync automatico già implementato e verifica che DB + viste Markdown/Obsidian restino coerenti. Non ridisegnare l'architettura.

# Starting point autoritativo
- repo roadmap canonico: `/home/daniele/projects/codex-roadmap`, branch `main`;
- repo dati Codex canonico: `/home/daniele/projects/codex-usage`, branch `main`;
- `roadmap.sqlite` è ora source of truth; `roadmap.md`, `spiegazioni.md`, `prompt-registry.md` e `obsidian/` sono proiezioni generate;
- codice già presente: `tools/roadmap_db.py`, `tools/import_codex_usage.py`, `tools/roadmap_sync.py`, `tools/roadmap_result.py`;
- unit già presenti: `systemd/codex-roadmap-sync.service` e `.timer`;
- non leggere README/spiegazioni/MEMORY/MegaVault: il task è completo qui.

# Esecuzione
1. In una sola shell call: porta SOLO `codex-roadmap` a `origin/main` con fetch + `git merge --ff-only`; richiedi branch `main`. Non toccare dirty path utente non sovrapposti.
2. Esegui:
   `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`
   e
   `python3 tools/roadmap_db.py --repo . verify`.
   Al failure correggi soltanto il difetto dimostrato e riesegui il leaf test, poi una sola suite finale.
3. Esegui una prima riconciliazione reale:
   `python3 tools/roadmap_sync.py --repo /home/daniele/projects/codex-roadmap --source /home/daniele/projects/codex-usage`
   Deve importare i `metrics.json` disponibili senza copiare prompt text/final response/source path nel DB pubblico. Collisioni di materializzazione devono essere registrate e non sovrascrivere automaticamente lo stato.
4. Verifica con UNA query SQLite aggregata:
   - `PRAGMA foreign_key_check` vuoto;
   - esistono righe in `executions` per gli storici disponibili;
   - per `PROMPT_ID=424261`, se presente nel source, risultano timestamp start/end e `PASS`;
   - `v_runnable_prompts` e `v_attention` sono interrogabili;
   - `roadmap.md`, `spiegazioni.md`, `prompt-registry.md`, `obsidian/Prompts`, `obsidian/Projects`, `obsidian/Dashboards` esistono.
5. Installa copiando i due file già presenti in `systemd/` sotto `~/.config/systemd/user/`, poi `systemctl --user daemon-reload` e `systemctl --user enable --now codex-roadmap-sync.timer`.
6. Avvia UNA volta `systemctl --user start codex-roadmap-sync.service`; verifica service exit 0 e timer enabled+active. Un secondo avvio immediato deve essere `noop` salvo nuovi metrics realmente comparsi.
7. Se il task ha corretto codice, commit/push `main` una sola volta. Non aggiungere nuovi task di sola verifica.
8. PASS: finalizza una sola volta con:
   `python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 813383 --confirm-executed`
   BLOCKED/FAIL: registra l'esito una sola volta con `roadmap_result.py --result BLOCKED|FAIL --confirm-executed`.

# Acceptance
PASS solo se test/verify PASS, storico disponibile importato senza dati sensibili, viste Markdown/Obsidian generate dal DB, sync idempotente, timer enabled+active e service exit 0.

# Non-goal
Niente redesign schema, audit generale di altri repo, scansione manuale dei rollout raw, modifica di PersonalHub/MegaVault, refactor estranei, retry identici.

Output massimo 7 righe: RESULT, TESTS, BACKFILL, DB_VERIFY, OBSIDIAN, SYSTEMD, BLOCKER.
