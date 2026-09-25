PROMPT_ID=851204 | PARENT_PROMPT_ID=175908 | project_id=42 | MegaVault=STANDARD

# Goal
Monitorare e bonificare radicalmente il bot Telegram “Datasette Alerts” (@datasette_alerts_bot) affinché ogni notifica ricevuta sia utile, comprensibile e proporzionata, eliminando rumore, duplicati e raffiche senza perdere alert realmente importanti.

# Starting point verificato
- Il bot “Datasette Alerts” è il token TELEGRAM_INSERT_BOT_NOISY_BOT_TOKEN del repo /home/daniele/projects/telegram_insert_bot.
- word_monitor.py usa quel token/chat e oggi supporta batching/backoff, ma va auditato insieme a qualunque altro producer reale dello stesso token.
- Questo task parte SOLO dopo 107210 PASS.

# Esecuzione
1. Inventaria deterministicamente tutti i producer del noisy token e le classi di messaggi; niente token nei log.
2. Raccogli un campione bounded delle notifiche recenti da fonti locali/runtime/Telegram disponibili senza esportare conversazioni private inutili. Misura frequenza, duplicati, raffiche e messaggi non interpretabili.
3. Definisci una tassonomia semplice: info utile, warning azionabile, errore urgente, reminder; ogni messaggio deve dire cosa è successo, perché importa e cosa fare (se serve). Elimina dettagli tecnici non necessari all’utente.
4. Implementa policy centralizzata per deduplica, grouping, rate-limit, cooldown, severità e silenziamento degli eventi normali/no-op. Eventi ripetuti devono diventare un riepilogo, non N notifiche.
5. Riscrivi i template di ogni producer rilevante in italiano chiaro. Mantieni link/azioni solo se utili. Niente ID interni/raw SQL/trace salvo opzione diagnostica non notificata.
6. Aggiungi test dei template/policy e fixture per burst/dedup/rate-limit; verifica che gli alert critici non vengano soppressi.
7. Deploy sul runtime reale, poi canary/live smoke con messaggi di test chiaramente marcati; verifica consegna e leggibilità.
8. Aggiungi monitoraggio passivo non-model del volume del bot e contatori per suppressed/grouped/sent, senza loggare contenuti sensibili. Se il volume torna anomalo, crea evidenza operativa invece di tempestare Telegram.
9. Invia notifica C2 comprensibile a ogni milestone significativa completata, tramite il canale C2 canonico, non tramite Datasette Alerts stesso se ciò falserebbe il test.

# Acceptance
PASS solo se tutti i producer sono noti; policy unica e testata; duplicati/burst vengono aggregati; no-op non notificano; messaggi live sono comprensibili e azionabili; alert importanti restano visibili; volume/metriche sono monitorabili; test+deploy+canary PASS; nessun segreto esposto.
