PROMPT_ID=861305 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STANDARD

# Goal
Completa SOLO il Data Explorer Datasette già integrato in PersonalHub `main`: runtime Lite realmente offline, stessa semantica FK/Context del server e presentazione mobile PH-specifica. Non riscrivere Datasette in Compose.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`, branch canonico `main`;
- `origin/main` atteso: `fa86916e9cef06007298cb7e634df4afc084be7a`;
- `version.txt=47`; bump 47→48 UNA sola volta solo dopo tutti i gate feature;
- già presenti: snapshot detached+validato, DataExplorerActivity local/remote, WebViewAssetLoader, entry point Home + sei moduli, config `personalhub_read`, docs e CODE_MAP;
- contratto: live Room/WAL mai esposto; local mode blocca rete esterna; token mobile sync mai usato dall'explorer;
- `docs/DATA_EXPLORER.md` è autoritativo per FK native, cross-module entity hubs e mobile presentation;
- server task `527184` rende `personalhub_read` read-only e materializza FK cross-modulo + `hub_person_relations`.

# Esecuzione minima
1. Acquisisci task lock PH con PROMPT_ID 861305. Preflight unico: worktree + un solo fetch `origin main`; richiedi `origin/main == fa86916e9cef06007298cb7e634df4afc084be7a`; fast-forward locale. Mismatch/divergenza/dirty overlap => BLOCKED. Usa solo CODE_MAP row `database.data_explorer`, niente audit repo-wide.
2. Vendorizza/pinna Datasette Lite + Pyodide + wheel/assets necessari sotto gli asset PH. Nessuna CDN/runtime fetch. NON allentare il network block locale.
3. Dal detached snapshot costruisci, se necessario, una presentazione locale effimera read-only con semantica equivalente a `personalhub_read`:
   - vere SQLite FK e label leggibili;
   - relazioni dirette cross-modulo;
   - Context → bridge persona-centrico equivalente a `hub_person_relations`;
   - nessuna inferenza per nome e nessuna scrittura sul DB canonico.
4. Presentazione embedded: conserva motore Datasette per table/row/filter/facet/pagination/SQL/FK. Aggiungi solo template/CSS/assets compatibili con Lite per ottimizzare il mobile:
   - niente browser chrome;
   - card/list leggibile come default su schermi stretti, con accesso alla tabella densa quando utile;
   - FK come label/chip tappabili;
   - row detail con sezione **Related across PersonalHub** raggruppata per modulo, alimentata dalle vere FK/backlink;
   - filtri/facet/pagination/SQL restano funzionali;
   - light/dark, controlli touch-friendly, niente dipendenza da JS/plugin non supportati da Lite se non provata.
5. Test mirati prima del device:
   - snapshot coerente e isolato;
   - Lite avvia e SELECT funziona con networking disabilitato;
   - forward FK + reverse related rows con label;
   - scenario sintetico Carlo: persona collegata a transazione + Context con Place/Substance, tutti navigabili tramite FK reali;
   - i sei entry point aprono le tabelle canoniche;
   - tentativi write non modificano `personalhub.db`;
   - remote mode usa auth umana, mai token sync.
6. Gate host: compile leaf interessato, test mirati, poi una sola `checkArchitectureBoundaries`. Dopo failure usa solo leaf correction; un solo rerun aggregato finale.
7. QA solo AVD `Pixel_8a` tramite `python3 tools/android_emulator_control.py start|wait|stop`:
   - Home→Dati;
   - rete OFF: local Lite, tabella, row detail, SQL, FK e scenario cross-modulo navigabili;
   - verifica leggibilità a larghezza telefono senza colonne schiacciate come unico layout;
   - rete ON solo per remote: stesso comportamento relazionale su `personalhub_read` se 527184 è PASS;
   - back navigation corretta, chiusura elimina snapshot cache, nessun crash.
8. Misura una sola volta delta APK degli asset. Niente campagna di ottimizzazione salvo limite reale.
9. Solo dopo PASS: bump 47→48 una volta, build debug canonica firmata una volta, push `main`, installa QUELLO stesso APK sul Pixel fisico con helper canonico e delivery PH. Nessuna ricompilazione post-gate.
10. Rilascia task lock in ogni esito. PASS => stop.

# Acceptance
PASS solo se Lite è realmente offline/self-contained; local e remote offrono FK cliccabili/backlink e cross-module person hub equivalenti; UI embedded è più leggibile del raw browser mobile senza perdere funzioni Datasette; write bypass impossibile; architecture/tests/QA PASS; versione 48 costruita una sola volta e stesso APK installato/consegnato.

# Non-goal
Niente SQL write arbitrario, sync bidirezionale, nuovo DB canonico, riscrittura UI Datasette in Compose, redesign dei moduli, plugin opzionali non necessari, refactor generale o audit.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 861305 --confirm-executed`

Output massimo 7 righe: `RESULT`, `HEAD`, `OFFLINE_LITE`, `FK_GRAPH`, `MOBILE_UI`, `APK_SIZE_DELTA`, `BLOCKER`.
