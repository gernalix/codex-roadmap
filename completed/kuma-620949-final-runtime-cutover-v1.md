PROMPT_ID=994029

# Goal
Chiudi SOLO il residuo runtime del goal 620949 dopo che tutti i blocker Git sono rientrati: distribuisci sul Fedora il main già mergiato di activity-watch-uploader senza producer Kuma proprietario, verifica che il job continui a funzionare, e prova che il monitoraggio centrale di fedora-system-monitor copra il job senza buco di osservabilità.

# Evidenza già verificata
- 620949 ha già classificato 31/31 repository, creato il registro centrale MegaVault e verificato i monitor centrali Fedora/Oracle.
- fedora-system-monitor è il controller Kuma canonico.
- github-autosync e codex-usage-monitor hanno già rimosso i producer Kuma legacy.
- ActivityWatch PR #3 è ora mergiata su main come commit b8ef359da6da83be2af64628a004abb27d9b39f1; la precedente CI non eseguiva test per un blocco GitHub Actions/fatturazione, non per test falliti.
- PersonalHub PR #39 e #40 sono entrambe mergiate.
- Non riaprire il broad audit di 620949 e non riconfigurare altri repository.

# Esecuzione minima
1. Claim 994029 e usa il worktree/checkout canonico indicato dal runtime.
2. Porta il checkout Fedora di activity-watch-uploader al main contenente b8ef359d con il percorso Git protetto corrente; preserva qualunque dirty non correlato.
3. Esegui una sola suite/test mirata del repo ActivityWatch e py_compile del codice coinvolto. Se fallisce, correggi solo un bug direttamente causato dal cutover Kuma.
4. Reinstalla/aggiorna solo le unità ActivityWatch esistenti e fai daemon-reload se necessario.
5. Verifica readback locale:
   - timer enabled+active;
   - service non failed;
   - unit/installazione non richiedono più KUMA_PUSH_URL, Secret Service o credential Kuma proprietarie;
   - un solo run controllato ActivityWatch termina con successo.
6. Verifica tramite il control plane fedora-system-monitor/Kuma già esistente che il target ActivityWatch centrale sia unico, attivo e fresco dopo il run. Non creare un secondo monitor.
7. Verifica che l'eventuale vecchio monitor/push producer ActivityWatch sia disabilitato/rimosso e che il monitor centrale resti UP/fresco. Nessun polling model-driven: un readback dopo il run è sufficiente.
8. Nessun audit repo-wide, nessun altro target Kuma, nessun refactor. Dopo PASS finalizza e STOP.

# Acceptance
PASS solo se ActivityWatch funziona col runtime aggiornato, non possiede più monitoring Kuma proprietario, il target centrale mostra freschezza coerente col run reale e non esiste un buco/duplicato di monitoraggio.

# Report
Massimo 7 righe: RESULT, DEPLOY, TESTS, ACTIVITYWATCH_RUN, CENTRAL_MONITOR, LEGACY_PRODUCER, BLOCKER.