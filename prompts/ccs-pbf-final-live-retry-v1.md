PROMPT_ID=641903
PARENT_PROMPT_ID=996591
PROJECT_ID=96
REPO=gernalix/chrome-codex-switcher
MEGAVAULT=FAST

# Goal
Chiudi SOLO il leaf PBF 996591 verificando sul Codex Desktop reale i due contratti già implementati: launcher roadmap desktop-first e overlay/note legati al thread attivo. Non riaprire 284653, 613408 o 572554 e non rifare implementazioni già presenti su main.

# Evidenza già verificata
- 996591 è canonically BLOCKED, senza fix/follow-up; nessuna modifica codice registrata.
- Il suo fix-packet riporta come blocker soltanto `finalizzazione 996591 BLOCKED accodata (issue #938)`; Issue #938 è ora chiusa e applicata dal single writer.
- 284653, 613408 e 572554 hanno già relazione fix verso 996591: questo nuovo leaf deve coprire ricorsivamente la stessa catena, senza creare fix separati.
- Work-state di 996591: `b432fd3`. chrome-codex-switcher/main è avanzato a `00963e3f31939d936b614c36db1fde57a872e4c7`, che include anche il successivo fix di note hydration; non risultano PR aperte.
- project_id canonico CCS/Facilitatori di prompt = 96.

# Esecuzione minima
1. Claim SOLO 641903 con `roadmap_start.py`; usa il worktree assegnato. Niente audit repo-wide, history scan o nuova discovery architetturale.
2. Verifica UNA volta che il worktree contenga main corrente o un successore di `00963e3`; non fare reset/stash/cleanup distruttivi.
3. Se Codex Desktop non è visibile via AT-SPI, termina subito BLOCKED con `DESKTOP_REQUIRED`; nessun workaround Chrome, OCR, coordinate, clipboard o uinput.
4. Launcher: esegui UN solo smoke reale senza inviare il prompt. Da un task roadmap selezionabile verifica exact project=96, modello/reasoning dai metadata e prompt corretto nel composer. Ambiguità di progetto/thread/composer deve fallire chiusa.
5. Overlay: usa due thread Codex reali già disponibili e fai UN solo ciclo A -> B -> A. `active_codex_thread`, overlay e note devono seguire il thread attivo; durante transizione/ambiguità il vecchio stato deve sparire, mai essere ereditato.
6. Se entrambi PASS, NON modificare codice. Se uno fallisce per un difetto riproducibile del main corrente, modifica SOLO il componente responsabile, esegui il test mirato pertinente e ripeti UNA volta solo lo smoke fallito. Niente refactor/cleanup/feature collaterali. Suite repo completa solo se hai modificato codice.
7. Appena launcher + composer + A->B->A + fail-closed sono verificati, finalizza 641903 una sola volta. Una mutation di finalizzazione semplicemente accodata non è un nuovo blocker funzionale: non trasformare di nuovo un PASS live in BLOCKED solo perché il single writer deve ancora applicarla. Fai al massimo UN readback della mutation e STOP.

# Acceptance
PASS solo se Desktop reale è disponibile, project_id 96 è corretto, launcher seleziona esattamente project/model/reasoning, il composer contiene il prompt giusto senza invio, A->B->A non riusa stato stale e i casi ambigui falliscono chiusi.

# Report
Massimo 8 righe: RESULT, PARENT_996591, MAIN_REVISION, DESKTOP, LAUNCHER_COMPOSER, A_B_A, TESTS, BLOCKER.