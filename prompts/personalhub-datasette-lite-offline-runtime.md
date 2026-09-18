PROMPT_ID=861305 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STANDARD

# Goal
Completa SOLO il Data Explorer ibrido già integrato in `main`: rendi Datasette Lite realmente offline nell'APK, verifica local/remote su Android e rilascia il debug finale senza indebolire i boundary di sicurezza.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`, project_id `49`, branch `main`; unico branch remoto persistente: `main`;
- HEAD remoto atteso: `693f5d00f721a987e9a60a86625994d5319c1ff2`;
- commit applicativo del Data Explorer già integrato: `cbc35a522052fc16be5fe4f681c01bb1cf96ed70`; i commit successivi hanno solo aggiunto/rimosso il workflow one-shot di branch cleanup;
- Architecture boundaries e Play Store preflight erano PASS sul commit applicativo `cbc35a...`: non ripetere gate baseline prima delle modifiche;
- `main` contiene già snapshot DB detached+validato, DataExplorerActivity local/remote, contratto cross-feature, accessi dai sei moduli, WebViewAssetLoader, config `personalhub_read`, strings, docs e CODE_MAP;
- local mode blocca richieste fuori da `appassets.androidplatform.net`; il sync token Android NON deve essere usato dal Data Explorer remoto; il DB Room live NON deve mai essere servito;
- `version.txt` è `47`;
- il task `527184` deve essere PASS prima del QA remoto autenticato.

# Esecuzione minima
1. Acquisisci `python3 tools/personalhub_task_lock.py acquire --prompt-id 861305`. In un solo preflight: verifica worktree compatibile e branch `main`; fai un solo fetch + fast-forward; richiedi `HEAD=origin/main=693f5d00f721a987e9a60a86625994d5319c1ff2` e salva `RUN_HEAD`. Non esplorare il repo: usa solo la riga `database.data_explorer` di `.codex/CODE_MAP.tsv` e i path già elencati lì.
2. Non eseguire una build baseline. Controlla soltanto lo stato di `app/src/main/assets/datasette-lite/`; quindi vendorizza/pinna Datasette Lite + Pyodide + wheel/assets strettamente necessari secondo `docs/DATA_EXPLORER.md`. Nessuna CDN/runtime fetch e nessuna installazione globale. Mantieni il network block locale.
3. Se per completare l'integrazione cambi API Kotlin pubbliche, esegui il consumer preflight solo sui simboli effettivamente cambiati; altrimenti saltalo. Aggiungi/modifica esclusivamente test necessari a provare snapshot detached, cache confinata, avvio offline + SELECT reale, browse/SQL read-only, sei entry point canonici, impossibilità di modificare `personalhub.db` e remote auth interattiva senza token mobile.
4. Gate host dopo l'ultima modifica: compile leaf interessato, test mirati, poi UNA sola `checkArchitectureBoundaries`. Su failure usa solo il leaf/report pertinente e un unico rerun finale; niente `check` globale.
5. QA solo su `Pixel_8a` tramite `python3 tools/android_emulator_control.py start|wait|stop`: Home → Dati; disabilita rete del target e prova local Datasette Lite + SELECT; riabilita rete solo per il QA remoto su `personalhub_read` distribuito da `527184`; verifica nessun crash del feature, back navigation e rimozione snapshot cache. Se `527184` non è PASS o il runtime remoto non è disponibile, `BLOCKED`: non sostituire auth/token.
6. Misura UNA volta l'incremento dimensione APK dovuto agli asset; non avviare minificazione/refactor salvo limite reale di build/delivery.
7. Solo dopo i gate feature PASS: incrementa `version.txt` 47→48 UNA volta e costruisci il debug canonico firmato UNA volta. Prima del commit fai un solo fetch finale: se `origin/main != RUN_HEAD` => `BLOCKED`, niente rebase/merge. Altrimenti un solo commit/push diretto su `main`; installa QUELLO stesso APK sul Pixel fisico con `python3 tools/android_pixel_apk.py install` e usa la delivery canonica PH. Non ricostruire dopo il gate finale.
8. Rilascia `python3 tools/personalhub_task_lock.py release --prompt-id 861305` in ogni esito. PASS => stop immediato.

# Acceptance
PASS solo se Datasette Lite funziona realmente offline senza fetch esterni, usa soltanto snapshot read-only, remote explorer usa auth umana e non il token sync, write bypass è escluso dai test, architecture/tests/QA PASS, `main` contiene il completamento, versione 48 è costruita una sola volta e lo stesso APK finale è installato/consegnato.

# Non-goal
Niente riscrittura Datasette in Kotlin, sync bidirezionale server→PH, SQL write arbitrario, nuovo database canonico, redesign UI dei moduli, plugin opzionali, refactor generale o audit repository.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 861305 --confirm-executed`

Output massimo 7 righe: `RESULT`, `HEAD`, `OFFLINE_LITE`, `REMOTE`, `TESTS`, `APK_SIZE_DELTA`, `BLOCKER`.
