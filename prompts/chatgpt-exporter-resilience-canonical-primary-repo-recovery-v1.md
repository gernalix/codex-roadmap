PROMPT_ID=812553
PARENT_PROMPT_ID=697920
REPO=gernalix/prompt-history
MEGAVAULT=STANDARD

# Goal
Completa SOLO il lavoro funzionale già definito nel parent 697920, correggendo il blocker di bootstrap: usa `gernalix/prompt-history` come unico repository primario della roadmap e NON passare alcun PROJECT_ID al repo-task. ChatGPTExporter è una integrazione/upstream secondaria, non parte del campo `repo`.

# Evidenza già verificata
- 697920 è canonically BLOCKED senza fix/replacement; fix-packet: il campo repo multiplo `gernalix/prompt-history + ChatGPTExporter fork` non identifica un worktree canonico e PROJECT_ID=92 risolve `github-autosync`.
- `gernalix/prompt-history` esiste, default branch `main`, push consentito e nessuna PR aperta rilevata.
- Non esiste oggi un repository `gernalix/ChatGPTExporter`.
- Il parent 697920 contiene già scope, non-goal, test e acceptance completi; i report 199166 sono l’evidenza iniziale autoritativa.

# Esecuzione minima
1. Claim SOLO 812553 con `roadmap_start.py`. Deve creare il worktree di `gernalix/prompt-history` per repo slug; se fallisce ancora l’isolamento, BLOCKED con l’errore preciso e STOP. Non riaprire 697920.
2. Leggi UNA volta il prompt canonico 697920 e usa integralmente i suoi acceptance criteria. Leggi solo i report 199166 e i file direttamente pertinenti; niente audit repo-wide e niente nuova scansione completa da 2.4 GB/7108 chat.
3. Esegui il lavoro del parent nel worktree assegnato. Se serve rendere durevoli modifiche a ChatGPTExporter, crea/usa un fork scrivibile `gernalix/ChatGPTExporter` separando `origin` e `upstream`; non aprire PR verso siraht e non cambiare i metadata roadmap durante il run.
4. Mantieni il parent come contratto per retry/resume, failure classes, asset recovery, audit/health, 12 inventory-only, provenance multi-fonte e runtime cutover. Non ampliare scope.
5. Aggiorna il pin/documentazione prompt-history SOLO dopo build/test PASS del fork. Nessun token/cookie/credenziale in file, log o output; nessun workaround che violi policy browser.
6. Test SOLO quelli mirati elencati nel parent; amplia solo se un failure concreto lo richiede. Runtime: solo revalidate/retry mirato dei residui, mai full recapture. Nessun retry identico senza nuova evidenza.
7. Se una azione manuale inevitabile resta (es. reload unpacked non automatizzabile), riportala come singolo prerequisito e BLOCKED; non inventare workaround.
8. Appena tutti gli acceptance criteria del parent sono verificati, finalizza 812553 e STOP.

# Acceptance
PASS solo se il claim parte con un worktree canonico prompt-history senza PROJECT_ID conflittuale, tutto il contratto funzionale di 697920 è soddisfatto, l’eventuale fork ChatGPTExporter è durevole e testato, il pin prompt-history punta alla revisione realmente verificata e nessun secret/export sorgente viene compromesso.

# Report
Massimo 10 righe: RESULT, WORKTREE, EXPORTER_FORK, EXPORTER_COMMIT, PROMPT_HISTORY_COMMIT, RETRY_ENGINE, FAILURE_CLASSES, AUDIT_HEALTH, RUNTIME_CUTOVER, BLOCKER.