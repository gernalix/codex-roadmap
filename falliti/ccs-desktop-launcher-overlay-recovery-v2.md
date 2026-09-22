PROMPT_ID=613408
PARENT_PROMPT_ID=284653
ROADMAP_PROJECT=Facilitatori di prompt
PROJECT_ID=23
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=FAST
REPO=gernalix/chrome-codex-switcher

# Goal
Riprendi il BLOCKED 284653 senza rifare il lavoro precedente e chiudi in un solo passaggio i due residui CCS sul ChatGPT/Codex Desktop reale:
A) consumer AT-SPI desktop-first del launcher roadmap;
B) prova live che overlay/note seguano il thread Codex attivo senza stato stale.

# Starting point da riusare
- Il launcher spec/deep-link/binding esistono già: completa solo il consumer operativo che seleziona progetto, modello, reasoning e inserisce il prompt senza inviarlo.
- Il fix overlay per-thread è già su main: serve soprattutto la prova A→B→A sul Desktop reale.
- Non rifare audit, bootstrap, history o fix già verdi.

# Esecuzione minima
1. Claim 613408 e usa il worktree assegnato.
2. Verifica una sola volta il Desktop via AT-SPI e parti dai componenti già indicati dal lavoro 284653.
3. Launcher: seleziona progetto/repo, modello Sol/Terra/Luna e reasoning richiesti dal prompt; inserisci prompt_text nel composer via AT-SPI; verifica round-trip; NON inviare. Binding/titolo PROMPT_ID devono fallire chiusi se ambigui.
4. Overlay: usa due thread reali già associati e fai un solo A→B→A; active_codex_thread e overlay devono seguire il thread reale. Durante transizione, thread ambiguo o non associato, l'overlay deve restare nascosto.
5. Vietati clipboard, uinput, coordinate, OCR/image matching e workaround Chrome come prova finale.
6. Se un punto fallisce, modifica solo il componente responsabile, aggiungi il test mirato e ripeti una sola volta quello smoke. Niente refactor o cleanup.
7. Suite repo solo se hai modificato codice. Stop immediato appena entrambi i contratti sono verificati.

# Acceptance
PASS solo se launcher e overlay funzionano sul Desktop reale, progetto/modello/reasoning e composer sono corretti, il prompt non viene inviato automaticamente, A→B→A non riusa stato vecchio e i casi ambigui falliscono chiusi.

# Roadmap
Su PASS roadmap_finish.py per 613408; su blocker realmente esterno roadmap_result.py. Dopo terminalizzazione: STOP.

Output max 9 righe: PROMPT_ID, RESULT, DESKTOP, PROJECT_MODEL_REASONING, COMPOSER, BINDING, A_B_A, TESTS, BLOCKER.