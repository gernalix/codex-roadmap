PROMPT_ID=582408

# Goal
Completa il bootstrap del drain autonomo C2 dallo stato canonico corrente e consegna il controllo al runtime event-driven. Non eseguire manualmente i task applicativi e non mantenere questa sessione viva per aspettare la quiescenza.

# Starting point verificato
- Work item: wi:20c6161eec104b8c84f4b669a1e2d8b3.
- Il runtime scheduler (c2-runtime.timer + .path) è intenzionalmente fermo; c2-supervisor-watchdog.timer resta attivo.
- Il runtime worktree era stato riallineato a main e il guard risultava healthy.
- Sono già state preparate execution spec per vari task: riusale; non ricreare prompt/worktree/spec già presenti.
- Ultimo readback noto: cdab43... aveva prompt materializzato e una execution-spec mutation in flight; e2dd36... e a299a4... erano ancora da preparare. Questo è solo starting point: fai un singolo readback canonico e usa quello come autorità.
- Inbox #1350 segnala che roadmap_finish._queue_repo_integration tratta no-task-record come integrato per prompt Codex su codex-roadmap: correggi o rendi fail-closed questo caso prima di consentire PASS sicuri su quel repo.
- Non preparare né lanciare manual/conditional/external blockers (login Grindr/MitID, PAT, billing, PH-owned, device/user prerequisite). Non trattare state:step:* importati come worker autonomi.

# Esecuzione minima
1. Se non sei dentro un run C2 già claimed, esegui il normale claim/start canonico del PROMPT_ID; non duplicare claim/start esistenti.
2. Leggi una sola volta snapshot canonico, lease/authority, execution specs, active runs e unit state. Riusa ogni preparazione già applicata.
3. Completa solo le execution spec mancanti degli intake già verificati e senza blocker reale, usando tools/c2_prepare_codex.py; nessuna deduzione da titolo/prosa.
4. Correggi #1350 con patch minima e test mirati, oppure mantieni fail-closed i task codex-roadmap finché la prova di integrazione è corretta.
5. Assicurati che supervisor lease/authority e recovery pointer siano validi; nessun secondo supervisor concorrente.
6. Riallinea il runtime worktree al main corrente solo con il percorso canonico e verifica c2_worktree_guard.py = healthy.
7. Riattiva c2-runtime.timer e c2-runtime.path; lascia il watchdog attivo.
8. Verifica un solo ciclo reale schedule/launch, o equivalente readback deterministico, dimostrando: dipendenze rispettate, resource lock, parallelismo compatibile, nessun state:step lanciato e nessun PH worker toccato.
9. Registra checkpoint/evidence e termina. Non aspettare CI/merge/quiescenza con polling modello: dopo l'handoff, runtime/watchdog devono proseguire da soli.

# Acceptance
PASS solo se tutti gli acceptance criteria del work item canonico sono verificati, il runtime è event-driven e recuperabile, #1350 non permette finalizzazioni unsafe, e il lavoro futuro può avanzare senza questa sessione Codex.
