PROMPT_ID=861305 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STANDARD

# Goal
Completa SOLO il Data Explorer ibrido di PersonalHub già preparato: rendi Datasette Lite realmente offline nell'APK, verifica local/remote su Android e integra il branch in main senza indebolire i boundary di sicurezza.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`, project_id `49`;
- branch: `feature/hybrid-datasette-explorer`;
- HEAD remoto atteso del branch: `88fa81aa7974b21535629586a91e714fcff016a6`;
- base iniziale main: `7cf69218b5956c13e70194fe1801804c4143e4fc`;
- il branch contiene già: snapshot DB detached+validato, DataExplorerActivity local/remote, home entry, WebViewAssetLoader, config `personalhub_read`, strings, docs e CODE_MAP;
- local mode è intenzionalmente fail-closed e blocca ogni richiesta fuori da `appassets.androidplatform.net`;
- il sync token Android NON deve mai essere usato dal Data Explorer remoto;
- il DB Room live NON deve mai essere servito: solo lo snapshot cache;
- `version.txt` è ancora 47: fai il bump +1 UNA sola volta solo quando il feature gate è pronto per l'artefatto finale.

# Esecuzione minima
1. Acquisisci il task lock PH con PROMPT_ID 861305. In un solo preflight: verifica branch/worktree, fetch branch+main, richiedi branch remoto all'HEAD atteso; se main è avanzato, integra SOLO se fast-forward/rebase-free e senza conflitti con i file del feature, altrimenti BLOCKED. Non esplorare il repo: usa `.codex/CODE_MAP.tsv` row `database.data_explorer`.
2. Prima modifica: esegui consumer preflight solo per le API pubbliche cambiate se applicabile, quindi compile mirato. Correggi esclusivamente errori del feature.
3. Vendorizza/pinna Datasette Lite + Pyodide + wheel/assets strettamente necessari sotto il packaging previsto da `docs/DATA_EXPLORER.md` (o helper deterministico equivalente già nel repo). Nessuna CDN/runtime fetch. Mantieni il network block locale: NON allentarlo per far partire Pyodide.
4. Aggiungi solo i test necessari a provare:
   - snapshot coerente e validato, mai file Room/WAL live;
   - snapshot/cache non accessibile fuori dal path dedicato;
   - local mode avvia Datasette Lite e una SELECT con rete disabilitata;
   - navigazione tabella/SQL read-only funziona;
   - tentativi write non modificano `personalhub.db`;
   - remote mode usa `personalhub_read` e autenticazione interattiva, senza header/token mobile.
5. Gate host economici: compile leaf interessato, test mirati, poi una sola `checkArchitectureBoundaries`. Se un gate aggregato fallisce, usa solo il leaf failure e un unico rerun finale.
6. QA emulator con il facade canonico `python3 tools/android_emulator_control.py start|wait|stop`, solo `Pixel_8a`:
   - avvio Home → Dati;
   - con networking del target disabilitato, local Datasette Lite apre snapshot e SELECT reale;
   - riabilita rete solo per il test remote e verifica browse/query autenticato sul `personalhub_read` già distribuito dal task 527184; se il server task non è PASS, remote QA può essere BLOCKED ma NON sostituire auth/token;
   - nessun crash/logcat error del feature, back navigation corretta, chiusura elimina snapshot cache.
7. Misura una sola volta l'incremento dimensione APK dovuto agli asset e riportalo; non avviare una campagna di minificazione/refactor salvo superamento di un limite reale di build/delivery.
8. Solo dopo tutti i gate feature PASS: incrementa `version.txt` 47→48 una volta, costruisci il debug canonico firmato una volta, integra/pusha `main` senza merge ambiguo, installa QUELLO stesso APK sul Pixel fisico con `python3 tools/android_pixel_apk.py install` e usa la delivery canonica PH. Non ricostruire dopo il gate finale.
9. Rilascia il task lock in ogni esito. PASS => stop immediato.

# Acceptance
PASS solo se Datasette Lite funziona realmente offline senza fetch esterni, usa soltanto snapshot read-only, remote explorer usa auth umana e non il token sync, write bypass impossibile nei test, architecture/tests/QA PASS, main contiene il feature, versione 48 è costruita una sola volta e lo stesso APK finale è installato/consegnato secondo le regole PH.

# Non-goal
Niente riscrittura Datasette in Kotlin, sync bidirezionale server→PH, SQL write arbitrario, nuovo database canonico, redesign UI dei moduli, plugin opzionali, refactor generale o audit repository.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 861305 --confirm-executed`

Output massimo 7 righe: `RESULT`, `HEAD`, `OFFLINE_LITE`, `REMOTE`, `TESTS`, `APK_SIZE_DELTA`, `BLOCKER`.
