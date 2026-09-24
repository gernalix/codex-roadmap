# TASK_ID=CHATGPT-20260924-TELEGRAM-NOTIFICATION-HYGIENE

## Objective
Automatizzare la raccolta della chat Telegram usata per le notifiche tecniche e usarla come evidenza per ridurre rumore, duplicati, messaggi incomprensibili e flapping senza richiedere export manuali all'utente.

## Constraints
- Fedora user service/timer, nessun processo model-driven sempre acceso.
- Archivio Git privato; nessun token, session file, API hash, chat secret o credenziale nel repository.
- Export incrementale e resumable; nessun commit/push se non ci sono nuovi messaggi.
- Collector separato da telegram_insert_bot.
- Testi futuri comprensibili a un non tecnico, brevi, autoesplicativi, con emoji e formattazione Telegram.
- Stesso incidente invariato non deve notificare ripetutamente; recovery utile una volta sola dopo un alert realmente inviato.
- Non cambiare trigger/frequenze storicamente dichiarati come eccezioni (es. quota Codex/spazio disco) finché l'evidenza nuova non giustifica esplicitamente una revisione.
- Il project_id non deve essere necessario come prefisso tecnico visibile se può essere conservato come metadata strutturato nell'archivio/audit.

## Verified facts
- Esiste un precedente task completato di Telegram signal hygiene (PROMPT_ID 417826) con deduplica parziale e regola legacy project_id visibile.
- telegram_insert_bot è un repo applicativo distinto; non è il posto giusto per il collector passivo.
- L'ecosistema usa già systemd --user e repo Git privati per dati/runtime.
- Un export affidabile della chat richiede un client Telegram account-level (es. Telethon) oppure una sorgente equivalente; Bot API da sola non è una fonte generale della cronologia dei messaggi inviati dal bot.

## Decisions
- Creare un collector dedicato che legge solo la chat del bot notifiche, non tutte le chat Telegram.
- Autorizzazione Telegram una tantum; poi esecuzione unattended.
- Dati canonici in JSONL append-only con message_id, timestamp, testo/caption, sender/peer minimale ed eventuale metadata media; niente download media salvo necessità.
- Repo dati privato dedicato, scritto solo dal sync service.
- Timer consigliato: 15 minuti; commit/push solo se ci sono nuove entry.
- L'audit successivo deve modificare i produttori reali, non filtrare le notifiche a valle.

## Checklist
- [ ] Allocare un PROMPT_ID canonico per il task locale.
- [ ] Registrare il goal nella roadmap via single writer.
- [ ] Implementare collector Telegram incrementale e test.
- [ ] Creare/configurare repo dati privato dedicato.
- [ ] Installare service+timer systemd --user e lock anti-overlap.
- [ ] Eseguire login Telegram una tantum senza esporre segreti.
- [ ] Verificare almeno due run: prima ingestione + seconda no-op.
- [ ] Verificare commit/push solo con nuovi messaggi.
- [ ] Rendere il repo leggibile dal connettore GitHub usato da ChatGPT.
- [ ] Dopo raccolta sufficiente, classificare notifiche verbose/incomprensibili/inutili/ripetute/flapping.
- [ ] Creare fix mirati per i singoli producer; niente broad refactor.
- [ ] Aggiornare la policy legacy project_id visibile se il metadata strutturato rende il prefisso non più necessario.

## Completed
- Architettura scelta.
- Individuato il precedente task 417826 da trattare come baseline storica, non come policy immutabile.

## Remaining
Tutto il deployment locale e l'audit sui messaggi reali.

## Blockers
- Possibile login Telegram/2FA iniziale manuale; deve essere un solo prerequisito, non un loop Codex.
- Il repo dati dedicato non esiste ancora.

## Evidence
- codex-roadmap/completed/telegram-notification-signal-hygiene.md
- codex-roadmap/AGENTS.md e SQLITE_ROADMAP.md per lifecycle/roadmap writer.

## Acceptance criteria
PASS della fase collector quando il servizio legge solo la chat target, persiste nuove entry senza duplicati, non espone segreti, il timer è enabled+active, una seconda run senza nuovi messaggi è no-op e il repo privato remoto contiene l'archivio aggiornato.

## Next action
Allocare il PROMPT_ID canonico e registrare il goal collector nella roadmap.
