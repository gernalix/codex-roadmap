PROMPT_ID=377172

Aggiorna SOLO la documentazione dell'architettura callback Grindr già deployata.

Correggi README di telegram_insert_bot e, solo se il repo/worktree assegnato consente il relativo aggiornamento senza violare ownership, il riferimento corrispondente a grindr-favorites-monitor. La verità runtime è: callback gf:* accodati su Oracle; Fedora li preleva/esegue via SSH; callback timer circa 15s. Non cambiare comportamento o codice runtime.

Acceptance:
- wording obsoleto del local handler Oracle rimosso;
- architettura queue/worker Fedora↔Oracle descritta correttamente e compatta;
- diff-check PASS;
- commit+push del solo scope documentale; report finale conciso.
