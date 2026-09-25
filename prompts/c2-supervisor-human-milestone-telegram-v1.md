PROMPT_ID=238170 | PARENT_PROMPT_ID=175908 | project_id=104 | MegaVault=FAST

# Goal
Rendi strutturale nel chatgpt-rdc-supervisor la policy Telegram della Checklist 2.0: una notifica umana e comprensibile per ogni milestone significativa completata, non per micro-step.

# Starting point
- /home/daniele/.local/bin/c2-notify esiste già e usa il bot Telegram principale, non Datasette Alerts.
- 107210 usa già milestone manuali C2; questo task deve generalizzare il comportamento nel supervisor futuro.
- Non toccare PersonalHub né il P0.

# Implementazione
1. Introduci un evento/milestone C2 persistente e idempotente: stessa milestone/work_item non può notificare due volte dopo restart/recovery.
2. Template italiano breve: cosa è stato completato, risultato concreto per l’utente, prossimo passo. Nessun dump tecnico, stack trace, SHA o log salvo se indispensabile alla comprensione.
3. Notifica solo transizioni significative: gate/test principale PASS, artifact pronto, deploy/install completato, blocker che richiede azione umana, task/goal completato. Non notificare singoli comandi, retry, heartbeat o polling.
4. Usa il canale/helper C2 canonico e il bot principale. Datasette Alerts non deve essere usato per C2. Fail-safe: un errore Telegram non deve cambiare falsamente lo stato del work item; conserva pending delivery per retry bounded/event-driven.
5. Integra con scheduler/recovery del supervisor in modo compatibile con il futuro work_items DB; fino al cutover supporta gli eventi roadmap esistenti senza creare una seconda source of truth.
6. Testa dedup, restart recovery, template comprensibile, failed-send retry e assenza di micro-step spam.

# Acceptance
PASS se una fixture C2 con più micro-eventi e 3 milestone produce esattamente 3 notifiche umane, un restart non duplica invii, un failed send viene ritentato senza alterare lifecycle, Datasette Alerts non viene usato e i test mirati PASS.

Dopo PASS finalizza e STOP.