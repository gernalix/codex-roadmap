PROMPT_ID=861305 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STANDARD

# Goal
Completa SOLO il Data Explorer ibrido già presente su PersonalHub main: vendorizza Datasette Lite/Pyodide realmente offline, porta la navigazione foreign-key nativa a piena parità utile local/remote, applica una presentazione mobile PH sottile senza riscrivere Datasette, quindi esegui QA/release.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`, project_id `49`, branch canonico `main`;
- origin/main minimo atteso: `690bcd9deb9056ee9fc12ee80e5c2e1d57c4dfa6`;
- la fondazione Data Explorer è già su main: snapshot detached+validato, `DataExplorerActivity`, contratto cross-feature, entry point dai sei moduli, WebViewAssetLoader, remote `personalhub_read`, docs/CODE_MAP;
- `docs/DATA_EXPLORER.md` è il contratto autorevole per offline, FK native e mobile presentation;
- local mode è fail-closed e blocca richieste fuori da `appassets.androidplatform.net`;
- il token Android `personalhub-sync` NON deve mai entrare nel Data Explorer remoto;
- il DB Room live e WAL NON devono mai essere serviti o modificati dal Data Explorer;
- `version.txt` è 47 al baseline: bump +1 UNA sola volta solo al gate finale.

# Esecuzione minima
1. Acquisisci il task lock PH con PROMPT_ID 861305. Preflight unico: checkout `main`, worktree, un solo fetch, fast-forward a origin/main; richiedi che `690bcd9...` sia antenato. Dirty overlap/divergenza => BLOCKED, niente stash/reset/rebase. Usa solo la row `database.data_explorer` di `.codex/CODE_MAP.tsv`.
2. Consumer preflight soltanto per API pubbliche effettivamente cambiate; poi compile leaf mirato. Niente audit repo-wide.
3. Vendorizza/pinna Datasette Lite + Pyodide + wheel/assets strettamente necessari sotto gli asset PH. Nessuna CDN/runtime fetch. Mantieni il network block locale: non allentarlo per far partire Pyodide.
4. Foreign key native:
   - lascia Datasette responsabile della navigazione relazionale; NON ricreare link FK in Compose/DOM custom;
   - per ogni FK SQLite reale, Datasette deve mostrare hyperlink con label leggibile e backlink dalla row referenziata;
   - fornisci metadata `label_column` espliciti dove l'inferenza è ambigua;
   - se una relazione canonica nota non è una FK fisica nel raw snapshot, genera DA QUELLO snapshot una presentazione effimera read-only con vere PK/FK SQLite e label semantiche; mai alterare `personalhub.db`;
   - local e remote devono avere semantica relazionale equivalente per le relazioni canoniche coperte dalla proiezione, senza mantenere manualmente due mappe divergenti: riusa/genera deterministicamente la specifica autorevole esistente (`datasette5`/Room schema) invece di riscoprirla o duplicarla a mano.
5. Presentazione mobile embedded, senza fork funzionale di Datasette:
   - Datasette continua a renderizzare table/row/filter/facet/pagination/SQL/FK;
   - applica lo stesso stylesheet/layout PH bundled a local e remote WebView: no browser chrome, compatibilità light/dark, tipografia leggibile, touch target adeguati, header tabella sticky dove sicuro, scrolling orizzontale delle tabelle invece di compressione illeggibile, FK link chiaramente distinguibili;
   - non nascondere filtri, facets, pagination, row pages o SQL editor;
   - l'azione "apri nel browser" resta Datasette standard non tematizzato da PH.
6. Test mirati sufficienti a provare:
   - snapshot coerente/validato e nessun accesso al DB/WAL live;
   - offline Lite avvia con rete disabilitata e una SELECT reale;
   - zero fetch esterni;
   - i sei entry point: People=`contacts`, Timer=`sessions`, Places=`places`, Substances=`substances`, WordPulse=`word_entries`, Soldi=`finance_transactions`;
   - almeno una catena FK per ciascun dominio dove presente: forward link con label + backlink filtrato; inoltre confronto automatico della specifica relazionale locale con quella canonica per evitare drift;
   - ID tecnici disponibili in dettaglio/API/SQL ma non usati come label primaria quando esiste label semantica;
   - write tentati dal Data Explorer non modificano `personalhub.db`;
   - remote usa `personalhub_read` con auth interattiva e senza header/token mobile.
7. Gate host: compile leaf, test mirati, una sola `checkArchitectureBoundaries`; failure aggregato -> correggi leaf e un unico rerun finale.
8. QA solo `Pixel_8a` emulator tramite `python3 tools/android_emulator_control.py start|wait|stop`:
   - Home → Dati e un entry point per ciascun modulo;
   - networking OFF: local Lite, SELECT, table/row, FK forward/backlink e SQL editor funzionano;
   - verifica leggibilità reale su viewport telefono: nessun testo/controllo essenziale tagliato, tabelle scrollabili, header/touch target utilizzabili;
   - networking ON solo per remote: browse/query autenticato su `personalhub_read`; se il runtime server del task 527184 non è ancora PASS, riporta BLOCKED per questo solo gate senza sostituire auth;
   - back navigation e cleanup snapshot PASS.
9. Misura UNA volta il delta APK dovuto a Lite/Pyodide/theme. Nessuna campagna di minificazione fuori scope.
10. Solo dopo tutti i gate PASS: incrementa `version.txt` 47→48 una volta, costruisci il debug canonico firmato una volta, push main, installa QUELLO stesso APK sul Pixel fisico con `python3 tools/android_pixel_apk.py install` e usa la delivery canonica PH. Nessuna ricompilazione post-gate.
11. Rilascia il task lock in ogni esito. PASS => stop immediato.

# Acceptance
PASS solo se Datasette Lite è realmente offline senza fetch esterni; local/remote conservano la navigazione FK nativa Datasette con label semantiche e backlink; il layout embedded è più leggibile su telefono senza sostituire le funzioni Datasette; il DB live resta read-only/inaccessibile al WebView; remote usa auth umana e mai token sync; architecture/test/QA PASS; versione 48 è costruita una sola volta e lo stesso APK finale viene installato/consegnato.

# Non-goal
Niente clone Datasette in Compose/Kotlin, fake FK links, sync bidirezionale server→PH, SQL write arbitrario, nuovo DB canonico, redesign delle UI normali dei moduli, plugin opzionali, refactor generale o audit repository.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 861305 --confirm-executed`

Output massimo 7 righe: `RESULT`, `HEAD`, `OFFLINE_LITE`, `FK_NAV`, `MOBILE_UX`, `APK_SIZE_DELTA`, `BLOCKER`.
