PROMPT_ID=781426
PARENT_PROMPT_ID=327684
ROADMAP_PROJECT=minsp-export
MODEL=GPT-5.6 Sol
REASONING=medium
MEGAVAULT=FAST
REPO=gernalix/minsp-export

# Goal
Riprendi il goal completo di 682741 dopo il bootstrap Git e dopo che l'utente ha completato MitID nel profilo Chrome persistente. Usa il normale single-writer e porta l'export reale a PASS senza rifare l'architettura già implementata.

# Stato già verificato
- 682741 è stato bloccato prima del lavoro applicativo per assenza della baseline Git remota.
- 327684 crea la prima baseline sicura su origin/main.
- L'unica azione umana ammessa resta il login MitID.
- Riusa il prompt/goal e l'implementazione esistenti di 682741; non riscrivere il progetto.

# Esecuzione
1. Claim 781426 e usa solo il worktree assegnato.
2. Verifica una sola volta che la sessione Min Sundhedsplatform sia autenticata nel profilo persistente. Se no: BLOCKED immediato con LOGIN_MITID_REQUIRED; nessun bypass/retry.
3. Recupera il goal canonico di 682741 e completa SOLO ciò che manca, riusando test/checkpoint già presenti.
4. Inventaria le sezioni leggibili reali, colma i gap minimi e completa l'export read-only.
5. Preserva raw/JSON/PDF/allegati localmente fuori Git, normalizza in health.sqlite, FTS5/search e Markdown come previsto dal parent.
6. Prova checkpoint/resume una volta e tracciabilità raw -> normalized -> search/Markdown.
7. Nessuna mutazione account; nessuna credenziale o dato sanitario in Git.
8. Test mirati, poi solo i gate finali necessari. STOP al PASS.

# Report
Max 10 righe: PROMPT_ID, RESULT, PROJECT_ID, COVERAGE, RAW, NORMALIZED, RESUME, SEARCH, TESTS, BLOCKER.