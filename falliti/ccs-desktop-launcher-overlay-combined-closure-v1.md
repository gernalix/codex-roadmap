PROMPT_ID=284653
MERGED_FROM=764529,784216
ROADMAP_PROJECT=Facilitatori di prompt
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=FAST
REPO=gernalix/chrome-codex-switcher

# Goal
Con ChatGPT/Codex Desktop realmente aperto, chiudi in UN solo passaggio i due residui CCS già noti:
A) completa il consumer AT-SPI desktop-first del launcher roadmap;
B) valida live che overlay/note seguano il thread Codex attivo senza stato stale.
Non rifare audit, bootstrap o fix già verificati su main.

# Evidenza da riusare
- 764529: launcher spec/deep-link/binding esistono già; manca il consumer operativo che seleziona progetto, modello e reasoning e inserisce il prompt senza inviarlo.
- 784216/125435: il fix overlay per-thread è già su main (baseline b432fd3 o successore); la prova A→B→A era bloccata solo perché Desktop non era presente.
- Entrambi richiedono la stessa UI Desktop/AT-SPI e lo stesso repo: fai una sola discovery e un solo deploy quando possibile.

# Scope stretto
1. Claim SOLO 284653 e usa solo il worktree assegnato.
2. Verifica UNA volta che ChatGPT/Codex Desktop sia visibile via AT-SPI. Se assente: BLOCKED con DESKTOP_REQUIRED; nessun retry/workaround Chrome.
3. Sincronizza/verifica una volta la baseline main; niente history audit.
4. Launcher:
   - seleziona progetto/repo esatto;
   - seleziona modello esatto Sol/Terra/Luna e reasoning esatto;
   - inserisci prompt_text nel composer via AT-SPI, verifica round-trip e NON inviare;
   - completa binding/titolo PROMPT_ID fail-closed;
   - vietati clipboard, uinput, coordinate e image matching.
5. Overlay:
   - riusa due thread reali già associati;
   - esegui un solo ciclo A→B→A;
   - verifica active_codex_thread/fonte/overlay a ogni switch;
   - durante transizione nessun overlay vecchio; thread ambiguo/non associato => overlay nascosto.
6. Se il launcher o l’overlay falliscono, modifica SOLO il componente direttamente responsabile, aggiungi test mirato e ripeti una sola volta il relativo smoke.
7. Esegui test mirati; una suite repo solo se hai modificato codice. Nessun refactor/cleanup.
8. STOP immediato quando entrambi i contratti sono verificati.

# Acceptance
PASS solo se launcher e overlay sono entrambi provati su Desktop reale, fail-closed nei casi ambigui, prompt non inviato automaticamente, e nessun lavoro fuori scope è stato introdotto.

# Report
Max 9 righe: PROMPT_ID, RESULT, DESKTOP, PROJECT_MODEL_REASONING, COMPOSER, BINDING, A_B_A, TESTS, BLOCKER.