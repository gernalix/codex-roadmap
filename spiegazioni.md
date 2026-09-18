# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi **perché ogni task richiede ancora Codex, quale modello usare e quali dipendenze rispettare**. Tutto ciò che è eseguibile direttamente sui repository remoti resta fuori dalla coda Codex.

PersonalHub usa ora `main` come unica base remota persistente: i vecchi branch feature sono già stati integrati/eliminati. Le fasi PH non devono ricrearli né dipendere da merge manuali tra prompt. Ogni fase parte dal `main` validato dalla precedente e, dopo PASS, pubblica il proprio risultato su `main`.

## Dipendenze e parallelismo

`754406` è il bootstrap prioritario del registro PROMPT_ID: eseguilo da solo prima degli altri task che usano o modificano il checkout canonico MegaVault. Dopo il PASS si applicano di nuovo le regole di parallelismo sotto.

Catena PH obbligatoriamente seriale:

`918274 → 461839 → 418763 → 724615 → 582741 → 671904 → 845312 → 672418 → 861305 → 294731`

Inoltre `527184` è indipendente dalle prime fasi PH ma deve essere PASS **prima di 861305**, perché il QA Datasette Lite deve confrontarsi con il runtime server già distribuito.

Regole pratiche:
- `319311` è un deploy/benchmark locale del solo publisher Fedora: è indipendente dalla catena PH e da Uptime Kuma. Per non falsare il benchmark, non sovrapporlo ad altri deploy/benchmark di servizi Fedora; inoltre non lanciarlo durante `255325`, che riscrive il checkout MegaVault mentre `319311` usa MegaVault=FAST.
- `255325` è volutamente l'ultimo task: riscrive la history di `logseq_updates`, modifica il checkout canonico MegaVault e chiude anche il runtime updater Fedora. Eseguilo da solo, non in parallelo con task che usano MegaVault.
- `643817` ActivityWatch è indipendente dalla catena PH e può correre insieme a un task PH, ma non insieme a `690049`; entrambi toccano Uptime Kuma. Per ridurre interferenze sulla VM Oracle, evita anche di sovrapporlo a `527184`.
- `527184` può correre in parallelo con la catena PH e va chiuso prima di `861305`.
- `690049` può correre in parallelo con la catena PH dopo il login umano a Kuma, purché `643817` non sia in esecuzione.
- due task PH non vanno mai eseguiti contemporaneamente.

`roadmap_finish.py` gestisce completion out-of-order e race di push della roadmap: un task laterale completato mentre il primo elemento è ancora pendente può essere archiviato senza riordinamenti manuali.

| # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/megavault-prompt-id-registry-activation]] | Attiva sul Fedora reale lo schema/allocator già implementato, fa backup del DB canonico, backfill degli ID pre-allocator da fonti note, lifecycle del prompt bootstrap, test concorrenza e push del `megavault.sqlite`. Migrazione DB canonica e backfill storico richiedono **GPT-5.6 Terra/medium + STRICT**. | medium | Prompt |
| 2 | [[prompts/codex-usage-publisher-noop-fastpath-deploy]] | Il codice remoto ora evita il full scan di tutti i rollout quando path/size/mtime/ctime sono invariati, invalida il fast-path ai cambi semantici e conserva il full scan se esiste stato pendente. Restano solo deploy del runtime Fedora e benchmark di due run consecutivi sul runtime reale. **GPT-5.6 Luna/low + FAST**. | low | Prompt |
| 3 | [[prompts/activity-watch-uploader-runtime-deploy]] | Il primo ciclo 643817 si è fermato in 74 s su un clone annidato/parziale prima di toccare ActivityWatch/Kuma. ChatGPT ha già aggiunto un bootstrap fail-closed che ripara solo quello stato noto e ha riscritto il prompt per evitare rediscovery/MegaVault lookup e raggruppare i gate. Resta solo runtime reale Fedora+Oracle/Kuma e doppio run E2E. **GPT-5.6 Terra/medium + STANDARD**. | medium | Prompt |
| 4 | [[prompts/personalhub-global-profiles-timer-demotion]] | `main` contiene già DatabaseProfiles e la prima de-promozione Timer; restano crash recovery, isolamento runtime dei profili, widget/alarm/geofence e rimozione sicura del codice Timer duplicato. **GPT-5.6 Sol/medium + STRICT**. | medium | Prompt |
| 5 | [[prompts/personalhub-epoch-timestamps-migration]] | Dopo i profili, lascia invariati gli epoch-ms già corretti, migra solo vere violazioni TEXT/ISO e corregge il formatter globale a `EEE d/M/yy HH:mm`. **GPT-5.6 Sol/medium + STRICT**. | medium | Prompt |
| 6 | [[prompts/personalhub-salute-canonical-integration]] | Lo schema PH è ancora v15 e Salute usa ancora il DB esterno: introduce modello Room/migration, sample/turnaround, patch e AI/history sintetica. **GPT-5.6 Terra/medium + STRICT**. | medium | Prompt |
| 7 | [[prompts/personalhub-salute-ui-hub-obsidian]] | Dopo lo schema PASS elimina il consumer `salute.db` esterno e collega Salute a UI minima, Hub, Temporal e Datasette. **GPT-5.6 Terra/medium + STANDARD**. | medium | Prompt |
| 8 | [[prompts/personalhub-obsidian-archive-foundation]] | Crea contratto/provider, Markdown/YAML deterministico, manifest, SAF, Settings OFF-by-default e full rebuild. **GPT-5.6 Terra/medium + STANDARD**. | medium | Prompt |
| 9 | [[prompts/personalhub-obsidian-archive-incremental]] | Aggiunge queue/ack indipendenti da Datasette, WorkManager, create/update/delete convergence e recovery. **GPT-5.6 Terra/medium + STANDARD**. | medium | Prompt |
| 10 | [[prompts/personalhub-obsidian-archive-projections]] | Completa provider/grain per tutti i moduli, bounded file count, long-form, wikilink e AVD, lasciando `main` pronto al gate History. **GPT-5.6 Terra/medium + STANDARD**. | medium | Prompt |
| 11 | [[prompts/datasette5-personalhub-explorer-security-deploy]] | Il codice server è già implementato; restano test runtime, deploy Oracle e readback auth/FK/Context/temporal. Indipendente dalle prime fasi PH ma prerequisito di 861305. **GPT-5.6 Terra/medium + STRICT**. | medium | Prompt |
| 12 | [[prompts/personalhub-git-history-data-sync-validation]] | Gate ad alto rischio dopo Salute/Obsidian: group transaction, revert/restore, patch, sharding, firme e bookkeeping tecnico escluso. **GPT-5.6 Sol/medium + STRICT**. | medium | Prompt |
| 13 | [[prompts/personalhub-datasette-lite-offline-runtime]] | Richiede 672418 e 527184 PASS; vendorizza Lite/Pyodide offline, replica FK/Context/temporal server, chiude UI mobile e produce v51. **GPT-5.6 Sol/medium + STANDARD**. | medium | Prompt |
| 14 | [[prompts/personalhub-play-release-local-validation]] | Valida soltanto l'AAB finale v51: signing, manifest, SDK/16 KiB e smoke dell'APK set derivato dall'AAB. **GPT-5.6 Luna/low + FAST**. | low | Prompt |
| 15 | [[prompts/fedora-runtime-validation]] | Deploy già concluso; resta `kuma-configure` bounded e readback #39/#40 dopo login umano nel profilo Chrome canonico. **GPT-5.6 Luna/low + FAST**. | low | Prompt |
| 16 | [[prompts/logseq-updates-pat-safety-closure]] | Chiude la bonifica PAT/history e sostituisce il vecchio updater Windows con un updater Fedora x86_64 realmente unattended: risolve live l'ultima build GitHub Actions Linux x64, scarica l'artifact, installa atomicamente l'AppImage, usa un timer systemd user resiliente e invia Telegram sia su successo sia su fallimento. History rewrite + credenziale + runtime install giustificano **GPT-5.6 Sol/medium + STRICT**. | medium | Prompt |

## Lavoro remoto escluso dalla roadmap

La campagna CI consolidata identificata da 483921 non è un task Codex: l'handoff autorevole MegaVault/ai/repository-ci-handoff.json dichiara next_executor=chatgpt_github, e il README vieta di occupare la roadmap con modifiche che ChatGPT può fare direttamente via GitHub.

Il contratto architetturale Obsidian è già su PersonalHub `main` in `docs/OBSIDIAN_ARCHIVE.md`; in roadmap restano implementazione/toolchain/QA locali.
