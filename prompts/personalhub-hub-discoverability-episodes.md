[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=838979 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=1/4 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Rendere comprensibili e richiamabili le utility Hub di PersonalHub senza cambiare il modello dati: chiarire Context/Search/Activity nella UI, mostrare le sessioni Timer in Context con titolo/tag leggibili, e rendere gli episodi salvati realmente ritrovabili e riapribili.

# Starting point verificato
Usa `.codex/CODE_MAP.tsv` come router e apri SOLO i path pertinenti. In chat è già stato verificato che:
- Home instrada `Context` -> `HubContextComposerScreen`, `Search` -> `HubTemporalSearchScreen`, `Activity` -> `HubActivityRegisterScreen`;
- Search salva un “episode” chiamando `HubContextRuntime.createContext(..., title=episodeTitle)`: non esiste un tipo persistence separato per gli episodi;
- `TimerSessionHubAdapter` usa oggi il titolo sessione e, se vuoto, un fallback basato sull'id; i tag non entrano nel summary;
- non esiste una superficie globale chiara per elencare/richiamare tutti i context titolati salvati come episodi;
- la media fatigue mostrata da Search è un segnale 0–100 personalizzato, non una percentuale clinica.
Path iniziali: `app/src/main/java/com/gernalix/personalhub/MainActivity.kt`, `app/src/main/java/com/gernalix/personalhub/HubTemporalSearchScreen.kt`, `app/src/main/java/com/gernalix/personalhub/HubActivityRegisterScreen.kt`, `core/hub-context/.../HubContextRuntime.kt`, `HubContextRepository.kt`, `HubContextComposer.kt`, `feature/multitimetracker/.../hub/TimerSessionHubAdapter.kt`, WordPulse solo per riusare wording/calcolo già esistente. Niente repo-wide audit.

# Implementazione minima
1. Home: rendi autoesplicative Context/Search/Activity con etichette/sottotitoli/help brevi, senza ridisegnare Home. Semantica da comunicare: Context=collega entità tra moduli; Search=cerca eventi/entità in un intervallo; Activity=registro modifiche/undo.
2. Timer in Context/Search: il label primario delle sessioni deve essere umano. Regola: titolo non vuoto + tag risolti quando presenti; se titolo vuoto usa i nomi tag; se anche i tag mancano usa un fallback localizzato tipo “Sessione senza titolo” con data/ora utile. MAI id DB/UUID come testo primario visibile. Gli id restano solo interni.
3. Episodi: aggiungi da Search una superficie `Episodi salvati` che elenca i context con `title` non vuoto, ordinati dal più recente. Deve mostrare titolo + riassunto membri leggibile e permettere di riaprire/modificare lo stesso context. Riusa tabelle/DAO esistenti; NON aggiungere schema/migrazione. Nessun nuovo concetto persistence “episode”.
4. Fatigue: dove Search mostra la fatigue media, aggiungi help conciso: 0–100 relativo al baseline personale, più alto = maggiore deviazione fatigue-like; nessuna banda clinica fissa. Non cambiare algoritmo/pesi.
5. Mantieni deep link, undo Activity e behavior Context esistenti. Se un dettaglio collaterale è brutto ma non blocca questi acceptance criteria, segnalalo e non investigarlo.

# Verifica mirata
- aggiungi/aggiorna test unitari solo per label Timer e query/lista episodi;
- test Compose/instrumented mirato: Context non espone raw session id come label primario; un episodio titolato salvato da Search compare in `Episodi salvati` e si riapre con gli stessi membri; help fatigue presente;
- esegui `checkArchitectureBoundaries` solo se tocchi wiring/public integration boundary;
- un solo build debug finale dopo i leaf test PASS. Niente full suite, benchmark, Pixel/TCL, Perfetto o audit generale.

# Campagna / release
Fase intermedia: NON incrementare `version.txt`, NON installare sul Pixel e NON inviare APK/Telegram. Push sul branch canonico remoto una sola volta dopo PASS. La release consolidata è nella fase 4.

# Acceptance
PASS se le tre utility sono autoesplicative, le sessioni Timer sono leggibili senza raw id, gli episodi titolati sono elencabili e riapribili, il fatigue score è spiegato senza cambiare algoritmo, test mirati + build PASS.

# Stop
Acquisisci/rilascia il lease PH secondo `AGENTS.md`. Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 838979 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 838979`

Dopo `status=completed` + `push_verified=git_push_exit_0` fermati. Output massimo 6 righe.