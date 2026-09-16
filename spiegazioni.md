# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

La roadmap contiene solo lavoro che richiede Codex/local runtime. Le modifiche puramente remote/documentali vengono fatte direttamente in chat; dopo PASS non si apre un follow-up senza nuova evidenza concreta.

| # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | --- | --- | --- | --- |
| 1 | [[prompts/personalhub-startup-pixel-verification]] | **Cosa fa:** chiude il blocker startup sul Pixel 8a con tre cold start e un tap innocuo per provare che l'interfaccia risponde davvero; solo se fallisce usa una Perfetto + un fix mirato. **Perché ora:** è un malfunzionamento reale già pre-localizzato; non va mescolato alla successiva CI. | medium | Prompt |
| 2 | [[prompts/codex-usage-fedora-only-runtime-cutover]] | **Cosa fa:** rende Fedora l'unico runtime di `codex-usage-monitor`, preserva eventuale storico Oracle, spegne solo il vecchio monitor VM e aggiunge nello stesso pass la CI del repo. **Perché:** evita di riaprire lo stesso progetto in un secondo task CI e chiude una migrazione cross-host ad alto rischio. | medium | Goal |
| 3 | [[prompts/repository-publication-secret-audit]] | **Cosa fa:** in un'unica sessione protegge i repo pubblici classificati PRIVATE, scansiona history/tree/Actions dei candidati e applica la visibility finale solo ai repo realmente pronti. **Perché:** audit e applicazione usano lo stesso inventario/matrice; separarli duplicava contesto e tool-call. | medium | Goal |
| 4 | [[prompts/personalhub-github-actions-ci-and-fedora-runner]] | **Cosa fa:** imposta la CI PersonalHub in base alla visibility finale, usando hosted se pubblico o runner Fedora PH-only solo se resta privato. **Perché:** PH è il progetto attivo principale e la strategia dipende dal task 3. | medium | Goal |
| 5 | [[prompts/python-automation-github-actions-ci]] | **Cosa fa:** CI soltanto per `github-autosync` e `workflowy-import`. **Perché:** `codex-usage-monitor` è già coperto dal task 2 e `codex-roadmap` viene coperto direttamente da ChatGPT, quindi Codex non deve rileggerli. | low | Goal |
| 6 | [[prompts/standalone-android-github-actions-ci]] | **Cosa fa:** host gate minimo per `SuperContacts`, `MultiTimeTracker`, `android-app-template`, con emulator solo quando pubblico e utile. **Perché:** task deterministico e separato dalla toolchain PH. | low | Goal |
| 7 | [[prompts/browser-downloader-github-actions-ci]] | **Cosa fa:** fixture/mock CI per `whatsapp-watcher`, `chatgpt_tab_watcher_v1`, `WindowTabNotes`, `yt_dlp_downloader`. **Perché:** i repo volutamente privati/personali sono stati esclusi; resta solo la copertura con reale beneficio di pubblicazione/CI. | medium | Goal |
| 8 | [[prompts/fedora-tools-github-actions-ci]] | **Cosa fa:** CI sandboxabile per `fedora-system-monitor`, `fedora-t7-backup`, `app_lifecycle_monitor`, `codex-session-logger`. **Perché:** `vm_oracle` e `oracle-backup-service` restano privati e non meritano una campagna CI generica senza un requisito concreto. | low | Goal |
| 9 | [[prompts/retire-obsolete-standalone-module-repositories]] | **Cosa fa:** elimina in sicurezza `Soldi`, `wordpulse`, `Sostanze`, `Luoghi`, `luoghi-app`, preservando identità/storia in MegaVault e ripulendo riferimenti operativi. **Perché in fondo:** è distruttivo e un dirty worktree non deve bloccare tutta la campagna precedente. | medium | Goal |
