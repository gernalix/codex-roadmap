PROMPT_ID=946527
ROADMAP_PROJECT=Fedora / Workflowy
MODEL=GPT-5.5
REASONING=low
MEGAVAULT=FAST

# Goal
Distribuisci sul Fedora reale il fix già completato su gernalix/workflowy-importer/main che ripulisce la categoria Workflowy "Needs fix", poi verifica la dashboard live.

# Evidenza già verificata
- Fix codice: commit 346b0e79e84ae2314286711b0892e36ee2b19a86.
- Test/allineamento: commit 2f5ceae6c2894c35e333cb6c3270c5a4afffc816.
- GitHub Actions CI run #100: PASS su Python 3.11 e 3.13.
- Nuova semantica: un BLOCKED/FAIL storico oppure con fix/replacement/followup attivo o completato va in Archive; Needs fix resta solo per failure leaf realmente irrisolti.

# Scope stretto
1. Claim canonico con roadmap_start.py.
2. Usa il checkout canonico ~/projects/workflowy-importer e il normale meccanismo single-writer/autosync già previsto dal sistema. Non creare PR/branch e non fare audit repo-wide.
3. Porta il checkout a main contenente almeno 2f5ceae6c2894c35e333cb6c3270c5a4afffc816.
4. Esegui solo il deploy runtime canonico:
   python3 deploy_runtime.py
   Questo deve riavviare workflowy-bridge e avviare workflowy-roadmap-sync.service.
5. Verifica:
   - systemctl --user --no-pager --full status workflowy-bridge.service workflowy-roadmap-sync.service workflowy-roadmap-sync.timer
   - esegui/leggi un solo sync della roadmap se necessario;
   - controlla la dashboard Workflowy live.
6. Acceptance dashboard:
   - i vecchi BLOCKED/FAIL con successore attivo/PASS non sono più in Needs fix ma in Archive;
   - gli historical stub senza prompt materializzato non sono in Needs fix;
   - Needs fix contiene esclusivamente eventuali failure leaf realmente irrisolti;
   - con lo stato canonico osservato al momento della verifica, se non esistono nuovi failure reali, Needs fix deve essere 0.
7. Se compare un vero nuovo failure corrente, NON nasconderlo: riportalo come blocker reale.
8. Non modificare codice salvo una regressione introdotta esattamente da questo deploy; niente cleanup/refactor.

# Stop
Appena deploy + verifica live PASS, roadmap_result PASS e STOP. Nessun audit ulteriore.

# Report
Max 7 righe:
PROMPT_ID
RESULT
DEPLOYED_COMMIT
SERVICES
ROADMAP_SYNC
NEEDS_FIX_COUNT
BLOCKER
