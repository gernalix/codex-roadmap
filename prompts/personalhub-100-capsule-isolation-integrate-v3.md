PROMPT_ID=284916 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST
PARENT_PROMPT_ID=886414


# Contratto Git/integrazione PH aggiornato — prevale su ogni istruzione successiva incompatibile
- `main` è baseline/target finale, non area di implementazione. Qualunque riferimento successivo a “branch obbligatorio main”, “lavora su main”, “push main”, “non creare PR”, “mantieni il branch separato” o equivalenti è superato da questo contratto.
- Se il task parte già da un branch feature nominato nel prompt, continua su QUEL branch. Altrimenti crea/usa il branch dedicato `codex/284916-capsule-isolation` dal più recente `origin/main`.
- Durante implementazione/fix branch-local NON acquisire il lock PH. Esegui i gate host branch-local necessari e pusha solo il branch candidato.
- Quando il branch è pronto, apri/aggiorna una PR verso `main`. A quel punto la stessa sessione può diventare integratore: acquisisci `tools/personalhub_task_lock.py`, fai un solo refresh di `origin/main`, usa `tools/personalhub_integration_context.py --branch <branch>`, rileggi il diff rispetto al main corrente e valuta semanticamente le interazioni. Un merge Git senza conflitti non basta.
- Se servono fix di compatibilità, applicali SOLO sul branch candidato e rilancia i gate pertinenti. Ambiguità sostanziale/out-of-scope => BLOCKED senza toccare `main`.
- Solo dopo review semantica + gate pertinenti PASS, integra la PR in `main`, pusha il canonico, elimina subito il branch remoto+locale e rilascia il lock. Se il task include QA condivisa su AVD/device o release, il lock deve essere acquisito prima di quella fase e può restare detenuto fino a fine integrazione/release.
- Se il task è davvero read-only e non produce alcuna modifica, branch/PR non sono necessari; resta comunque obbligatorio il lock per QA condivisa/release.

# Goal
Porta il branch remoto PersonalHub `feature/100-capsule-isolation` sopra il `main` corrente senza perdere né le nuove regole di concorrenza né l'isolamento capsule già implementato da ChatGPT; poi valida localmente e chiudi SOLO questo lavoro. Correggi esclusivamente errori direttamente causati dall'integrazione, dallo spostamento dei componenti Android nei manifest delle feature, dalla navigazione tramite alias pubblici o dal nuovo gate architetturale. Mantieni il branch separato: NON mergiarlo in `main` e NON eliminarlo.

# Starting point autoritativo
- sostituisce il prompt non eseguito 886414;
- dipendenza: PROMPT_ID=749621 deve essere PASS/finalizzato prima di iniziare;
- repo canonico locale: `/home/daniele/projects/PersonalHub`, project_id=49;
- branch remoto da validare: `feature/100-capsule-isolation`;
- baseline remota minima del branch capsule: `8bfca0a683184109708fc9ceba2da897c7a7c413`;
- al momento della preparazione, il branch era 18 commit avanti e 4 commit indietro rispetto a `main`;
- i 4 commit allora presenti solo su `main` toccavano `AGENTS.md`, `docs/CONCURRENT_WORK.md`, `tools/personalhub_integration_context.py`, `tools/personalhub_task_lock.py`; unico overlap col branch capsule: `AGENTS.md`;
- prima dei test devi integrare il `main` corrente NEL branch capsule con review semantica bounded, preservando sia le regole di concorrenza nuove sia la regola capsule/manifest aggiunta dal branch;
- `version.txt=51` sul branch e NON va incrementato di nuovo;
- ChatGPT ha già:
  - rimosso dal manifest host Activity/receiver/provider e permessi specifici delle feature;
  - spostato ogni componente Android nel manifest della feature proprietaria;
  - spostato gli alias pubblici `com.gernalix.personalhub.shortcut.*` nei manifest delle feature;
  - eliminato dalla Home i nomi delle Activity private e instradato Home/pinned shortcut tramite gli stessi alias pubblici;
  - rafforzato `tools/check_architecture_boundaries.py` per vietare classi feature private nel manifest/Kotlin host e per consentire all'host solo i package diretti `.api` / `.hub`;
  - aggiornato `docs/CAPSULE_BOUNDARIES.md`, `docs/ARCHITECTURE.md` e `AGENTS.md`;
- il singolo `personalhub.db` resta intenzionalmente invariato: NON separare database, schema o DAO;
- niente audit generale: usa `.codex/CODE_MAP.tsv`, i file già toccati e l'evidenza dei gate.

# Esecuzione minima
1. Dopo il PASS di 749621, usa il coordinamento PH corrente. Un solo fetch mirato di `main` e `feature/100-capsule-isolation`; checkout/worktree isolato senza toccare lavori concorrenti. Verifica che la baseline minima capsule sia antenata del branch.
2. Prima di compilare, porta il `main` corrente DENTRO `feature/100-capsule-isolation`:
   - usa `tools/personalhub_integration_context.py`/regole correnti per il contesto bounded;
   - se il solo overlap resta `AGENTS.md`, preserva entrambe le famiglie di regole: concorrenza/single-writer da main + ownership manifest/direct `.api`/`.hub` dal branch;
   - per ulteriori commit apparsi dopo questa preparazione, integra solo se gli overlap sono chiaramente compatibili con questo failure domain; ambiguità reale o conflitto sostanziale fuori scope => BLOCKED;
   - push del branch aggiornato. NON toccare `main`.
3. Gate statico:
   - `python3 -m py_compile tools/check_architecture_boundaries.py`;
   - `./gradlew checkArchitectureBoundaries --no-configuration-cache --console=plain`.
   Failure => correggi SOLO il failure concreto nei manifest, host navigation, test o gate.
4. Verifica manifest + compile con una sola invocazione aggregata iniziale:
   - `./gradlew :app:processDebugMainManifest :app:compileDebugKotlin :app:testDebugUnitTest --tests com.gernalix.personalhub.HubModuleTest --no-configuration-cache --console=plain`.
   Se il task manifest ha un nome diverso nella versione AGP corrente, consulta una sola volta i task di `:app` e usa l'equivalente più stretto. In caso di failure, leggi il report una volta, correggi in batch lo stesso failure domain e rilancia solo il leaf fallito; poi una sola conferma aggregata.
5. Sul manifest merged verifica bounded:
   - esistono esattamente i 7 alias pubblici People/Timer/Places/Substances/WordPulse/Soldi/Salute;
   - ogni alias risolve alla propria Activity;
   - provider/receiver/widget/permission già esistenti non sono scomparsi;
   - nessun duplicato manifest introdotto;
   - `app/src/main/AndroidManifest.xml` non nomina implementazioni feature.
6. Solo dopo host PASS, usa l'AVD canonico `Pixel_8a`; nessun device fisico. Costruisci una sola APK debug necessaria al test e installa esattamente quell'artefatto sull'emulatore.
7. Smoke runtime minimo dei 7 alias:
   - ogni `com.gernalix.personalhub.shortcut.*ShortcutActivity` deve risolversi;
   - avvialo esplicitamente e verifica che apra il modulo corretto senza `ActivityNotFoundException`, crash o ritorno involontario alla Home;
   - nessun test feature interno non pertinente.
8. Se un alias/component manifest fallisce, applica il minimo fix sullo stesso branch, riesegui solo il leaf gate necessario e poi una sola conferma finale di architettura + compile/manifest + smoke alias.
9. Commit/push SOLO su `feature/100-capsule-isolation`. Non creare PR, non mergiare in `main`, non eliminare branch e non fare release/Telegram/Pixel reale.
10. Rilascia il coordinamento/lock secondo le regole correnti. Dopo PASS finalizza la roadmap e fermati.

# Acceptance
PASS solo se: il `main` corrente è stato integrato nel branch capsule preservando le regole concorrenti; `py_compile` + `checkArchitectureBoundaries` PASS; manifest merge + `:app:compileDebugKotlin` + `HubModuleTest` PASS; merged manifest conserva componenti/permessi senza duplicati; i 7 alias risolvono e aprono i 7 moduli sull'AVD; branch remoto contiene integrazione/fix; `version.txt` resta 51; `main` è intatto e il branch resta separato.

# Non-goal
Separare `personalhub.db`, cambiare schema/DAO/dati, refactor delle feature, nuove API, redesign UI, audit generale, test su Pixel/TCL, release, merge del branch capsule in `main`, cancellazione branch.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 284916 --confirm-executed`

Output massimo 7 righe: RESULT, BRANCH_HEAD, MAIN_INTEGRATION, ARCH_GATE, MANIFEST_COMPILE, ALIASES_AVD, MAIN_UNCHANGED.
