[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=694153 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

> Esecuzione diretta: questo file è il task Codex completo. Non eseguire `roadmap_guard.py select` e non rileggere roadmap/README/spiegazioni. Usa direttamente quanto segue come specifica autoritativa.

# Goal
Verificare/finalizzare i fix UI/People già in gran parte implementati sul remoto. **Non rifare inventory generale**: la root matrix è già stata verificata e i residui sono elencati sotto. Correggi solo residui/failure concrete, poi una build/install/QA finale.

# Stato remoto già implementato
Sul `main` corrente di `gernalix/PersonalHub` sono già presenti:

## Home / export
- `app/.../HomeAutoExportStatus.kt`: indicatore tappabile derivato esclusivamente da `DatabaseVault.autoExportStatus()`, con stato healthy/problem e dettaglio folder/generation/stale/last success/error;
- `HomeAutoExportStatusTest`: healthy + missing folder + stale + error + unavailable;
- `MainActivity.kt`: indicatore integrato accanto a Settings; footer Home usa host `BuildConfig.VERSION_NAME`;
- stringhe EN+IT già aggiunte.

## Theme
- host `app/.../ui/theme/Theme.kt`: `isSystemInDarkTheme()` + light/dark;
- Timer `ui/theme/Theme.kt`: default `isSystemInDarkTheme()` usando gli schemi già esistenti;
- `feature/soldi/src/main/java/com/gernalix/personalhub/soldi/SoldiTheme.kt` è già stato aggiunto come boundary light/dark system-aware;
- `feature/soldi/src/main/java/com/gernalix/personalhub/soldi/SoldiActivity.kt` contiene ancora esattamente `setContent { MaterialTheme { Surface { SoldiScreen(capsule, ::finish, hubTransactionUuid) } } }`. Sostituiscilo direttamente con `setContent { SoldiTheme { Surface { SoldiScreen(capsule, ::finish, hubTransactionUuid) } } }`; `SoldiTheme` è nella stessa package, quindi non serve cercare un altro theme/import;
- People/Places/Substances/WordPulse erano già system-aware: non ri-auditarli salvo regressione concreta.

## Versione — matrix già verificata
Non rifare questa inventory:
- **Home**: già `BuildConfig.VERSION_NAME` host, footer bottom-right;
- **Timer**: `AppPatchVersion.current()` ora legge `versionName` del package host; footer esiste. Resta solo la label Info `R.string.versione_patch_v` ancora descritta come “Patch version”;
- **Substances**: `build.gradle.kts` già deriva `VERSION_CODE`/`VERSION_NAME` da root `version.txt`; footer usa `BuildConfig.VERSION_NAME`, quindi valore già canonico;
- **Places**: `AppPatchVersion.current()` ora legge il package host. `HomeScreen` ha già item `footer`, ma il testo non è allineato bottom-right: rendi solo quel footer right-aligned, preservando il resto del contenuto/folder label;
- **WordPulse**: `build.gradle.kts` ora deriva `BuildConfig.VERSION_NAME` da root `version.txt`; `WordPulseScreen.Header` mostra ancora `v${BuildConfig.VERSION_NAME}` **in alto**, non come footer. Sposta/rendi una sola visualizzazione bottom-right e rimuovi la duplicazione in header;
- **Soldi**: `build.gradle.kts` ora deriva `BuildConfig.VERSION_NAME` da root `version.txt` e abilita BuildConfig, ma `SoldiScreen` non mostra ancora footer: aggiungi una sola footer bottom-right;
- **People**: `SuperContactsApp` continua a caricare `assets/patch-version.txt` via `loadPatchVersion()` e mostra `v$patchVersion`; `feature/supercontacts/build.gradle.kts` ha ancora versioni feature hardcoded. Non sincronizzare manualmente l'asset. Modifica il path minimo affinché il valore visibile derivi dal package host `versionName` (come Timer/Places), quindi elimina l'uso visibile dell'asset legacy. Il footer esistente va reso bottom-right se non lo è già.

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
3. Applica i cinque micro-fix versione già descritti nella matrix: Timer label; Places alignment; WordPulse posizione/unicità; Soldi footer; People host version + alignment. Non ispezionare schermate figlie.
4. Test di intent esplicito/log redaction solo nei file People già indicati; non auditare manifest/repository salvo compile/test failure.

# Verification
Test mirati sopra + una sola build preliminare. Poi **un solo bump** `version.txt`, rebuild finale, install Pixel e una navigation QA consolidata: Home export status; una root rappresentativa di ogni modulo; light/dark; call-overlay disposable/strumentato. Verifica una sola versione visibile bottom-right per root e nessuna “patch version” legacy.

Niente redesign estetico/navigation/backup, niente broad suite, niente secondo giro di inventory. Telegram delivery, commit/push.

Su PASS, dopo il push del repo target, finalizza questo task nella roadmap con `python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 694153 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 694153`. `push_verified=git_push_exit_0` è prova sufficiente: non fare verifiche Git successive sulla roadmap e non aprire il task successivo. Su BLOCKED/FAIL non avanzare la roadmap. Stop immediato.

Output conciso: `PROMPT_ID`, `RESULT`, indicator, host version/footer matrix, host+Timer+Soldi theme, overlay intent/race/privacy, test/device QA, version/APK/delivery, SHA, blocker.
