PROMPT_ID=918536 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STANDARD


# Contratto Git/integrazione PH aggiornato — prevale su ogni istruzione successiva incompatibile
- `main` è baseline/target finale, non area di implementazione. Qualunque riferimento successivo a “branch obbligatorio main”, “lavora su main”, “push main”, “non creare PR”, “mantieni il branch separato” o equivalenti è superato da questo contratto.
- Se il task parte già da un branch feature nominato nel prompt, continua su QUEL branch. Altrimenti crea/usa il branch dedicato `codex/918536-datasette-lite-offline` dal più recente `origin/main`.
- Durante implementazione/fix branch-local NON acquisire il lock PH. Esegui i gate host branch-local necessari e pusha solo il branch candidato.
- Quando il branch è pronto, apri/aggiorna una PR verso `main`. A quel punto la stessa sessione può diventare integratore: acquisisci `tools/personalhub_task_lock.py`, fai un solo refresh di `origin/main`, usa `tools/personalhub_integration_context.py --branch <branch>`, rileggi il diff rispetto al main corrente e valuta semanticamente le interazioni. Un merge Git senza conflitti non basta.
- Se servono fix di compatibilità, applicali SOLO sul branch candidato e rilancia i gate pertinenti. Ambiguità sostanziale/out-of-scope => BLOCKED senza toccare `main`.
- Solo dopo review semantica + gate pertinenti PASS, integra la PR in `main`, pusha il canonico, elimina subito il branch remoto+locale e rilascia il lock. Se il task include QA condivisa su AVD/device o release, il lock deve essere acquisito prima di quella fase e può restare detenuto fino a fine integrazione/release.
- Se il task è davvero read-only e non produce alcuna modifica, branch/PR non sono necessari; resta comunque obbligatorio il lock per QA condivisa/release.

# Goal
Completa SOLO il Data Explorer Datasette già integrato in PersonalHub `main`: runtime Lite realmente offline, stessa semantica FK/Context/temporal del server e presentazione mobile PH-specifica. Non riscrivere Datasette in Compose.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`, branch canonico `main`;
- esegui questo prompt SOLO dopo `PROMPT_ID=357214` PASS/finalizzato **e** `PROMPT_ID=527184` PASS/finalizzato; quindi anche 918274+734205+862541+315972+946238+528163+684930 devono essere conclusi e Salute/Obsidian devono essere presenti in `main`; baseline Git Data/History `3558ab39fb7f51f39a09c43e6d90b18ae3319b07` deve essere antenata del RUN_HEAD;
- `version.txt=50`; bump 50→51 UNA sola volta solo dopo tutti i gate feature;
- fix Luoghi già in `main`: check-in sovrapposti scelgono automaticamente il candidato nettamente più vicino solo quando gli intervalli di distanza rispetto all'accuracy GPS non si sovrappongono; journal conserva la causa originale e registra la soglia reale raggio+accuracy;
- già presenti: snapshot detached+validato, DataExplorerActivity local/remote, WebViewAssetLoader, entry point globale Home e route ancora supportate; NON reintrodurre un entry point Data Explorer nel Timer; config `personalhub_read`, docs e CODE_MAP;
- contratto: live Room/WAL mai esposto; local mode blocca rete esterna; token mobile sync mai usato dall'explorer;
- `docs/DATA_EXPLORER.md` è autoritativo per FK native, grafo cross-modulo peer-to-peer e mobile presentation;
- server task `527184` rende `personalhub_read` read-only e materializza FK cross-modulo + grafo simmetrico `hub_entity_relations`.

# Esecuzione minima
1. Acquisisci task lock PH con PROMPT_ID 918536. Preflight unico: worktree + un solo fetch `origin main`; fast-forward locale e fissa RUN_HEAD. Richiedi `version.txt=50`, che la baseline Git Data/History indicata sopra sia antenata e che i task 357214 e 527184 risultino già finalizzati nella roadmap; divergenza/dirty overlap => BLOCKED. Non ripetere i gate Git History già PASS salvo che questo task tocchi direttamente quel boundary. Usa solo CODE_MAP row `database.data_explorer` più i file Luoghi già noti sotto `capsules/checkin` e i test indicati sotto; niente audit repo-wide.
2. Vendorizza/pinna Datasette Lite + Pyodide + wheel/assets necessari sotto gli asset PH. Nessuna CDN/runtime fetch. NON allentare il network block locale.
3. Dal detached snapshot costruisci, se necessario, una presentazione locale effimera read-only con semantica equivalente a `personalhub_read`:
   - vere SQLite FK e label leggibili;
   - relazioni dirette cross-modulo;
   - Context → grafo simmetrico deduplicato equivalente a `hub_entity_relations`, con provenienza Context separata e ogni entità risolvibile navigabile da entrambi gli estremi;
   - temporal graph equivalente al server: visite Places, sessioni Timer, transazioni Soldi, intake, eventi/initiative People e WordPulse activity bursts; stesse soglie e stessa suppression se FK/Context già spiega la coppia;
   - WordPulse NON usa gli intervalli lunghi delle sessioni come evidenza temporale; People NON deduce la presenza della persona dal timestamp;
   - nessuna inferenza per nome e nessuna scrittura sul DB canonico.
4. Presentazione embedded: conserva motore Datasette per table/row/filter/facet/pagination/SQL/FK. Aggiungi solo template/CSS/assets compatibili con Lite per ottimizzare il mobile:
   - niente browser chrome;
   - card/list leggibile come default su schermi stretti, con accesso alla tabella densa quando utile;
   - FK come label/chip tappabili;
   - row detail con **Related across PersonalHub** per FK/Context e sezione separata **Temporal associations** per inferenze temporali; high prima, medium collassate di default; niente doppioni quando esiste già FK/Context;
   - filtri/facet/pagination/SQL restano funzionali;
   - light/dark, controlli touch-friendly, niente dipendenza da JS/plugin non supportati da Lite se non provata.
5. Test mirati prima del device:
   - esegui il gate Luoghi già pre-localizzato: `CheckInAccuracyPolicyTest` (incluso scenario reale Carlo Visda/Rema), i casi check-in di `PlacesHistoryMapGeofencingTest` e compile leaf `:feature:luoghi`; niente discovery aggiuntiva se PASS;
   - verifica che un overlap chiaramente separabile scelga Carlo, che candidati entro l'incertezza restino `AMBIGUOUS`, che `threshold_m` includa l'accuracy e che recovery/cancel non cancellino la causa diagnostica;
   - snapshot coerente e isolato;
   - Lite avvia e SELECT funziona con networking disabilitato;
   - forward FK + reverse related rows con label;
   - scenario sintetico con almeno quattro moduli inclusa Salute (es. Salute sample/journal, Places, People e Substances), verificando navigazione FK/backlink in entrambe le direzioni da ciascun record;
   - scenario temporale: overlap Place/Timer esplicito via Context viene soppresso come duplicate backlink ma incrementa supporto temporale; intake durante visita resta temporal link; transazione→Place già FK non duplica; WordPulse entry ravvicinate diventano un burst; People compare solo tramite event/initiative;
   - l'entry point globale Home e le route module-level ancora supportate aprono le tabelle canoniche; Timer non deve riacquistare un entry point Data Explorer;
   - tentativi write non modificano `personalhub.db`;
   - remote mode usa auth umana, mai token sync.
6. Gate host: compile leaf interessato, test mirati, poi una sola `checkArchitectureBoundaries`. Dopo failure usa solo leaf correction; un solo rerun aggregato finale.
7. QA solo AVD `Pixel_8a` tramite `python3 tools/android_emulator_control.py start|wait|stop`:
   - esegui una sola volta `CheckInAttemptJournalInstrumentedTest` sul target canonico; se fallisce, correggi solo il failure domain Luoghi e riesegui il leaf test;
   - Home→Dati;
   - rete OFF: local Lite, tabella, row detail, SQL, FK e scenario cross-modulo navigabili;
   - verifica leggibilità a larghezza telefono senza colonne schiacciate come unico layout;
   - rete ON solo per remote: stesso comportamento relazionale su `personalhub_read`, già distribuito e validato dal task 527184;
   - back navigation corretta, chiusura elimina snapshot cache, nessun crash.
8. Misura una sola volta delta APK degli asset. Niente campagna di ottimizzazione salvo limite reale.
9. Solo dopo PASS: bump 50→51 una volta, build debug canonica firmata una volta, push `main`, installa QUELLO stesso APK sul Pixel fisico con helper canonico e delivery PH. Nessuna ricompilazione post-gate.
10. Rilascia task lock in ogni esito. PASS => stop.

# Acceptance
PASS solo se il regression gate Luoghi Carlo Visda/Rema è PASS; Lite è realmente offline/self-contained; local e remote hanno FK/Context deduplicati e lo stesso temporal graph separato del server, senza duplicare backlink espliciti; UI embedded distingue Related vs Temporal e resta più leggibile del raw browser mobile; write bypass impossibile; architecture/tests/QA PASS; versione 51 costruita una sola volta e stesso APK installato/consegnato.

# Non-goal
Niente SQL write arbitrario, sync bidirezionale, nuovo DB canonico, riscrittura UI Datasette in Compose, redesign dei moduli, plugin opzionali non necessari, refactor generale o audit.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 918536 --confirm-executed`

Output massimo 8 righe: `RESULT`, `HEAD`, `PLACES_CHECKIN`, `OFFLINE_LITE`, `FK_GRAPH`, `TEMPORAL`, `MOBILE_UI`, `BLOCKER`.
