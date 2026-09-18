PROMPT_ID=886414 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST

# Goal
Valida localmente e chiudi SOLO l'isolamento completo delle capsule già implementato da ChatGPT sul branch remoto PersonalHub `feature/100-capsule-isolation`. Correggi esclusivamente eventuali errori direttamente causati dallo spostamento dei componenti Android nei manifest delle feature, dalla navigazione tramite alias pubblici o dal nuovo gate architetturale. Mantieni il branch separato: NON mergiarlo in `main` e NON eliminarlo.

# Starting point autoritativo
- dipendenza: PROMPT_ID=749621 deve essere PASS/finalizzato prima di iniziare;
- repo canonico locale: `/home/daniele/projects/PersonalHub`, project_id=49;
- branch remoto da validare: `feature/100-capsule-isolation`;
- baseline remota minima del branch: `8bfca0a683184109708fc9ceba2da897c7a7c413`;
- `version.txt=51` sul branch e NON va incrementato di nuovo;
- ChatGPT ha già:
  - rimosso dal manifest host Activity/receiver/provider e permessi specifici delle feature;
  - spostato ogni componente Android nel manifest della feature proprietaria;
  - spostato anche gli alias pubblici `com.gernalix.personalhub.shortcut.*` nei manifest delle feature;
  - eliminato dalla Home i nomi delle Activity private e instradato Home/pinned shortcut tramite gli stessi alias pubblici;
  - rafforzato `tools/check_architecture_boundaries.py` per vietare classi feature private nel manifest/Kotlin host e per consentire all'host solo i package diretti `.api` / `.hub`;
  - aggiornato `docs/CAPSULE_BOUNDARIES.md`, `docs/ARCHITECTURE.md` e `AGENTS.md`;
- il singolo `personalhub.db` resta intenzionalmente invariato: questo task NON deve separare database, schema o DAO;
- niente audit generale: usa solo i file già toccati e l'evidenza dei gate.

# Esecuzione minima
1. Dopo il PASS di 749621, acquisisci il coordinamento/lock PH previsto dalle regole correnti. Un solo fetch mirato del branch remoto e checkout/worktree isolato senza toccare lavori concorrenti. Verifica che la baseline minima sia antenata del branch.
2. Gate statico più economico:
   - `python3 -m py_compile tools/check_architecture_boundaries.py`;
   - `./gradlew checkArchitectureBoundaries --no-configuration-cache --console=plain`.
   Se fallisce, correggi SOLO il failure concreto nei manifest, host navigation, test o gate; niente refactor laterali.
3. Verifica manifest + compile con una sola invocazione aggregata iniziale:
   - `./gradlew :app:processDebugMainManifest :app:compileDebugKotlin :app:testDebugUnitTest --tests com.gernalix.personalhub.HubModuleTest --no-configuration-cache --console=plain`.
   Se il nome del task manifest non esiste nella versione AGP corrente, consulta una sola volta i task di `:app` e usa l'equivalente più stretto; non fare discovery repo-wide.
   In caso di failure, leggi il report una volta, correggi in batch lo stesso failure domain e rilancia solo il leaf fallito; alla fine un solo aggregato di conferma.
4. Sul manifest merged prodotto dal build verifica in modo bounded:
   - esistono esattamente i 7 alias pubblici People/Timer/Places/Substances/WordPulse/Soldi/Salute;
   - ogni alias risolve alla propria Activity;
   - provider/receiver/widget/permission già esistenti non sono scomparsi;
   - non esistono duplicati manifest introdotti dallo spostamento;
   - `app/src/main/AndroidManifest.xml` non nomina classi di implementazione delle feature.
5. Solo dopo host PASS, usa l'AVD canonico `Pixel_8a`; nessun device fisico. Costruisci una sola APK debug necessaria al test e installa esattamente quell'artefatto sull'emulatore.
6. Smoke runtime minimo dei 7 alias:
   - per ciascun `com.gernalix.personalhub.shortcut.*ShortcutActivity`, verifica che PackageManager/ADB lo risolva;
   - avvialo esplicitamente e verifica che si apra il modulo corretto senza `ActivityNotFoundException`, crash o ritorno involontario alla Home;
   - non testare feature interne non pertinenti.
7. Se un alias/component manifest fallisce, applica il minimo fix sullo stesso branch, riesegui solo il leaf gate necessario e poi una sola conferma finale di architettura + compile/manifest + smoke alias.
8. Commit/push SOLO su `feature/100-capsule-isolation`. Non modificare `main`, non creare PR, non mergiare, non eliminare il branch e non fare release/Telegram/Pixel reale.
9. Rilascia il lock/coordinamento. Dopo PASS finalizza la roadmap e fermati.

# Acceptance
PASS solo se: `py_compile` + `checkArchitectureBoundaries` PASS; manifest merge + `:app:compileDebugKotlin` + `HubModuleTest` PASS; merged manifest conserva i componenti/permessi richiesti senza duplicati; i 7 alias pubblici risolvono e aprono i 7 moduli sull'AVD; il branch remoto contiene eventuali fix; `version.txt` resta 51; `main` è intatto e il branch resta esistente/separato.

# Non-goal
Separare `personalhub.db`, cambiare schema/DAO/dati, refactor delle feature, nuove API, redesign UI, audit generale, test su Pixel/TCL, release, merge in `main`, cancellazione branch.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 886414 --confirm-executed`

Output massimo 7 righe: RESULT, BRANCH_HEAD, ARCH_GATE, MANIFEST_COMPILE, ALIASES, AVD_SMOKE, MAIN_UNCHANGED.
