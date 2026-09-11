[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=694153 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Chiudere in un solo pass finale i fix non-schema di UI/People, condividendo inventory schermate, build, install e device QA: auto-export status, versione host coerente, system light/dark e tre bug call-overlay People.

Assorbe `742618` + `925471`. Un solo bump versione e UNA build/install/navigation finale.

# Pass iniziale unico
Inventaria una volta Home + full-page destinations People/Timer/Places/Substances/Soldi/WordPulse. Riusa fatti noti: Home già usa host `BuildConfig.VERSION_NAME`; `DatabaseVault.autoExportStatus()` ha già i dati; People/Places/Substances/WordPulse seguono già system dark; Timer ha Light/Dark ma default light; Soldi usa MaterialTheme generico; Substances mostra feature BuildConfig; Timer mostra legacy patch version. Non ri-auditare temi già corretti salvo regression failure.

# A — Home/export + versione + theme
- Home: piccolo status tappabile ✅/❌ con semantic label, derivato solo da `DatabaseVault.autoExportStatus`; dettaglio config/last success/generation/stale/error. Nessun cambio backup/WorkManager.
- Versione visibile canonica = host PersonalHub `versionName`. Ogni full-page destination mostra una sola footer bottom-right; rimuovi Substances feature version e Timer patch version, niente duplicate/dialog footer.
- Host theme segue sistema; Timer seleziona scheme già esistenti via system default; Soldi aggiunge boundary system-aware minimo. Patch altro solo se la singola navigation matrix dimostra un difetto concreto. Verifica contrasto/insets/FAB e recreation state.

# B — People call overlay
Parti solo da `CallSystemOverlayController`, `CallStateReceiver`, People MainActivity/repository e app manifest.
- `openContact()` usa intent esplicito alla People MainActivity mantenendo URI `supercontacts://contact/<publicId>`; non esportare Activity per il fix.
- invalida pending async lookup su dismiss/nuova call, impedendo overlay stale o overwrite da request vecchia.
- elimina/redigi phone number dai log mantenendo solo metadata non sensibili.

Test mirati: export indicator states; una canonical host version per inventory; host+Timer+Soldi light/dark e regressione rappresentativa altri moduli; state recreation; explicit contact intent; delayed show→dismiss; two successive shows; log senza raw number.

Poi UNA build, Pixel install e UNA QA: Home + schermate rappresentative in light/dark + call-overlay disposable/strumentato. Telegram delivery, commit/push, roadmap, STOP. Nessun redesign estetico/navigation/backup.

Output: `PROMPT_ID`, `RESULT`, indicator/version/theme, overlay intent/race/privacy, test/device QA, version/APK/delivery, SHA, blocker.
