PROMPT_ID=784216 | PARENT_PROMPT_ID=125435 | project_id=23
MODEL=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
REPO=gernalix/chrome-codex-switcher

# Goal
Chiudi SOLO il blocker di 125435 eseguendo la validazione live dell'overlay per-thread quando ChatGPT/Codex Desktop è realmente presente. Non rifare il fix già su main e non toccare launcher/Workflowy/roadmap oltre alla finalizzazione.

# Evidenza già verificata
- 125435 è canonically BLOCKED senza fix/replacement; fix-packet: Fedora esponeva solo Chrome, non una finestra Codex Desktop reale.
- chrome-codex-switcher/main HEAD è `b432fd3eb2b86db2daa68985c6b7ccf2dec5c0b8`; contiene il fix per-thread, preceduto da `dfd0d6c0f558b2d57dc77bbfa56cb27bc276bf7`.
- Il parent si è fermato sul prerequisito runtime prima di poter dimostrare A -> B -> A; non serve nuova implementazione salvo failure reale della prova.

# Esecuzione minima
1. Claim SOLO 784216. Verifica UNA volta che ChatGPT/Codex Desktop sia visibile via AT-SPI. Se non lo è, BLOCKED immediato con `DESKTOP_REQUIRED`; nessun retry e nessun workaround via Chrome.
2. Verifica solo che il checkout/runtime includa `b432fd3` o un successore; distribuisci con il meccanismo già previsto solo se il runtime non è aggiornato.
3. Riusa due thread Codex reali già associati. Esegui un solo ciclo UI/sidebar A -> B -> A.
4. Dopo ogni switch verifica soltanto: `active_codex_thread`, fonte di risoluzione, overlay/note del thread attivo; durante la transizione il vecchio thread deve sparire prima della nuova risoluzione.
5. Verifica un caso non associato/ambiguo: overlay nascosto, mai ereditato dal thread precedente. Vietati OCR, image matching, coordinate, uinput e clipboard come prova identità.
6. Se tutto PASS, NON modificare codice. Se fallisce, applica SOLO il minimo fix nel watcher/resolver direttamente coinvolto, un regression test mirato e ripeti UNA volta A -> B -> A.
7. Finalizza 784216 e STOP appena gli acceptance criteria sono verificati.

# Acceptance
PASS solo se Desktop reale è presente, A -> B -> A segue correttamente il thread e l'overlay senza stato stale, i casi ambigui/non associati falliscono chiuso e nessuna modifica fuori scope viene eseguita.

# Report
Massimo 7 righe: RESULT, PARENT_125435, DESKTOP, REVISION, A_B_A, FAIL_CLOSED, BLOCKER.