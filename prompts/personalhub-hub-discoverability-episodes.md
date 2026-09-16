[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=838979 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=1/4 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Rendere comprensibili e richiamabili le utility Hub di PersonalHub senza cambiare schema: chiarire Context/Search/Activity, mostrare le sessioni Timer con titolo/tag leggibili e rendere gli episodi titolati elencabili/riapribili.

# Routing verificato — niente discovery
Usa `.codex/CODE_MAP.tsv` e apri SOLO le righe `app.shell`, `hub.context`, `hub.temporal_search`, `timer.sessions`. Per il fatigue usa direttamente `docs/HUB_USER_GUIDE.md`: NON riaprire l'algoritmo WordPulse salvo errore di compilazione/test che lo richieda.
Facts già verificati:
- Search salva gli episodi come normali Hub context con `title`, senza persistence separata;
- manca una lista globale dei context titolati;
- `TimerSessionHubAdapter` oggi non include i tag nel summary e può ricadere su un label con id;
- Activity/deep-link/undo esistono già e non vanno ridisegnati.

# Implementazione minima
1. Home: etichette/help brevi che chiariscano Context=collega entità, Search=ricerca per intervallo, Activity=registro modifiche/undo. Nessun redesign Home.
2. Timer summary: titolo + nomi tag quando presenti; se titolo vuoto usa i tag; se entrambi vuoti fallback localizzato umano con data/ora utile. MAI DB id/UUID come label primario.
3. Search: aggiungi `Episodi salvati` riusando context/DAO esistenti, solo `title` non vuoto, newest-first, titolo + membri leggibili, riapertura/modifica dello stesso context. Nessuna migrazione e nessun nuovo tipo `Episode`.
4. Fatigue: help conciso coerente con `docs/HUB_USER_GUIDE.md`; non cambiare pesi/algoritmo.
5. Mantieni invariati deep link, Activity undo e semantica Context. Problemi collaterali non bloccanti: segnala e STOP.

# Verifica host-only
Questa fase NON avvia emulatore/device. La QA UI strumentale di fase 1 viene accorpata alla fase 2, che deve già avviare Pixel_8a emulator.
- aggiungi/aggiorna unit test mirati per Timer label e query/lista episodi;
- esegui solo quei leaf test;
- `checkArchitectureBoundaries` solo se il diff cambia wiring/public integration;
- chiudi con UNA compilazione `:app:compileDebugKotlin` (o leaf compile equivalente sufficiente), non `assembleDebug` e non full suite.

# Campagna
Fase intermedia: niente bump `version.txt`, Pixel reale, APK/Telegram. Push una volta dopo PASS. La fase 2 eseguirà in un'unica sessione emulator la UI QA necessaria per fase 1 + fase 2.

# Acceptance
PASS host-side se codice/test mirati/compile dimostrano: utility autoesplicative, Timer label umano, query episodi riapribili e wording fatigue corretto. La verifica visuale/device è esplicitamente deferred alla fase 2.

# Stop
Acquisisci/rilascia il lease PH secondo `AGENTS.md`. Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 838979 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 838979`

Dopo `status=completed` + `push_verified=git_push_exit_0` fermati. Output massimo 6 righe.