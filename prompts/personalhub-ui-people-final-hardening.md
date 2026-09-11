[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=694153 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

> Esecuzione diretta: questo file è il task Codex completo. Non eseguire `roadmap_guard.py select` e non rileggere roadmap/README/spiegazioni. Usa direttamente quanto segue come specifica autoritativa.

# Goal
Verificare/finalizzare i fix UI/People già in gran parte implementati sul remoto e rimuovere definitivamente dalle UI dei moduli i vecchi numeri versione ereditati da quando erano app standalone. **L'unico numero versione visibile deve restare quello autentico di PersonalHub nella Home principale.** Non rifare inventory generale: la root matrix è già verificata. Correggi solo residui/failure concrete, poi una build/install/QA finale.

# Stato remoto già implementato
Sul `main` corrente di `gernalix/PersonalHub` sono già presenti:

## Home / export
- `app/.../HomeAutoExportStatus.kt`: indicatore tappabile derivato esclusivamente da `DatabaseVault.autoExportStatus()`, con stato healthy/problem e dettaglio folder/generation/stale/last success/error;
- `HomeAutoExportStatusTest`: healthy + missing folder + stale + error + unavailable;
- `MainActivity.kt`: indicatore integrato accanto a Settings;
- la Home principale mostra già `BuildConfig.VERSION_NAME` del package host in basso a destra: **questa è l'unica versione che deve restare visibile**;
- stringhe EN+IT già aggiunte.

## Theme
- host `app/.../ui/theme/Theme.kt`: `isSystemInDarkTheme()` + light/dark;
- Timer `ui/theme/Theme.kt`: default `isSystemInDarkTheme()` usando gli schemi già esistenti;
- `feature/soldi/src/main/java/com/gernalix/personalhub/soldi/SoldiTheme.kt` è già stato aggiunto come boundary light/dark system-aware;
- `feature/soldi/src/main/java/com/gernalix/personalhub/soldi/SoldiActivity.kt` contiene ancora esattamente `setContent { MaterialTheme { Surface { SoldiScreen(capsule, ::finish, hubTransactionUuid) } } }`. Sostituiscilo direttamente con `setContent { SoldiTheme { Surface { SoldiScreen(capsule, ::finish, hubTransactionUuid) } } }`; `SoldiTheme` è nella stessa package, quindi non serve cercare un altro theme/import;
- People/Places/Substances/WordPulse erano già system-aware: non ri-auditarli salvo regressione concreta.

## Versioni legacy dei moduli — matrix già verificata
Questi numeri non sono più feature da allineare: sono residui di app standalone e **vanno rimossi dalla UI**, non spostati o sincronizzati.

Non rifare inventory oltre ai punti già localizzati:
- **Home PersonalHub**: conserva una sola visualizzazione `BuildConfig.VERSION_NAME` host, bottom-right;
- **Timer**: esiste ancora footer/version UI basata su `AppPatchVersion.current()` e label Info `R.string.versione_patch_v`; rimuovi le visualizzazioni/version label dalla UI Timer. Non sostituirle con la versione host;
- **Substances**: il footer mostra `BuildConfig.VERSION_NAME`; rimuovi solo la visualizzazione dalla UI;
- **Places**: `HomeScreen` contiene già l'item/footer versione; rimuovilo dalla UI invece di riallinearlo;
- **WordPulse**: `WordPulseScreen.Header` mostra `v${BuildConfig.VERSION_NAME}`; rimuovi questa visualizzazione e qualsiasi duplicato/footer versione della root WordPulse;
- **Soldi**: non aggiungere alcun footer versione; se esiste una visualizzazione versione nella root, rimuovila;
- **People**: `SuperContactsApp` carica ancora `assets/patch-version.txt` tramite `loadPatchVersion()` per mostrare `v$patchVersion`; elimina l'uso **visibile** di questa versione legacy. Se asset/helper servono ancora a compatibilità tecnica fuori dalla UI non fare cleanup non necessario.

Le versioni/build config interne dei feature module possono restare se servono alla build o ad altre logiche: il requisito è **nessun numero versione visibile dentro i moduli**. Non fare refactor Gradle solo per cancellare metadata non mostrati.

## People call overlay
`CallSystemOverlayController.kt` già:
- usa intent esplicito `MainActivity::class.java` preservando `ContactDeepLink` URI;
- usa `CallOverlayRequestGate` per invalidare lookup pendenti su dismiss/nuova call;
- non include più il numero di telefono nel log di show.
`CallOverlayRequestGateTest` copre dismiss→stale e nuova call→vecchia stale.

# Residui da fare
1. **Prima compila/testa i file già modificati**, senza nuova discovery:
   - `HomeAutoExportStatusTest`;
   - `CallOverlayRequestGateTest`;
   - compile/test mirati app + Timer + Places + WordPulse + Soldi + People solo per le modifiche già note.
   Correggi solo failure concrete.
2. Applica la sostituzione letterale `MaterialTheme`→`SoldiTheme` indicata sopra; non cercare alternative e nessun redesign.
3. Rimuovi tutte le visualizzazioni versione dalle root UI Timer, Substances, Places, WordPulse, Soldi e People usando esclusivamente i punti della matrix. **Non aggiungere nuovi footer/version label nei moduli.** Conserva soltanto `BuildConfig.VERSION_NAME` nella Home PersonalHub.
4. Test di intent esplicito/log redaction solo nei file People già indicati; non auditare manifest/repository salvo compile/test failure.

# Verification
Test mirati sopra + una sola build preliminare. Poi **un solo bump** `version.txt`, rebuild finale, install Pixel e una navigation QA consolidata: Home export status; una root rappresentativa di ogni modulo; light/dark; call-overlay disposable/strumentato.

Acceptance UI versione:
- Home PersonalHub: esattamente una versione autentica host visibile, bottom-right;
- Timer, Places, Substances, WordPulse, Soldi, People: **zero** numeri/version label visibili nelle rispettive root;
- nessuna stringa “Patch version”/equivalente visibile.

Niente redesign estetico/navigation/backup, niente broad suite, niente secondo giro di inventory. Telegram delivery, commit/push.

Su PASS, dopo il push del repo target, finalizza questo task nella roadmap con `python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 694153 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 694153`. `push_verified=git_push_exit_0` è prova sufficiente: non fare verifiche Git successive sulla roadmap e non aprire il task successivo. Su BLOCKED/FAIL non avanzare la roadmap. Stop immediato.

Output conciso: `PROMPT_ID`, `RESULT`, indicator, visible-version matrix, host+Timer+Soldi theme, overlay intent/race/privacy, test/device QA, version/APK/delivery, SHA, blocker.
