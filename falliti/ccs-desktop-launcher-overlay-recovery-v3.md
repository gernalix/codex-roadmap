PROMPT_ID=572554
PARENT_PROMPT_ID=613408
ROADMAP_PROJECT=Facilitatori di prompt
PROJECT_ID=96
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=FAST
REPO=gernalix/chrome-codex-switcher

# Goal
Riprendi esclusivamente dal BLOCKED 613408 e completa sul ChatGPT/Codex Desktop reale:
A) il consumer AT-SPI desktop-first del launcher roadmap;
B) la verifica live che overlay/note seguano il thread Codex attivo senza stato stale.

# Evidenza già verificata da 613408
- Codex Desktop è visibile via AT-SPI: NON ripetere discovery generica.
- Il task precedente si è fermato prima di selezionare progetto/modello/reasoning perché PROJECT_ID=23 era errato.
- PROJECT_ID canonico di chrome-codex-switcher / Facilitatori di prompt = 96.
- Composer non è stato modificato o inviato; binding e A→B→A non sono stati eseguiti.
- Nessuna modifica codice è stata fatta da 613408.

# Starting point da riusare
- Launcher spec/deep-link/binding esistono già: completa solo il consumer operativo che seleziona progetto, modello, reasoning e inserisce il prompt senza inviarlo.
- Il fix overlay per-thread è già su main: serve soprattutto la prova A→B→A sul Desktop reale.
- Non rifare audit, bootstrap, history o fix già verdi.

# Esecuzione minima
1. Claim 572554 e usa il worktree assegnato.
2. Usa PROJECT_ID=96. Verifica una sola volta che risolva chrome-codex-switcher/Facilitatori di prompt; mismatch => BLOCKED con evidenza precisa.
3. Launcher: seleziona progetto/repo, modello Sol/Terra/Luna e reasoning richiesti dal prompt; inserisci prompt_text nel composer via AT-SPI; verifica round-trip; NON inviare. Binding/titolo PROMPT_ID devono fallire chiusi se ambigui.
4. Overlay: usa due thread reali già associati e fai un solo A→B→A; active_codex_thread e overlay devono seguire il thread reale. Durante transizione, thread ambiguo o non associato, l'overlay deve restare nascosto.
5. Vietati clipboard, uinput, coordinate, OCR/image matching e workaround Chrome come prova finale.
6. Se un punto fallisce, modifica solo il componente responsabile, aggiungi il test mirato e ripeti una sola volta quello smoke. Niente refactor o cleanup.
7. Suite repo solo se hai modificato codice. Stop immediato appena entrambi i contratti sono verificati.

# Acceptance
PASS solo se launcher e overlay funzionano sul Desktop reale, PROJECT_ID=96 risolve il progetto corretto, progetto/modello/reasoning e composer sono corretti, il prompt non viene inviato automaticamente, A→B→A non riusa stato vecchio e i casi ambigui falliscono chiusi.

# Roadmap
Su PASS roadmap_finish.py per 572554; su blocker realmente esterno roadmap_result.py. Dopo terminalizzazione: STOP.

Output max 9 righe: PROMPT_ID, RESULT, DESKTOP, PROJECT_MODEL_REASONING, COMPOSER, BINDING, A_B_A, TESTS, BLOCKER.