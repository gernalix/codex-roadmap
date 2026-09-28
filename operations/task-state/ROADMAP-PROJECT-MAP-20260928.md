# Active roadmap project attribution — 2026-09-28

MegaVault is authoritative. These are the active work items that lacked usable C2 project metadata at reconciliation time.

Total: 231

| Work item | Inferred MegaVault project | Evidence source | Title |
|---|---|---|---|
| `wi:37832d5a38a04e29a6c1bdccabf08f82` | `grindr-favorites-monitor` | `repo` | Regression: C2 Issue #1310 Grindr favorites history and Telegram actions |
| `wi:7e98dee44dae4265ab7b8210cf6a2cc8` | `datasette5` | `repo` | Datasette5: correggere il percorso predefinito degli schemi nei test PersonalHub |
| `wi:f5cef53ce33749e8b100ad866f01278f` | `fedora-system-monitor` | `semantic` | Diagnostica e ripristina i monitor Uptime Kuma rossi |
| `wi:fdd72bab3cd44ee89decb25f910b87c6` | `grindr-favorites-monitor` | `repo` | Usare identità canonica per le card Grindr Favorites |
| `wi:c0d99c19998740e2b386bb2bf54ae106` | `megavault` | `root` | Phase C — selezione DB e Datasette-friendliness nel codice sorgente |
| `wi:8e74cd241eea460faa2556eb392d4bb6` | `fedora-t7-backup` | `repo` | Investigate T7 restic backup failures and repository corruption |
| `prompt:302284` | `codex-roadmap` | `repo` | Distribuisci gli ultimi fix della prompt infrastructure |
| `prompt:714263` | `fedora-system-monitor` | `repo` | Chiudere il residuo Kuma di sqlite-to-obsidian |
| `wi:f078db802caf4cdcbcf8682527fe0e14` | `personalhub` | `repo` | Definire strategia i18n/lint PersonalHub per MissingTranslation |
| `state:gate:008c5ecbb292e8c246fc` | `codex-roadmap` | `repo` | Resolve blocker: Raw/normalized archive source available for the target session does not contain the successor goal cycles needed by `codex_task_costs.py`; a safe isolated analysis returns only the historical 624831 row. Repo-integrator also reports unrelated PR #2 checks-failed for `gernalix/adb-device-keeper`. |
| `state:gate:9ad7b5812f954676d1c8` | `adb-device-keeper` | `root` | Resolve blocker: GitHub Actions cannot start the deterministic job because of the account billing/spending-limit condition. This is external to the code change. |
| `state:gate:55124f54849769b609e2` | `fedora-system-monitor` | `root` | Resolve blocker: L'audit successivo richiede solo una finestra di cronologia reale sufficientemente rappresentativa. |
| `state:gate:5c9bd667130f639a1d50` | `codex-roadmap` | `root` | Resolve blocker: ahead_by>0 can still be squash/cherry-pick equivalent; ancestry alone is insufficient. |
| `state:gate:d9a7f05f5f4c41fffdf5` | `codex-roadmap` | `root` | Resolve blocker: Credential-store writes are currently blocked by the Remote Desktop tool safety layer: attempts to pipe the existing passwords into GitHub Actions secrets or GNOME Secret Service are rejected before execution. Do not expose, regenerate or commit them. Other implementation/monitoring work can continue. |
| `state:gate:418325ea7dc254618ead` | `codex-roadmap` | `root` | Resolve blocker: 181259 targets a nonexistent GitHub remote (gernalix/grindr-web-exporter); local state must be reconciled before a safe successor can run. |
| `state:gate:30eb0387ec8cc1a918ca` | `codex-roadmap` | `root` | Resolve blocker: Telegram source/runtime closure non ha blocker ed è completa: 966124 è terminale `completed`, il source canonico è integrato e i branch temporanei sono rimossi. Il successivo audit notifiche resta subordinato alla master lane. |
| `state:gate:7ee051a4742193a325c6` | `personalhub` | `root` | Resolve blocker: Priority gate, not a product blocker: C2 / 175908 owns the current execution lane. Do not launch new PH workers until C2 is terminal; 707603 is already running and must not be duplicated. |
| `wi:126a7347376647d08d75cfb0b3aed128` | `personalhub` | `repo` | Rimuovere Datasette completamente da PersonalHub |
| `wi:2f0f5246432e48ed8f454714e8cff72c` | `github-autosync` | `repo` | Reconcile stale chrome-codex-switcher repo-task without publishing historical branch |
| `wi:4dd3b3acaac84e79abacbf0df59d765e` | `codex-roadmap` | `repo` | Analizzare retrospettivamente le chat ChatGPT e tracciare i finding C2 |
| `wi:4e8aaf5df49a4d45808b52d93ccdd667` | `codex-roadmap` | `repo` | C2 TUI: throughput e tempi da eventi canonici |
| `wi:53a52adb1bf24689a76e384a95ca9919` | `codex-roadmap` | `repo` | Aggiungere fast-path C2 per adottare modifiche esterne |
| `wi:6a5d66627c98493c98b8c3f2080538e7` | `codex-roadmap` | `repo` | c2-codex-human: aggiungere la spiegazione on-demand dei messaggi visibili |
| `wi:7c0bbc55a6b14f99845c133eff406c1a` | `salute` | `repo` | Resolve salute.db authority classification mismatch |
| `wi:b0e08a6e920442d7b3eb2533fcf52ed9` | `megavault` | `repo` | Riconciliare path authority e metadata repository di MegaVault |
| `wi:bdfb0b1951cc4361b01690b5b18efcd7` | `chatgpt-rdc-supervisor` | `repo` | Adopt Project Capsule v1 in chatgpt-rdc-supervisor |
| `wi:d08356a155404433bbea2f6700287927` | `codex-roadmap` | `manual_verified` | Sanare tutti i repo/worktree sporchi e prevenire ricorrenza |
| `wi:dce555999f864385912180bedadb974d` | `fedora-external-updater` | `repo` | Automatizzare la copertura updater del software esterno, incluso RDC |
| `wi:f5e4489e271244c68e987a58a006cedb` | `personalhub` | `repo` | Ripristinare History PersonalHub con Mutation Event Store semantico |
| `wi:68cd5b09eae24fe59352bd0750a559c1` | `megavault` | `root` | P0 MegaVault definitiva + database inventory + Datasette universale |
| `wi:6a187c7e94be40daba8dce5678ba64f6` | `datasette5` | `repo` | Phase D — motore unico Fedora → Oracle → Datasette |
| `wi:9116862e72024e89b0033b4c6eeb146c` | `datasette5` | `repo` | Phase E — UX Datasette standard e navigazione frictionless |
| `wi:879ae0332e364440ad013f090a63714d` | `megavault` | `root` | Gate finale — MegaVault + database inventory + Datasette end-to-end |
| `wi:e20d87af9a6641c385b03b40aa72ab8a` | `megavault` | `root` | Gate finale — MegaVault + database inventory + Datasette end-to-end |
| `wi:7ee12d74262b498f892f51de128e041b` | `personalhub` | `repo` | Substances registra con stock 0 e clear+focus globale nei filtri Cerca |
| `prompt:181259` | `grindr-web-exporter` | `repo` | Riprendi Grindr dopo il login senza model waiting |
| `prompt:556372` | `grindr-web-exporter` | `manual_verified` | Delegare export Grindr end-to-end a ChatGPT Desktop |
| `prompt:588376` | `logseq-updates` | `repo` | Bonificare history Logseq e attivare updater |
| `wi:4679f25e5daa41e1bb43f74914aad26e` | `workflowy-importer` | `repo` | Verify recurring Workflowy roadmap sync heartbeat alert |
| `wi:862b055b7d354891bf6a25ea47c5904a` | `datasette5` | `manual_verified` | Verify recurring Oracle Datasette API Kuma heartbeat alert |
| `wi:1c989b834905489993c3ab03f88ba06c` | `codex-roadmap` | `repo` | Route web executor C2 intake through the canonical writer |
| `wi:c04fddf34c024cc49a9dc94974212e9e` | `codex-roadmap` | `repo` | Coalesce recurrent Kuma heartbeat alerts in C2 Inbox |
| `wi:fb1b1feff32b4eec98c4cf244905f007` | `codex-roadmap` | `repo` | C2 Activity Digest: notifiche desktop dalle transizioni canoniche |
| `wi:dad7a0b2953041a597762b7190bd074c` | `codex-roadmap` | `manual_verified` | Convergere tutti i branch non-main su main e rimuovere quelli integrati |
| `wi:ce3676f92b59422f94c4d5607daf630a` | `grindr-favorites-monitor` | `semantic` | Valutare enrichment chat e convergenza repo Grindr |
| `wi:9e4582576d404f3ebcd51c687f36289e` | `codex-roadmap` | `repo` | Prevent stale C2 human copy after lifecycle changes |
| `state:phase:5d12701b31d1cc556c86` | `fedora-system-monitor` | `root` | Plan |
| `state:phase:9a29a9cc7fcaffc446ea` | `codex-roadmap` | `repo` | Plan |
| `state:phase:d782b96c5fa7dbd1b8db` | `adb-device-keeper` | `root` | Plan |
| `wi:76b6cc855584427993abe9c6bfb2289b` | `workflowy-importer` | `repo` | Handle Workflowy API 429 with bounded retry/coalesced sync |
| `state:step:10bbb6a275529b86bf07` | `codex-roadmap` | `repo` | Integrate the codex-usage task branch through the repo single writer. |
| `state:step:63ae4d9a0f58b01e4079` | `adb-device-keeper` | `root` | Integrate PR #2 into main once GitHub Actions can run or an approved equivalent gate is available. |
| `state:step:6810f4deddeae23c390f` | `codex-roadmap` | `repo` | Fast-forward canonical checkouts only where remote main is newer and clean. |
| `state:step:44dcfb45a24fb6986267` | `adb-device-keeper` | `root` | Verify the service remains enabled/active and reconnect behavior survives one normal Fedora reboot. |
| `state:step:05479a2ce0079fb7d5b6` | `fedora-system-monitor` | `root` | Lasciare accumulare cronologia reale sufficiente. |
| `state:step:ef290e68e1ac780b8924` | `fedora-system-monitor` | `root` | Classificare notifiche verbose/incomprensibili/inutili/ripetute/flapping. |
| `state:step:51a7aa9414200d5d78b2` | `fedora-system-monitor` | `root` | Applicare fix mirati ai singoli producer; niente broad refactor. |
| `state:step:91ff20cf023f8cb7b1f6` | `fedora-system-monitor` | `root` | Rivalutare la policy legacy del prefisso project_id visibile e spostarlo a metadata se non serve all'utente. |
| `state:phase:406e01fae59883091b63` | `codex-roadmap` | `root` | Phase 2 — Patch-equivalence review |
| `state:phase:ed5f2fed53a2355da052` | `codex-roadmap` | `root` | Phase 2 — Implementation |
| `state:step:b1ec2cf01999526bacfe` | `activity-watch-uploader` | `repo` | None for 994029. |
| `state:step:d8b40dc99d0d0789d6f8` | `codex-roadmap` | `repo` | Target-session prompt_costs readback/backfill requires source evidence containing the successor goal cycles; repo-integrator has an unrelated failed-check PR. Acceptance is not met. |
| `state:step:c7048f3f5721fc2d6c72` | `adb-device-keeper` | `root` | Resolve/clear the external GitHub Actions billing/spending-limit prerequisite or use the repository's approved integration path if it can accept existing deterministic local evidence. |
| `state:step:9fe05c6a607b3a9aeafb` | `adb-device-keeper` | `root` | Merge/integrate PR #2 to main without bypassing repository protections. |
| `state:step:28cbf219208a356b64aa` | `adb-device-keeper` | `root` | Perform one normal Fedora reboot and verify adb-device-keeper returns enabled/active and reconnects both devices automatically. |
| `state:step:ebee4ac4feae4af425c3` | `fedora-system-monitor` | `root` | Accumulare e analizzare cronologia reale. |
| `state:step:e22f313cf0a586071f40` | `fedora-system-monitor` | `root` | Correggere i producer rumorosi e verificare una nuova finestra di notifiche post-fix. |
| `state:step:c41e05c7469d66fe0617` | `codex-roadmap` | `root` | Wait until active infrastructure tasks are terminal. |
| `state:step:7d5e8a8cccc8ddb1c02a` | `codex-roadmap` | `root` | Fetch all refs locally once and run bounded `git cherry` / patch-id review on every `ahead_by>0` candidate. |
| `state:step:342fa12f1bf63362cddb` | `codex-roadmap` | `root` | Integrate any genuinely unique useful commit before considering its branch deletable. |
| `state:step:519514145a852408fa95` | `codex-roadmap` | `root` | Record explicit keep/delete disposition for every review branch. |
| `state:step:7324dbeaafed954e9cbb` | `codex-roadmap` | `root` | Store publisher credential in GitHub Actions secret; never commit it. |
| `state:step:4b3f828253631930505b` | `codex-roadmap` | `root` | Store subscriber credential in Fedora Secret Service; never commit it. |
| `state:step:99e8f6692dec6e59e047` | `codex-roadmap` | `root` | Enable/validate the Fedora subscriber after its Secret Service credential is present. |
| `state:phase:b8e9d9ddf7809999f44c` | `codex-roadmap` | `root` | Phase 3 — Validation |
| `state:phase:ba09a0734fb2b5cdba98` | `codex-roadmap` | `root` | Phase 3 — Deletion and readback |
| `state:phase:d8e13b38be7ed8f9e1e9` | `codex-roadmap` | `root` | Phase 2 — PersonalHub P0 + live DB migration (PARKED BY USER OVERRIDE) |
| `state:step:7f67eae1e98200c0a2d7` | `codex-roadmap` | `root` | Delete ancestry-safe and proven-equivalent branches with authenticated local/GitHub tooling. |
| `state:step:81a6301abdffe3daee16` | `codex-roadmap` | `root` | Prove one real checkpoint push produces one ntfy event. |
| `state:step:f7438e8a8e78cda3ddb3` | `codex-roadmap` | `root` | Re-read all remote branch lists. |
| `state:step:d314424f62de4c66d5c7` | `codex-roadmap` | `root` | Retain only canonical branches plus explicitly justified active/seed branches. |
| `state:step:ab41bcec03dd8c4dc9b7` | `codex-roadmap` | `root` | Update this checkpoint with final evidence and close the cleanup lane. |
| `state:step:c608fe0ef0c890c9cb1c` | `codex-roadmap` | `root` | Verify affected repos are clean and pushed. |
| `state:step:6991351d6dbd266e194e` | `codex-roadmap` | `root` | Update protocol/docs and close this state file. |
| `state:step:ac6183f67a544c3f3bae` | `codex-roadmap` | `root` | Reconcile and integrate `chatgpt/workflowy-integration` into the then-current PersonalHub main, rerun affected gates, delete the temporary branch, and record the merged commit. |
| `state:step:87ec725cf06e0cc7baca` | `codex-roadmap` | `root` | Run and integrate 857906 after 920550. |
| `state:step:88e2221ae2d33f610713` | `codex-roadmap` | `root` | Run and integrate 707603 on the resulting schema. |
| `state:step:76ddc66ecd08ec2293c8` | `codex-roadmap` | `root` | Run and integrate 840907, including true offline behavior and artifact-size impact. |
| `state:step:27dcb919a9e66ad2d3f0` | `codex-roadmap` | `root` | Run 788606 release preflight; freeze the exact final PersonalHub main commit, Room schema/identity, minified APK/AAB and hashes. |
| `state:step:d257e2780924892d9910` | `codex-roadmap` | `root` | **ABSOLUTE NEXT STEP AFTER 788606:** execute 913264 immediately. Read the real Pixel DB identity/schema, take immutable DB/WAL/SHM + installed-APK rollback backup, externally migrate a copy directly to the frozen final schema, and pass SQLite quick_check/integrity/FK/data-preservation checks. Do not insert any unrelated task between 788606 and 913264. |
| `state:step:e685443f4fb7023f4e8c` | `codex-roadmap` | `root` | Install the exact frozen final APK on the primary Pixel using explicit ADB serial and verify Home + every module against preserved real data before any non-PH lane resumes. |
| `state:step:68ac8aae03946340c602` | `codex-roadmap` | `root` | Before final cutover, converge every still-relevant PH side branch into `main`: prove patch/semantic uniqueness, merge/cherry-pick/squash only valid unabsorbed work through the canonical writer, then delete all absorbed/obsolete non-main PH branches and close stale PRs. End with clean main-only operational state. |
| `state:step:7d878ed8bcc02e621b6f` | `codex-roadmap` | `root` | Do not resume non-PH recovery lanes until all PH items above are complete, unless PH is truly blocked. |
| `state:phase:8d8ce18fa8c47d1ad721` | `codex-roadmap` | `root` | Phase 3 — C2 / remaining prompt-infrastructure runtime closure (CURRENT PRIORITY) |
| `state:step:13517a9116bec1042d29` | `codex-roadmap` | `root` | After active tasks finish, fetch all refs locally and run git cherry / patch-id checks on every review branch. |
| `state:step:88da4b732f1fc43d768e` | `codex-roadmap` | `root` | Integrate genuinely unique useful commits before deletion. |
| `state:step:a351d7a428d799129f1d` | `codex-roadmap` | `root` | Delete ancestry-safe and subsequently proven-equivalent branches with authenticated local/GitHub tooling. |
| `state:step:a5412c9ccbb65c395fad` | `codex-roadmap` | `root` | Re-read remote branches and retain only canonical plus intentionally active/seed branches. |
| `state:step:cc7feee4d22d859f1585` | `codex-roadmap` | `root` | Populate the GitHub Actions publisher secret and Fedora Secret Service subscriber credential when the tool can perform credential-store writes; enable/test Fedora subscriber; run one real checkpoint end-to-end; perform browser/Android one-time subscription where device UI is available; finalize docs/state. |
| `state:step:11046c379b7d2a9a0a54` | `codex-roadmap` | `root` | Resume 302284 from its parked checkpoint and finish the remaining consolidated roadmap/Workflowy/CCS/codex-usage runtime readback. |
| `state:step:032e1357d145bd5eeb06` | `codex-roadmap` | `root` | Run routing-safe CCS successor 896074 only after 302284 PASS. |
| `state:step:f2c02fe5e9d2d2506f44` | `codex-roadmap` | `root` | Run 714263 only after 994029, closing the sqlite-to-obsidian Kuma residual. |
| `state:step:fb24db267874c3211207` | `codex-roadmap` | `root` | Run 812553 after 302284, using prompt-history as the canonical primary repo. |
| `state:step:4b619576fe52c78445ba` | `codex-roadmap` | `root` | Verify the corresponding live/runtime import/backfill/readback during the infrastructure closure tasks above. |
| `state:phase:2ec4595cf61c613d6646` | `personalhub` | `root` | Phase 4 — 707603 Git History / restore |
| `state:phase:3bccf071755721ed153c` | `codex-roadmap` | `root` | Phase 4 — Notification and checkpoint infrastructure |
| `state:step:89469e41b023f86eb4aa` | `personalhub` | `root` | Run 707603 on the resulting schema. |
| `state:step:18a44d989857a75fd450` | `personalhub` | `root` | Validate Git Data / Global History / restore only on safe copies/staging. |
| `state:step:559ea5622b4f97cef5a0` | `codex-roadmap` | `root` | After sufficient Telegram history exists, audit noisy producers and apply only producer-specific fixes; verify the post-fix notification stream is quieter and still actionable. |
| `state:step:7d61e8468fac8b307a62` | `codex-roadmap` | `root` | Complete the ntfy checkpoint-notification lane and prove accepted Git checkpoint pushes produce one remote notification; details in `CHATGPT-20260924-NTFY-CHECKPOINTS.md`. |
| `state:phase:63077c4cdea14df6395f` | `personalhub` | `root` | Phase 5 — 840907 Datasette Lite offline |
| `state:phase:b5cf99bcc96cf8ed1319` | `codex-roadmap` | `root` | Phase 5 — Conditional/manual project lanes |
| `state:step:14f698729113df1566d8` | `personalhub` | `root` | Run 840907 after 707603. |
| `state:step:555a6c439f1a66a7d01c` | `codex-roadmap` | `root` | Reconcile 181259's missing `gernalix/grindr-web-exporter` remote/single-writer path without guessing. |
| `state:step:2b2909ff2958df515a4c` | `personalhub` | `root` | Verify true offline runtime, detached validated snapshots and acceptable artifact-size impact. |
| `state:step:c578f3ad315b0f463492` | `codex-roadmap` | `root` | After the real Grindr-login prerequisite and repo-routing fix, complete 181259. |
| `state:step:fef7073c11e9c53f99c7` | `codex-roadmap` | `root` | Run 556372 only after 181259 to avoid browser/session contention. |
| `state:step:290feaf2e747dceab62c` | `codex-roadmap` | `root` | Resume 582946 only after the user completes MitID login. |
| `state:step:3c0268068d27f00a899b` | `codex-roadmap` | `root` | Reevaluate 218695 after 582946: cancel it explicitly if native e-Boks export is sufficient; otherwise run it. |
| `state:step:24f1ce6380d233ad4c3e` | `codex-roadmap` | `root` | Resume 588376 only after the old GitHub PAT is manually revoked. |
| `state:phase:5abe58c430bc4e58e182` | `personalhub` | `root` | Phase 6 — 788606 final release preflight |
| `state:phase:84067e30a578ec7e7aef` | `codex-roadmap` | `root` | Phase 6 — Infrastructure branch cleanup |
| `state:step:269d460bc9c8f7f6f98f` | `codex-roadmap` | `root` | After active/integration tasks are terminal, perform the bounded patch-equivalence review and delete only proven-safe infrastructure branches. |
| `state:step:3493812dbfb15ba5079c` | `personalhub` | `root` | Run 788606 with no new features. |
| `state:step:097c406093421d30b617` | `codex-roadmap` | `root` | Re-read every affected remote and retain only canonical branches plus explicitly justified active/seed branches. |
| `state:step:3c1e3041ace1d9459ff5` | `personalhub` | `root` | Pass minification/resource shrink, signing, bundletool/Play gates and bounded emulator smoke. |
| `state:step:ca85ec32e60d1eb8a1a1` | `personalhub` | `root` | Freeze exact final main commit, schema version/identity and final APK/AAB hashes/paths. |
| `state:phase:19472414ba33f00e78ea` | `personalhub` | `root` | Phase 7 — 913264 live DB migration and Pixel cutover |
| `state:phase:bf4ec7e1b332d95a7f00` | `codex-roadmap` | `root` | Phase 7 — Final global gate |
| `state:step:997e9ab1a0748109a2cc` | `codex-roadmap` | `root` | Re-run roadmap Attention/PBF reconciliation and verify every real PBF is completed, intentionally closed, or linked to an active/completed successor. |
| `state:step:a35709005a09b3b892f8` | `personalhub` | `root` | Inventory all viable PH DB sources at cutover (live Pixel DB plus local/export/backup copies), record provenance/timestamps/data freshness, and select the freshest coherent source. |
| `state:step:269fd0d176ce10cbc976` | `personalhub` | `root` | Read the selected freshest source DB schema/identity; when the Pixel source is involved use the explicit Pixel serial. |
| `state:step:45513b096c545fc3e78d` | `codex-roadmap` | `root` | Verify no runaway/model-driven waiting, heartbeat or polling automation remains active. |
| `state:step:087805c7fd0056031b85` | `codex-roadmap` | `root` | Verify Waiting/manual/conditional tasks still match their real prerequisites and no obsolete prompt is launchable. |
| `state:step:3701cf2fffb9850c256e` | `personalhub` | `root` | Take immutable rollback backup of the selected freshest source DB/WAL/SHM and recoverable current APK/reference before any migration/write. |
| `state:step:4ea18b6d9c56ed8adb63` | `codex-roadmap` | `root` | Verify no pending prompt contains model/reasoning execution metadata in its body or a known-invalid hard-coded project route. |
| `state:step:f4d4d4c1788a00a7e81f` | `personalhub` | `root` | Externally migrate a copy of the real DB directly to the frozen final schema. |
| `state:step:24381b8dca9c8d787d0a` | `personalhub` | `root` | Pass SQLite quick_check/integrity/FK and representative-data preservation checks. |
| `state:step:56a7bdf9a5a5ca6e262c` | `codex-roadmap` | `root` | Verify Workflowy/CCS/codex-usage runtime reflects the consolidated metadata/lifecycle behavior. |
| `state:step:5ebc51207dabaeb96be9` | `personalhub` | `root` | Install the exact frozen final APK on the primary Pixel using explicit serial. |
| `state:step:8e8e94ee08904dcfd342` | `codex-roadmap` | `root` | Verify PersonalHub final release/data migration/device acceptance is complete. |
| `state:step:8894fd29bfe2a339c1b4` | `codex-roadmap` | `root` | Verify involved repositories are tested, pushed, clean, and branch cleanup is complete. |
| `state:step:d79d44ce1fc99bea6b13` | `personalhub` | `root` | Verify Home + every module with preserved real data; retain rollback until acceptance. |
| `state:step:3212129bc8e8dce87f68` | `codex-roadmap` | `root` | Mark global recovery complete only when every acceptance criterion below is satisfied. |
| `state:phase:e54edc40652bb1cace8e` | `personalhub` | `root` | Phase 8 — Final PH cleanup |
| `state:step:94ab9c6c690888ddd296` | `codex-roadmap` | `root` | When the master recovery returns to PersonalHub, reconcile/integrate the verified Workflowy branch, rerun affected gates, delete the temporary branch and update both PH/global checkpoints. |
| `state:step:c7e52b231a4a102e011c` | `codex-roadmap` | `root` | Run routing-safe CCS successor 896074 only after 302284 PASS; never run superseded 641903. |
| `state:step:f36f54687c18049f1528` | `codex-roadmap` | `root` | Reconcile 181259's nonexistent remote repo before it can become genuinely launchable. |
| `state:step:79218ce9025062e854bd` | `codex-roadmap` | `root` | Resume 302284 only after PH 913264 PASS (or a true PH blocker), using its preserved partial checkpoint; do not redo already-verified work. |
| `state:step:58f5221d703d615b3931` | `codex-roadmap` | `root` | 994029 è completo. 714263 è ora sbloccato dal suo prerequisito, ma resta soggetto all'ordine della master lane e non va lanciato finché PersonalHub P0 è azionabile. |
| `state:step:48baa9fa46efd11cef2a` | `codex-roadmap` | `root` | Keep 812553 behind 222733. |
| `state:step:892a3bf9a32133fef74d` | `codex-roadmap` | `root` | Complete PH P0 chain and final external DB migration/APK/Pixel gate. |
| `state:step:d4ecc67dc0f97dd38e7d` | `codex-roadmap` | `root` | 966124 è completo e non va rilanciato. Quando la master lane consentirà la fase notifiche, passare direttamente all'audit history-based dei producer rumorosi; non rilanciare 422308 e non lanciare 333860. |
| `state:step:d90165d121f5217509b7` | `personalhub` | `root` | Converge every still-relevant non-main PersonalHub branch into `main`: compare against current main for unique semantic work, integrate only valid unabsorbed changes through the canonical single-writer flow, then delete each absorbed/obsolete remote/local branch. |
| `state:step:f19677ccb076ab352bc3` | `personalhub` | `root` | Converge every remaining non-main PH branch: integrate all valid unique work into `main`, prove containment/patch-equivalence, then delete the branch; final remote target is `main` only. |
| `state:step:82734626a9f3256afad6` | `personalhub` | `root` | Prove obsolete PH branches/PRs contain no unique unabsorbed work, then remove them. |
| `state:step:af191398dabc8e389060` | `personalhub` | `root` | Verify no relevant PH PBF/integration/action remains pending. |
| `state:step:110c40096c8641f25b19` | `personalhub` | `root` | End with clean, operational, main-only PersonalHub. |
| `state:step:2c1d09849c6c9628e151` | `personalhub` | `root` | Continue already-running 707603 strictly from its canonical checkpoint after C2 terminalizes; do not claim a duplicate worker. |
| `state:step:55f55ab5697a0dcc9533` | `personalhub` | `root` | Run/review 707603 on the resulting final-ish schema and close it canonically. |
| `state:step:b911f987b9d93f197c67` | `personalhub` | `root` | Run/review 840907, including true offline behavior and artifact-size impact. |
| `state:step:46c738169cfda462b42e` | `personalhub` | `root` | Run/review 788606 and freeze exact release commit, schema version/identity, APK/AAB hashes/paths and shrink state. |
| `state:step:f4c698ff366d3dae4407` | `personalhub` | `root` | Before final migration, inspect the live Pixel DB schema/identity and take immutable backup. |
| `state:step:a9b7929e2d14df79302b` | `personalhub` | `root` | Execute external live DB migration to the exact frozen final schema; preserve rollback and validate data/integrity/FK. |
| `state:step:2068d3c50552345474dc` | `personalhub` | `root` | Install exact final APK on primary Pixel with explicit serial and verify Home + all modules with real data. |
| `state:step:4054f4f049d80c2fbbf5` | `personalhub` | `root` | Verify no open PH PR/issue/action remains relevant/unprocessed. |
| `state:step:075282a1de3792c91e83` | `personalhub` | `root` | Ensure PersonalHub repository ends clean and main-only. |
| `wi:43a64f7bc5704840a0f82cd2ad9172e9` | `codex-roadmap` | `repo` | Reduce C2 single-writer GitHub roundtrip latency |
| `wi:56582a64875f4bcf8df3b708f4a17e95` | `codex-roadmap` | `repo` | Reconcile C2 parent lifecycle after required child receipts change |
| `wi:7237e4d93f2e40b085ccb1c6fac02da9` | `codex-roadmap` | `repo` | Gate child dispatch on applied executor start and reconcile stale parent ownership |
| `wi:7f7fa9817c7741e59ffb9fb773026b65` | `codex-roadmap` | `repo` | Bound C2 orchestrator context with earlier compaction checkpoints |
| `wi:80573401502e4845b6e7520cd0cc79e0` | `github-autosync` | `repo` | Scope repo_single_writer status-any by repository identity |
| `wi:9b5fe27af4814065918a72c1d5b85fc4` | `codex-roadmap` | `repo` | Prevent task-state writes in canonical and runtime C2 worktrees |
| `wi:a392bc6406104fd98a665f42716d88ff` | `fedora-system-monitor` | `repo` | Distinguish intentional Workflowy ExecCondition skip from Kuma outage |
| `wi:db4eb9c690ce4db88f75f0e8823409b0` | `codex-roadmap` | `repo` | Regression: impedire il riavvio automatico del browser RDC da C2 |
| `wi:e0eed3bec9584f3a82f28c77b7a00e38` | `codex-roadmap` | `repo` | Validate repository and publication readiness before C2 dispatch |
| `wi:0575e6982b1e4c32978bb76c45796f1e` | `codex-roadmap` | `repo` | Improve roadmap command failure diagnostics |
| `wi:22a446534a654d8ba868fc7d04c5b175` | `codex-roadmap` | `repo` | Align C2 preparation with non-prompt child executor starts and local-only repositories |
| `wi:23f5aafd9abe4edba5effe14f6af0988` | `codex-roadmap` | `repo` | Batch RDC temporary prompt file preparation |
| `wi:27a7241e16b341278b2359267bfad4f5` | `codex-roadmap` | `repo` | Avoid routine tested-head drift during C2 integration |
| `wi:2f4b651f19734ba8af1191f1a8dfdba0` | `codex-roadmap` | `repo` | Replace model-driven GitHub status polling with receipts |
| `wi:3476c751c7734c9fb11ae4d737143ee3` | `codex-roadmap` | `repo` | Review C2 workflow simplification audit |
| `wi:3ccff086ad6a4a62831353fb3ed8565e` | `chatgpt-rdc-supervisor` | `repo` | ChatGPT RDC: rendere autorevole il fetch conversazione e gestire i 404 |
| `wi:450c736a819842659f8079679976dc54` | `codex-roadmap` | `repo` | Attribute model versus tool and queue latency in C2 |
| `wi:4a9d8d63fcdb4f06849698e2a440dae3` | `codex-roadmap` | `repo` | Chrome watch bridge: terminare il retry infinito quando il debugger è detached |
| `wi:4cbb0e01f57e43f2b1ea5e18138cb77f` | `codex-roadmap` | `repo` | Review roadmap alert one-shot versus persistent behavior audit |
| `wi:4d32aecaaa1f40a2b882cd1b283098c0` | `codex-roadmap` | `repo` | Separate worker completion from supervisor-owned integration |
| `wi:528ed2b27875441eb577c61d660ae65e` | `personalhub` | `repo` | PersonalHub: unificare la presentazione di toast e snackbar |
| `wi:531da330d6c24355ac1db4700a67989f` | `codex-roadmap` | `repo` | Bind restarted manual Codex execution to a managed C2 run |
| `wi:53317b48f00d4b3084353e7470b8fb89` | `codex-roadmap` | `repo` | Allow C2 Inbox triage to continue while a user-deferred row remains pending |
| `wi:58349358cc5f4aa19ebcba3ff3a3152c` | `codex-roadmap` | `repo` | Reduce empty RDC worker-output polling |
| `wi:5c52af51fc494286a05d89eda320607e` | `codex-roadmap` | `repo` | Review roadmap completion alert engine audit |
| `wi:5daced4160754725a783f77976a9295f` | `workflowy-importer` | `repo` | Prevent Workflowy importer tests from changing live services |
| `wi:5f95f420c4fa4315a6b7104adb043096` | `codex-roadmap` | `repo` | C2: aggiungere un comando read-only per lo stato canonico dei work item |
| `wi:6f1e3fffb4ee453fa9ecf96099da2ec9` | `chatgpt-rdc-supervisor` | `repo` | RDC supervisor: recuperare pagine e contesti CDP chiusi con errori osservabili |
| `wi:7dd7e7121347484ab59f9a274598c5a1` | `chatgpt-rdc-supervisor` | `repo` | RDC supervisor watcher: evitare falso positivo di processo già attivo da pgrep |
| `wi:880930830ac54dcdb3ccf8d062f8648b` | `chrome-codex-switcher` | `repo` | Restore Codex Desktop Linux access through the current Cloudflare challenge |
| `wi:91bda0f2a16f43049ab1f15c4d8005b7` | `megavault` | `repo` | Recover the Phase C MegaVault worktree without losing mixed changes |
| `wi:92343c3e9477413b86378a2cc399d05c` | `codex-roadmap` | `repo` | C2: rendere ripetibile il commit del runbook con checkout sporco |
| `wi:948b530657cb46c78a5e403826e2b7f4` | `codex-roadmap` | `repo` | Reconcile MegaVault and C2 project identity mappings before routing |
| `wi:94bef287ab7a4dc7960a084a9ab6a72f` | `chatgpt-rdc-supervisor` | `repo` | RDC supervisor: impedire invii duplicati tra percorso manuale e automatico |
| `wi:9e30e4d3e93c4881831529b1ab7cf726` | `codex-roadmap` | `repo` | Make repo_single_writer discover eligible PRs consistently |
| `wi:b4973cff2a6449bfa8e93af99d71ed7a` | `codex-roadmap` | `repo` | Aggiungere la riconciliazione di progetto prima dei batch C2 |
| `wi:b6eeb6db003143bd8d9031ebeba1c912` | `codex-roadmap` | `repo` | Reduce RDC short-command startup latency |
| `wi:be3cd0afad414f6297bc52155eceb0b1` | `codex-roadmap` | `repo` | Resume bulk Inbox triage safely after GitHub API rate limits |
| `wi:c55c1af448494a38a8f1350946a45caa` | `codex-roadmap` | `repo` | C2 supervisor: documentare e velocizzare il bootstrap manuale degli executor |
| `wi:c613a965f8a340f7906e512168c6626e` | `chatgpt-rdc-supervisor` | `repo` | RDC supervisor: definire soglie di stall e recovery basate su evidenza dinamica |
| `wi:d0204d0bcf174d42ba382f8ff89661f0` | `workflowy-importer` | `repo` | Deduplicate equivalent Workflowy roadmap order mutations |
| `wi:daad704307a448e09f7b32b903939a52` | `codex-roadmap` | `repo` | C2 worktree integration: isolare le modifiche concorrenti e prevenire contaminazione |
| `wi:db9f575d8f3a40e08fb16dec95a2ad11` | `chatgpt-rdc-supervisor` | `repo` | RDC supervisor: aggiornare i selettori DOM per stato auth, composer e turni |
| `wi:e47e711db12d48aab86327770945407a` | `workflowy-importer` | `repo` | Reduce Workflowy roadmap sync wall time using recorded timing evidence |
| `wi:e9752f40936a4cfcbd5c1995de397a23` | `fedora-system-monitor` | `repo` | Fedora System Monitor: attribuire memoria Chrome a tab e conservare storico top-N |
| `wi:faf3525f8b624553bd6c9921fa8efd5f` | `chatgpt-rdc-supervisor` | `repo` | RDC supervisor: correggere l’invio del prompt dal composer corrente |
| `wi:fd61fd5e14ff4cb7a83c3bcd8c5c864c` | `codex-roadmap` | `repo` | Make executor-start reliable when worker GitHub egress is unavailable |
| `task:CHATGPT-20260924-GLOBAL-RECOVERY` | `codex-roadmap` | `root` | Operational task state — global roadmap recovery |
| `task:CHATGPT-20260924-INFRA-BRANCH-CLEANUP` | `codex-roadmap` | `root` | Operational task state — infrastructure branch cleanup |
| `task:CHATGPT-20260924-NTFY-CHECKPOINTS` | `codex-roadmap` | `root` | Operational task state — checkpoint notifications via ntfy |
| `task:CHATGPT-20260924-PERSONALHUB-P0` | `personalhub` | `root` | Operational task state — PersonalHub P0 |
| `task:CHATGPT-20260924-TELEGRAM-NOTIFICATION-HYGIENE` | `fedora-system-monitor` | `root` | Operational task state — Telegram notification hygiene |
| `task:CHATGPT-20260925-ADB-KEEPER-LATENCY` | `adb-device-keeper` | `root` | Operational task state — ADB Wi-Fi keeper latency |
| `wi:b9e561a89cd64ec1b344d4becb958651` | `codex-roadmap` | `repo` | Riconciliare RUNNING C2 con esecuzioni realmente vive |
| `wi:787f93c506dd4f3f8be56439372529db` | `codex-roadmap` | `repo` | C2 PH cutover + canonical temporary lane override |
| `wi:6d318704d7bd441c930832c927116a97` | `codex-roadmap` | `repo` | Rendere idempotente il CLI execution override C2 |
| `wi:e1373812bc1444488c824c0e57812fc8` | `codex-roadmap` | `repo` | Rimuovere special-case PH e implementare override execution canonico |
| `wi:cbaeaf6d11924d2297ea512bb626eb92` | `codex-roadmap` | `repo` | C2: Recheck recurrence of Kuma monitor 73 history degradation |
| `wi:f2d5d81a952b47b1bd4fa4c07d175265` | `codex-roadmap` | `repo` | C2 Git guard: commit su branch emette errore pack-refs ambiguo pur riuscendo |
| `wi:3c7c9af3af3141b28b44f6d0016e41a4` | `chatgpt-rdc-supervisor` | `repo` | C2 supervisor: terminal workers restano abilitati e possono contendere la lane |
| `wi:ff254f4139444dc8909c96324bb9a588` | `codex-roadmap` | `semantic` | Diagnose and fix ChatGPT Desktop memory crash via RDC |
| `wi:b45503242af34c10ba32832d0645dbc6` | `codex-roadmap` | `repo` | C2 import: discendenti task-state obsoleti restano operativi sotto root waiting |
| `wi:0fa0c1ccfc3d4d269d28225ee81161bc` | `codex-roadmap` | `repo` | C2 prompt routing: repo canonico e-Boks resta MegaVault dopo la verifica del nuovo repo |
| `wi:cc78ff4dcaf942f998d821fb48826d23` | `grindr-favorites-monitor` | `repo` | Rendere immediato il profile_id dalle foto Grindr scaricate |
