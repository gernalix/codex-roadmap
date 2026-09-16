# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

La roadmap contiene solo lavoro che richiede Codex/local runtime. Le modifiche puramente remote/documentali vengono fatte direttamente in chat; dopo PASS non si apre un follow-up senza nuova evidenza concreta.

| # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | --- | --- | --- | --- |
| 1 | [[prompts/codex-usage-fedora-only-runtime-cutover]] | **Cosa fa:** rende Fedora l'unico runtime di `codex-usage-monitor`, preserva eventuale storico Oracle, spegne solo il vecchio monitor VM e aggiunge nello stesso pass la CI del repo. **Perché:** chiude prima il sistema che rende disponibili automaticamente i dump Codex senza copia-incolla. | medium | Goal |
| 2 | [[prompts/generate-repository-retention-checklist]] | **Cosa fa:** genera in MegaVault una lista `- [ ] repo` di tutti i repository posseduti, ordinata per data dell'ultimo commit dal più recente al più vecchio, e salva l'hash iniziale. **Poi si ferma:** l'utente deve mettere `[x]` soltanto ai repo che vuole conservare. | low | Prompt |
| 3 | [[prompts/archive-and-retire-unchecked-repositories]] | **Cosa fa:** solo dopo la modifica umana della checklist, crea un unico ZIP verificato con storia Git completa e stato locale dei repo `[ ]`, quindi elimina esclusivamente quelli non selezionati da GitHub e dal PC. **Perché:** rimuove prima i repo obsoleti, evitando audit e CI inutili, ma conserva un recupero offline completo. | medium | Goal |
| 4 | [[prompts/repository-publication-secret-audit]] | **Cosa fa:** sui soli repo rimasti, protegge quelli pubblici classificati PRIVATE, scansiona history/tree/Actions dei candidati e applica la visibility finale solo ai repo realmente pronti. **Perché:** la decisione pubblico/privato avviene dopo il cleanup, quindi non si spendono token sui repo eliminati. | medium | Goal |
| 5 | [[prompts/personalhub-github-actions-ci-and-fedora-runner]] | **Cosa fa:** imposta la CI PersonalHub in base alla visibility finale, usando hosted se pubblico o runner Fedora PH-only solo se resta privato. | medium | Goal |
| 6 | [[prompts/python-automation-github-actions-ci]] | **Cosa fa:** CI per `github-autosync` e `workflowy-import` se sono ancora presenti dopo la retention review. `codex-usage-monitor` è già coperto dal task 1 e `codex-roadmap` direttamente da ChatGPT. | low | Goal |
| 7 | [[prompts/standalone-android-github-actions-ci]] | **Cosa fa:** host gate minimo per `SuperContacts`, `MultiTimeTracker`, `android-app-template` rimasti, con emulator solo quando pubblico e utile. | low | Goal |
| 8 | [[prompts/browser-downloader-github-actions-ci]] | **Cosa fa:** fixture/mock CI per `whatsapp-watcher`, `chatgpt_tab_watcher_v1`, `WindowTabNotes`, `yt_dlp_downloader` rimasti dopo la retention review. | medium | Goal |
| 9 | [[prompts/fedora-tools-github-actions-ci]] | **Cosa fa:** CI sandboxabile per `fedora-system-monitor`, `fedora-t7-backup`, `app_lifecycle_monitor`, `codex-session-logger` rimasti. I repo infrastrutturali volutamente privati restano fuori dalla campagna generica. | low | Goal |
