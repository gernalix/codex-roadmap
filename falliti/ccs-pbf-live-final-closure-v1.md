PROMPT_ID=996591
PARENT_PROMPT_ID=572554
PROJECT_ID=96
MEGAVAULT=FAST
REPO=gernalix/chrome-codex-switcher

# Goal
Chiudere definitivamente la catena PBF 284653 -> 613408 -> 572554 verificando sul Codex Desktop reale i due soli contratti ancora non conclusi: launcher roadmap desktop-first e overlay/note legati al thread Codex attivo. Riusa il codice corrente; non reimplementare ciò che è già su main.

# Evidenza già verificata
- project_id canonico di chrome-codex-switcher / Facilitatori di prompt = 96.
- main contiene già il binding overlay per thread attivo e il fix del watcher AT-SPI (commit recenti dfd0d6c e b432fd3), oltre al launcher desktop-first.
- 572554 era un recovery; il residuo è soprattutto una prova live conclusiva. Non fare discovery generale o audit repo-wide.

# Esecuzione minima
1. Claim canonico e usa il worktree assegnato.
2. Porta il worktree alla main corrente con un solo aggiornamento sicuro; niente reset/stash/cleanup di lavoro altrui.
3. Verifica una sola volta che Codex Desktop sia raggiungibile via AT-SPI e che project_id 96 risolva il progetto corretto.
4. Launcher: esercita il percorso reale senza inviare il prompt. Deve selezionare progetto, modello e reasoning richiesti dai metadata del task scelto, inserire il prompt corretto nel composer e fallire chiuso se progetto/thread/composer sono ambigui. Vietati clipboard, coordinate, OCR/image matching e workaround Chrome come prova finale.
5. Overlay: usa due thread Codex reali già disponibili e fai un solo A->B->A. active_codex_thread, overlay e note devono seguire il thread realmente attivo; durante transizioni/ambiguità l'overlay deve restare nascosto, senza riusare stato vecchio.
6. Se uno smoke fallisce, modifica solo il componente responsabile, aggiungi/aggiorna il test mirato e ripeti una sola volta quello smoke. Niente refactor, cleanup o nuove feature.
7. Esegui la suite repo solo se hai modificato codice; altrimenti bastano i test mirati già pertinenti e le due prove live.
8. Su PASS finalizza 996591. Non riaprire né rieseguire 284653, 613408 o 572554.

# Acceptance
PASS solo se launcher e overlay funzionano sul Desktop reale, project_id 96 è corretto, il composer contiene il prompt giusto senza invio automatico, A->B->A non riusa stato stale e i casi ambigui falliscono chiusi.

# Stop
Dopo PASS esegui roadmap_finish.py per 996591 e termina. Output massimo 8 righe: RESULT, DESKTOP, PROJECT, LAUNCHER, COMPOSER, A_B_A, TESTS, BLOCKER.