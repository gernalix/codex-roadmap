PROMPT_ID=989559
PROJECT=Facilitatori di prompt
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=FAST
REPO=gernalix/chrome-codex-switcher

# Goal
Completa il launcher desktop-first della dashboard Workflowy: 🚀 Avvia deve preparare una nuova thread Codex in ChatGPT Desktop nel progetto/repo corretto, con modello Sol/Terra/Luna e reasoning esatti dalla roadmap, titolo PROMPT_ID e prompt canonico già nel composer ma NON inviato. Non usare Work né chat ChatGPT normali e non aprire nuove tab ChatGPT in Chrome.

# Starting point autoritativo
- `chrome-codex-switcher` main contiene già il contratto desktop-first: il daemon riceve dal bridge `project_id/project_name/repo/model/reasoning/prompt_text`, salva `pending_desktop_launch`, emette `desktop_launch_requested` e apre `codex://threads/new`.
- Commit principali già su main: `620f0a5f9b34341c0cf052feec5f1a7ab95f61a1`, `70e795b8344f2c5b479549c1c8c2636734d113b7`, `5b9b22e090fd8185cb81b778dba499386766d5bd`, `97059050cbd8492de85b12c560de2cdf23b09898`, `6e2af59ccdb0dcfd30c947e484af1bd30046003f`, docs `8bc21c91ccf2d72d29d86abd0899cbfd7792dfc6`.
- `workflowy-importer` commit `ea60d70726fdac95ba2129d2f69f60c7d8eeb2ea` espone già i metadati canonici al daemon: non rifare quel lavoro.
- Esistono già `CodexA11yWatch`, GNOME companion e AT-SPI. Riusa questa infrastruttura; manca il consumer operativo del launch spec.

# Scope
1. Prima di qualunque lettura/modifica esegui il claim con `roadmap_start.py --prompt-id 989559`; usa il worktree restituito come checkout autoritativo.
2. Ispeziona SOLO il subtree AT-SPI necessario della ChatGPT/Codex Desktop reale per identificare i controlli correnti: nuova thread/progetto, model picker, reasoning picker, composer e rename. Niente esplorazione generale.
3. Implementa il consumer minimo di `pending_desktop_launch` / `desktop_launch_requested`, preferibilmente nel daemon/host esistente senza nuovo servizio se non strettamente necessario.
4. Dopo `codex://threads/new`, porta Codex Desktop in primo piano e seleziona in modo verificabile:
   - progetto/workspace/repo canonico dalla launch spec;
   - modello ESATTO richiesto tra Sol/Terra/Luna;
   - reasoning ESATTO richiesto.
   Normalizza solo alias ortografici noti (`gpt-5.6-terra` ↔ `GPT-5.6 Terra` ecc.); non scegliere fallback o match ambiguo.
5. Inserisci l'intero `prompt_text` nel composer tramite interfaccia accessibile/AT-SPI, verifica round-trip del testo e lascia il composer focalizzato. NON premere Enter e NON inviare il prompt.
6. Non usare clipboard, `/dev/uinput`, xdotool/ydotool, coordinate, image matching o una tab Chrome ChatGPT. Le azioni Chrome esistenti restano separate.
7. Il titolo deve diventare esattamente il PROMPT_ID. Se una thread vuota non è rinominabile, arma il rename: dopo il primo invio manuale rileva in modo bounded la nuova sessione nativa tramite l'esatto PROMPT_ID, associa automaticamente il `codex://threads/<id>` senza Ctrl+Alt+L e rinomina la conversazione a `989559` via UI accessibile. Non modificare DB/file privati di ChatGPT.
8. Persisti uno stato launch leggibile (`requested/prepared/blocked/bound` o equivalente) con errore concreto. Se progetto/modello/reasoning/composer non sono verificabili esattamente, fail closed e non alterare silenziosamente altre impostazioni.
9. Aggiungi test mirati per parsing/normalizzazione, exact-match/fail-closed, nessuna dipendenza Chrome/clipboard e lifecycle del launch. Esegui prima i test mirati, poi una sola suite repo finale.
10. Fai un solo smoke sul Fedora reale che provi almeno: apertura/focus Codex Desktop, selezione esatta progetto+modello+reasoning, testo esatto nel composer NON inviato e nessuna nuova tab ChatGPT Chrome. Ripulisci il composer dello smoke senza inviare. Verifica rename/binding con test deterministici se un invio reale sarebbe necessario.

# Acceptance
PASS solo se 🚀 Avvia non crea ChatGPT Chrome; Codex Desktop va in primo piano; progetto/repo, modello e reasoning canonici sono selezionati e verificati esattamente; prompt canonico è nel composer senza invio; nessun clipboard/uinput/coordinate; fallback impliciti impossibili; thread risultante viene associata automaticamente al PROMPT_ID e rinominata a PROMPT_ID quando materializzata; test repo PASS e smoke reale PASS per i gate non distruttivi.

# Non-goal
Niente Work, chat ChatGPT normale, redesign della dashboard, refactor generale AT-SPI/GNOME, cambi a workflowy-importer già risolti, cleanup collaterale o audit post-PASS.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 989559 --confirm-executed`
Poi stop. Output finale conciso: RESULT, DESKTOP, PROJECT, MODEL_REASONING, COMPOSER, TITLE_BINDING, TESTS, COMMIT, BLOCKER.
