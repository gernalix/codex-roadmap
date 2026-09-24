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
- PROMPT_ID canonico allocato: 422308.
- Mutation roadmap di registrazione applicata: codex-roadmap Issue #1026.
- Prompt materializzato dal writer in prompts/telegram-notification-history-fedora-collector-v1.md.

## Decisions
- Creare un collector dedicato che legge solo la chat del bot notifiche, non tutte le chat Telegram.
- Autorizzazione Telegram una tantum; poi esecuzione unattended.
- Dati canonici in JSONL append-only con message_id, timestamp, testo/caption, sender/peer minimale ed eventuale metadata media; niente download media salvo necessità.
- Repo dati privato dedicato, scritto solo dal sync service.
- Timer consigliato: 15 minuti; commit/push solo se ci sono nuove entry.
- L'audit successivo deve modificare i produttori reali, non filtrare le notifiche a valle.
- Codice/runtime del collector assegnato a gernalix/fedora-system-monitor; data sink dedicato previsto: gernalix/telegram-notification-history.

## Checklist
- [x] Allocare un PROMPT_ID canonico per il task locale: 422308.
- [x] Registrare il goal nella roadmap via single writer.
- [x] Materializzare 422308 nel registry MegaVault: Issue #99 chiusa con status=materialized.
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
- PROMPT_ID 422308 allocato.
- Goal collector registrato/materializzato nella roadmap dal single writer.

## Remaining
Deployment locale, creazione data repo e audit sui messaggi reali.

## Blockers
- Possibile login Telegram/2FA iniziale manuale; deve essere un solo prerequisito, non un loop Codex.
- Il repo dati dedicato non esiste ancora.

## Evidence
- codex-roadmap/completed/telegram-notification-signal-hygiene.md
- codex-roadmap/prompts/telegram-notification-history-fedora-collector-v1.md
- MegaVault Issue #96 => PROMPT_ID=422308, status=allocated.
- codex-roadmap Issue #1026 => Applied by the roadmap single writer.
- MegaVault Issue #99 => PROMPT_ID=422308, status=materialized.
- codex-roadmap/AGENTS.md e SQLITE_ROADMAP.md per lifecycle/roadmap writer.

## Acceptance criteria
PASS della fase collector quando il servizio legge solo la chat target, persiste nuove entry senza duplicati, non espone segreti, il timer è enabled+active, una seconda run senza nuovi messaggi è no-op e il repo privato remoto contiene l'archivio aggiornato.

## Next action
Lanciare PROMPT_ID 422308 in Codex; se il runtime richiede login/2FA Telegram, completare la singola autorizzazione manuale e poi riprendere dal checkpoint senza rifare test già PASS.
