PROMPT_ID=896074

# Goal
Chiudi SOLO il residuo live della catena CCS 996591 dopo il deploy 302284, verificando launcher roadmap desktop-first e overlay/note per-thread sul Codex Desktop reale. Sostituisce 641903 perché il vecchio prompt hard-codava un project_id ormai non affidabile.

# Evidenza già verificata
- 641903 non è mai stato eseguito e non va lanciato.
- Il routing storico project_id=96 è ambiguo/stale: in evidenza recente risolve Workflowy, quindi non deve essere usato come costante.
- Repo canonico target: gernalix/chrome-codex-switcher.
- chrome-codex-switcher/main contiene già launcher desktop-first, binding overlay per thread attivo, note hydration e gli ultimi fix UI.
- 302284 distribuisce prima il runtime corrente di roadmap/Workflowy/codex-usage/CCS; questo task parte solo dopo il suo PASS.
- Non reimplementare 284653, 613408, 572554, 996591 o 641903.

# Esecuzione minima
1. Claim SOLO 896074 dopo 302284 PASS.
2. Usa repo/worktree assegnato e verifica una sola volta che il checkout contenga il main CCS corrente. Nessun audit repo-wide.
3. Prima dello smoke, risolvi il progetto Codex Desktop in modo autoritativo dalla coppia repo=gernalix/chrome-codex-switcher + metadata/runtime correnti. Non usare un project_id numerico hard-coded. Se esistono zero o più di un match coerente, termina BLOCKED con PROJECT_ROUTING_AMBIGUOUS e STOP.
4. Se Codex Desktop non è visibile via AT-SPI, BLOCKED con DESKTOP_REQUIRED. Nessun workaround Chrome/OCR/coordinate/uinput.
5. Launcher: da un task roadmap selezionabile fai UN solo smoke senza inviare il prompt. Verifica che venga scelto esattamente il progetto risolto al punto 3, che model/reasoning provengano dai metadata e che il composer contenga il prompt corretto.
6. Overlay: usa due thread Codex reali già disponibili e fai UN solo ciclo A -> B -> A. active_codex_thread, overlay e note devono seguire il thread attivo; durante transizioni/ambiguità il vecchio stato deve sparire.
7. Se entrambi PASS, non modificare codice. Se uno fallisce per un bug riproducibile del main corrente, correggi SOLO il componente responsabile, esegui il test mirato pertinente e ripeti una sola volta lo smoke fallito.
8. Finalizza una volta e STOP. Una finalizzazione accodata non è un nuovo blocker funzionale; un solo readback massimo, niente polling.

# Acceptance
PASS solo se il progetto CCS è risolto senza costante stale, launcher/composer selezionano project/model/reasoning/prompt corretti, A->B->A non riusa stato vecchio e i casi ambigui falliscono chiusi.

# Report
Massimo 8 righe: RESULT, PARENT_641903, MAIN_REVISION, PROJECT_RESOLUTION, DESKTOP, LAUNCHER_COMPOSER, A_B_A, BLOCKER.