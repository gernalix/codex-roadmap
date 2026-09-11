[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=694153 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Verificare/finalizzare i fix UI/People già in gran parte implementati sul remoto. **Non rifare l'inventory iniziale generale**: parti dai file e fatti elencati sotto, correggi solo residui/failure concrete, poi una build/install/QA finale.

# Stato remoto già implementato
Sul `main` corrente di `gernalix/PersonalHub` sono già presenti:

## Home / export
- `app/.../HomeAutoExportStatus.kt`: indicatore tappabile derivato esclusivamente da `DatabaseVault.autoExportStatus()`, con stato healthy/problem e dettaglio folder/generation/stale/last success/error;
- `HomeAutoExportStatusTest`: healthy + missing folder + stale + error + unavailable;
- `MainActivity.kt`: indicatore integrato accanto a Settings; footer Home continua a usare host `BuildConfig.VERSION_NAME`;
- stringhe EN+IT già aggiunte.

## Theme
- `app/.../ui/theme/Theme.kt`: host PersonalHub ora usa `isSystemInDarkTheme()` e schemi light/dark;
- Timer `ui/theme/Theme.kt`: default `darkTheme=isSystemInDarkTheme()` usando gli schemi Light/Dark già esistenti;
- People/Places/Substances/WordPulse erano già noti system-aware: non ri-auditarli salvo regressione concreta.

## Versione
- Substances `build.gradle.kts` già deriva `VERSION_CODE`/`VERSION_NAME` da root `version.txt`, quindi il suo footer `BuildConfig.VERSION_NAME` è già host-canonical: non rifarlo;
- Timer `AppPatchVersion.current()` è stato trasformato in compatibility wrapper che legge il `versionName` del package host. Il footer quindi mostra il valore PersonalHub; resta da eliminare solo eventuale **label testuale** che dica ancora “Patch version”.

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
   - test/compile mirati app + Timer/People.
   Correggi solo failure concrete.
2. **Soldi theme**: `SoldiActivity.kt` usa ancora `MaterialTheme { ... }` generico. Aggiungi il boundary system-aware minimo (light/dark), senza redesign.
3. **Version label Timer**: sostituisci l'eventuale testo “Patch version” con “Version”/traduzione; non reintrodurre patch-version asset come valore visibile.
4. **Footer matrix, una sola lettura mirata**: controlla esclusivamente le root full-page People/Timer/Places/Substances/Soldi/WordPulse. Ognuna deve mostrare una sola footer bottom-right con **host PersonalHub versionName**. Se una root non ha footer, aggiungi il minimo; se già conforme non toccarla. Non seguire schermate figlie.
5. Test di intent esplicito/log redaction solo nei file People già indicati; non auditare manifest/repository salvo compile/test failure.

# Verification
Test mirati sopra + una sola build. Poi **un solo bump** `version.txt`, rebuild finale, install Pixel e una navigation QA consolidata: Home export status; una root rappresentativa di ogni modulo; light/dark; call-overlay disposable/strumentato. Controlla contrasto/insets/FAB solo nella matrix finale.

Niente redesign estetico/navigation/backup, niente broad suite, niente secondo giro di inventory. Telegram delivery, commit/push, roadmap e STOP.

Output conciso: `PROMPT_ID`, `RESULT`, indicator, host version/footer matrix, host+Timer+Soldi theme, overlay intent/race/privacy, test/device QA, version/APK/delivery, SHA, blocker.
