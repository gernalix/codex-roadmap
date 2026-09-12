[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=694153 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | campaign_id=PH_FINAL_20260912`

> Esecuzione diretta. Non usare `select` e non rileggere roadmap/README/spiegazioni. Fase 3/4 della campagna: **niente bump versione/final APK/Pixel main/Telegram**.

# Goal
Chiudere i residui UI/People già localizzati e rimuovere tutti i numeri versione legacy dentro i moduli. Nessuna inventory generale.

# Starting point verificato
- Home: `HomeAutoExportStatus` già implementato/testato; conserva l'unica vera `BuildConfig.VERSION_NAME` host in basso a destra.
- Theme host/Timer system-aware. `SoldiTheme` esiste; in `SoldiActivity` sostituisci il wrapper root `MaterialTheme` con `SoldiTheme` se non già fatto.
- People call overlay ha già intent esplicito, request gate e log redaction; verifica i test esistenti, non ri-auditare manifest/repository senza failure.

# Versioni legacy da rimuovere
Usa solo questi punti già localizzati:
- Timer: footer/version UI basata su `AppPatchVersion.current()` / `versione_patch_v`;
- Substances: footer `BuildConfig.VERSION_NAME`;
- Places: version item/footer in `HomeScreen`;
- WordPulse: header `v${BuildConfig.VERSION_NAME}` e eventuale duplicato root;
- Soldi: nessuna versione deve essere visibile nella root;
- People: uso visibile di `patch-version.txt`/`loadPatchVersion()`.

Non cancellare metadata/helper tecnici se servono fuori UI. Requisito: **Home PersonalHub = 1 versione host; ogni root modulo = 0 versioni**.

# Verification fase
Prima test mirati `HomeAutoExportStatusTest`, `CallOverlayRequestGateTest` e compile delle root toccate. Poi QA isolata rapida su Home + una root per modulo + light/dark; overlay solo se il test locale non basta. Niente broad suite, niente package reale Pixel.

Commit/push PersonalHub al PASS; **non modificare `version.txt`**, non costruire/consegnare final APK.

Su PASS completa solo `PROMPT_ID=694153`; `push_verified=git_push_exit_0` è terminale.

Output ≤6 righe: RESULT, version matrix, Soldi/theme, People overlay tests, QA isolata, SHA/blocker.
