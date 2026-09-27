PROMPT_ID=856999

# Obiettivo
Aggiungi a github-autosync un gate canonico/idempotente per i task roadmap-backed che richiedono acceptance obbligatorie dopo il merge.

# Problema verificato
- start-roadmap salva roadmap_prompt_id=<task_id>.
- pending_roadmap_completions() include ogni task roadmap-backed appena status=merged e senza roadmap_completion_queued_at.
- repo-integrator chiama quindi automaticamente roadmap_finish PASS.
- PROMPT_ID 742579 richiede esplicitamente: code merge -> backup/migrazione/verifica DB live -> solo allora PASS C2.
- Senza gate, 742579 verrebbe terminalizzato prima dell'acceptance.

# Implementazione
1. Estendi il task record con uno stato esplicito di deferral dell'auto-completion roadmap, default OFF.
2. Aggiungi CLI canonici idempotenti, ad esempio:
   - defer-roadmap-completion --task-id ID [--reason ...]
   - release-roadmap-completion --task-id ID
   Naming equivalente ammesso se più coerente col repo.
3. Il defer è valido solo per task realmente roadmap-backed (roadmap_prompt_id == task_id), fail-closed altrimenti.
4. pending_roadmap_completions() deve ignorare task deferred anche se merged.
5. release deve rimuovere il defer senza falsificare roadmap_completion_queued_at; dopo release il task merged torna eleggibile all'auto-PASS.
6. status-any deve rendere visibile il defer/reason in modo leggibile.
7. Idempotenza: defer ripetuto coerente e release ripetuto non corrompono stato.
8. Nessun cambiamento al default dei task normali.
9. Test mirati repo_single_writer + repo_integrator/autosync completion flow.
10. Commit/push/integra secondo protocollo del repo e termina dopo merge/PASS.

# Acceptance concreta
Dopo il merge, il supervisor deve poter eseguire:
- defer su 742579 PRIMA che il task applicativo venga merged;
- integrare 742579 normalmente;
- osservare status=merged ma nessun auto roadmap completion;
- dopo acceptance live, release e finalizzare normalmente.

PROMPT_ID verrà fornito dal C2 lifecycle. Nessun lavoro sui repo Grindr in questo leaf.
