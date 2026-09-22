PROMPT_ID=764529
PARENT_PROMPT_ID=403496
ROADMAP_PROJECT=Facilitatori di prompt
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=FAST
REPO=gernalix/chrome-codex-switcher

# Goal
Completa il consumer AT-SPI desktop-first rimasto da 403496 quando ChatGPT/Codex Desktop è disponibile nella sessione grafica. Non rifare il bootstrap roadmap né l'audit già svolto.

# Stato già verificato
- Il branch mismatch del parent è stato superato.
- 403496 si è fermato solo perché Codex Desktop non era presente e quindi non poteva fare consumer AT-SPI + smoke E2E.
- main ha già launch spec, pending_desktop_launch, desktop_launch_requested e apertura codex://threads/new.
- Manca il consumer operativo: progetto/repo esatto, modello Sol/Terra/Luna esatto, reasoning esatto, prompt completo nel composer NON inviato, lifecycle/title binding fail-closed.

# Scope stretto
1. Claim 764529 e riusa la stessa chat di 403496.
2. Verifica una sola volta che ChatGPT/Codex Desktop sia visibile ad AT-SPI. Se non lo è, BLOCKED con DESKTOP_REQUIRED; nessun retry.
3. Ispeziona solo i controlli accessibili indispensabili della UI corrente.
4. Implementa il consumer minimo nel daemon/host esistente; nessun nuovo servizio salvo necessità tecnica provata.
5. Vietati clipboard, uinput, coordinate, image matching e Chrome ChatGPT.
6. Exact-match/fail-closed per progetto, modello e reasoning; nessun fallback ambiguo.
7. Inserisci prompt_text via AT-SPI, verifica round-trip, lascia composer focalizzato e NON inviare.
8. Associa/arma il titolo PROMPT_ID come previsto dal contratto esistente.
9. Test mirati, poi una sola suite repo; un solo smoke reale non distruttivo.
10. STOP al PASS; niente refactor o audit ulteriore.

# Report
Max 8 righe: PROMPT_ID, RESULT, DESKTOP, PROJECT, MODEL_REASONING, COMPOSER, TESTS, BLOCKER.