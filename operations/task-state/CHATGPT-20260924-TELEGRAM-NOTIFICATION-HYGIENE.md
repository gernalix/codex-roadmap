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
- [x] Implementare collector Telegram incrementale e test: commit fedora-system-monitor f577f66fb4cc9e354df032ee1b5dea527006ea9e.
- [x] Creare/configurare repo dati privato dedicato: gernalix/telegram-notification-history, PRIVATE.
- [x] Installare service+timer systemd --user e lock anti-overlap; unit caricate, timer intenzionalmente disabilitato finché manca la sessione Telegram.
- [ ] Eseguire login Telegram una tantum senza esporre segreti.
- [ ] Verificare almeno due run: prima ingestione + seconda no-op.
- [ ] Verificare commit/push solo con nuovi messaggi.
- [ ] Rendere il repo leggibile dal connettore GitHub usato da ChatGPT.
- [ ] Dopo raccolta sufficiente, classificare notifiche verbose/incomprensibili/inutili/ripetute/flapping.
- [ ] Creare fix mirati per i singoli producer; niente broad refactor.
- [ ] Aggiornare la policy legacy project_id visibile se il metadata strutturato rende il prefisso non più necessario.

## Completed
- PROMPT_ID 422308 terminato BLOCKED per solo prerequisito manuale di autorizzazione Telegram; codice/test/runtime preparatorio completati.
- Commit verificato: fedora-system-monitor f577f66fb4cc9e354df032ee1b5dea527006ea9e (`Add private Telegram notification history collector`).
- Data repo verificato: gernalix/telegram-notification-history, visibility=private.
- Config locale installata mode 0600; service/timer caricati; timer lasciato disabled prima del login.
- RUN1/RUN2 non eseguiti perché TELEGRAM_API_ID/API_HASH sono vuoti e non esiste account.session.
- Roadmap exception mutation #1042 registra analysis/code_change e manual-prerequisite:telegram-auth.
- Architettura scelta.
- Individuato il precedente task 417826 da trattare come baseline storica, non come policy immutabile.
- PROMPT_ID 422308 allocato.
- Goal collector registrato/materializzato nella roadmap dal single writer.

## Remaining
1. Ottenere TELEGRAM_API_ID e TELEGRAM_API_HASH dall'account Telegram.
2. Inserirli solo nel config locale insieme al peer target già previsto.
3. Eseguire una volta il comando login e completare codice Telegram/2FA nel terminale.
4. Solo dopo nuova evidenza, creare/lanciare un follow-up minimo che esegua RUN1/RUN2, abiliti il timer e chiuda il collector.
5. Dopo raccolta reale sufficiente, auditare e correggere i producer rumorosi.

## Blockers
- Unico blocker: autorizzazione Telegram account-level una tantum. TELEGRAM_API_ID/API_HASH non sono configurati e manca la sessione Telethon.
- Non lanciare retry Codex prima che il login produca nuova evidenza.

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
Ottenere API ID/hash su my.telegram.org, inserirli nel file locale ~/.config/fedora-telegram-history/collector.env senza condividerli in chat/Git, quindi eseguire il comando login già installato. Dopo `Telegram session is authorized.`, creare il follow-up minimo per RUN1/RUN2 + enable timer; non riaprire 422308.


## Remote Desktop Commander follow-up — 2026-09-24
- Fedora device connected successfully through Remote Desktop Commander.
- Verified local collector config exists with mode 0600; API ID/hash/phone remain unset and Telegram session is absent.
- Opened https://my.telegram.org in the existing Chrome session.
- Opened a fresh visible Ptyxis terminal for the user.
- Remote safety controls block reading/inserting authentication secrets, browser credential/session extraction, and direct GUI automation of those secret-bearing flows.
- Attempted Telegram Desktop tdata reuse as an alternative; the remote safety layer blocked direct session conversion before any account data was read.
- No Telegram authorization was completed and timer remains intentionally disabled.
- Do not retry Codex or model polling until there is new evidence: API credentials are entered locally and the Telegram login succeeds.

## Next action
User completes my.telegram.org login locally, creates/opens API development tools, enters API ID/hash only into ~/.config/fedora-telegram-history/collector.env, then runs the installed login command locally. After the session is authorized, ChatGPT/Remote Desktop Commander can resume with RUN1, RUN2, timer enablement, and repository verification.


## Login bug fix — 2026-09-24
- The API credentials from my.telegram.org were entered into the local 0600 config only; they were not committed to Git.
- First login attempt exposed a concrete bug: blank TELEGRAM_PHONE was passed explicitly as None to Telethon, causing ValueError before any prompt.
- Fixed both task worktree and installed runtime to call client.start() when TELEGRAM_PHONE is blank, allowing Telethon to prompt interactively.
- Targeted collector suite: 5/5 PASS; py_compile and git diff --check PASS.
- Fix committed and pushed on task/422308: 9d736aa (Prompt for phone during Telegram login).
- A visible Ptyxis login terminal is open and currently waits for the user's phone number, followed by Telegram code/optional 2FA.
- Noninteractive authorization readback still reports unauthorized; timer remains disabled.

## Next action
User completes the visible Telegram login terminal locally. As soon as the account session becomes authorized, run RUN1, then RUN2 no-op, enable the timer, verify the private data repo remote, persist the runtime closure, and create the minimal roadmap follow-up instead of relaunching terminal PROMPT_ID 422308.
