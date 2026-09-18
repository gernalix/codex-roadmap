# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi **perché ogni task richiede ancora Codex, quale modello usare e quali dipendenze rispettare**. Tutto ciò che è eseguibile direttamente sui repository remoti resta fuori dalla coda Codex.

PersonalHub usa ora `main` come unica base remota persistente: i vecchi branch feature sono già stati integrati/eliminati. Le fasi PH non devono ricrearli né dipendere da merge manuali tra prompt. Ogni fase parte dal `main` validato dalla precedente e, dopo PASS, pubblica il proprio risultato su `main`.

## Dipendenze e parallelismo

Catena PH obbligatoriamente seriale:

`918274 → 461839 → 418763 → 724615 → 582741 → 671904 → 845312 → 672418 → 861305 → 294731`

Inoltre `527184` è indipendente dalle prime fasi PH ma deve essere PASS **prima di 861305**, perché il QA Datasette Lite deve confrontarsi con il runtime server già distribuito.

Regole pratiche:
- `468205` è indipendente e non usa MegaVault: può correre in parallelo con qualsiasi altro task.
- `518264` modifica il checkout canonico MegaVault e fa una riscrittura della history: non lanciarlo insieme a task che usano MegaVault. Può invece correre insieme a `468205`.
- `643817` ActivityWatch è indipendente dalla catena PH e può correre insieme a un task PH, ma non insieme a `690049`; entrambi toccano Uptime Kuma. Per ridurre interferenze sulla VM Oracle, evita anche di sovrapporlo a `527184`.
- `527184` può correre in parallelo con la catena PH e va chiuso prima di `861305`.
- `690049` può correre in parallelo con la catena PH dopo il login umano a Kuma, purché `643817` non sia in esecuzione.
- due task PH non vanno mai eseguiti contemporaneamente.

`roadmap_finish.py` gestisce completion out-of-order e race di push della roadmap: un task laterale completato mentre il primo elemento è ancora pendente può essere archiviato senza riordinamenti manuali.

|   # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/logseq-updates-pat-safety-closure]] | Bonifica la vecchia history di `logseq_updates`, normalizza il repo a solo `main` e aggiorna MegaVault. History rewrite + stato credenziale giustificano **GPT-5.6 Sol/medium + STRICT**. | medium | Prompt |
| 2 | [[prompts/activity-watch-uploader-runtime-deploy]] | Codice e formato dati sono già remoti: `activity-watch-uploader` contiene solo il servizio, mentre tutti i bucket ActivityWatch vengono versionati nel privato `activity-watch-data` come JSONL giornalieri + metadata, ottimizzati per lettura/modifica ChatGPT. Resta deploy Fedora dei due checkout, lingering/systemd, monitor push Kuma con backup DB e due run end-to-end. **GPT-5.6 Terra/medium + STANDARD**. | medium | Prompt |
| 3 | [[prompts/personalhub-global-profiles-timer-demotion]] | `main` contiene già DatabaseProfiles e la prima de-promozione Timer; restano crash recovery, isolamento runtime dei profili, widget/alarm/geofence e rimozione sicura del codice Timer duplicato. **GPT-5.6 Sol/medium + STRICT**. | medium | Prompt |
| 4 | [[prompts/personalhub-epoch-timestamps-migration]] | Dopo i profili, lascia invariati gli epoch-ms già corretti, migra solo vere violazioni TEXT/ISO e corregge il formatter globale a `EEE d/M/yy HH:mm`. **GPT-5.6 Sol/medium + STRICT**. | medium | Prompt |
| 5 | [[prompts/personalhub-salute-canonical-integration]] | Lo schema PH è ancora v15 e Salute usa ancora il DB esterno: introduce modello Room/migration, sample/turnaround, patch e AI/history sintetica. **GPT-5.6 Terra/medium + STRICT**. | medium | Prompt |
| 6 | [[prompts/personalhub-salute-ui-hub-obsidian|personalhub-salute-ui-hub]] | Dopo lo schema PASS elimina il consumer `salute.db` esterno e collega Salute a UI minima, Hub, Temporal e Datasette. **GPT-5.6 Terra/medium + STANDARD**. | medium | Prompt |
| 7 | [[prompts/personalhub-obsidian-archive-foundation]] | Crea contratto/provider, Markdown/YAML deterministico, manifest, SAF, Settings OFF-by-default e full rebuild. **GPT-5.6 Terra/medium + STANDARD**. | medium | Prompt |
| 8 | [[prompts/personalhub-obsidian-archive-incremental]] | Aggiunge queue/ack indipendenti da Datasette, WorkManager, create/update/delete convergence e recovery. **GPT-5.6 Terra/medium + STANDARD**. | medium | Prompt |
| 9 | [[prompts/personalhub-obsidian-archive-projections]] | Completa provider/grain per tutti i moduli, bounded file count, long-form, wikilink e AVD, lasciando `main` pronto al gate History. **GPT-5.6 Terra/medium + STANDARD**. | medium | Prompt |
| 10 | [[prompts/datasette5-personalhub-explorer-security-deploy]] | Il codice server è già implementato; restano test runtime, deploy Oracle e readback auth/FK/Context/temporal. Indipendente dalle prime fasi PH ma prerequisito di 861305. **GPT-5.6 Terra/medium + STRICT**. | medium | Prompt |
| 11 | [[prompts/personalhub-git-history-data-sync-validation]] | Gate ad alto rischio dopo Salute/Obsidian: group transaction, revert/restore, patch, sharding, firme e bookkeeping tecnico escluso. **GPT-5.6 Sol/medium + STRICT**. | medium | Prompt |
| 12 | [[prompts/personalhub-datasette-lite-offline-runtime]] | Richiede 672418 e 527184 PASS; vendorizza Lite/Pyodide offline, replica FK/Context/temporal server, chiude UI mobile e produce v51. **GPT-5.6 Sol/medium + STANDARD**. | medium | Prompt |
| 13 | [[prompts/personalhub-play-release-local-validation]] | Valida soltanto l'AAB finale v51: signing, manifest, SDK/16 KiB e smoke dell'APK set derivato dall'AAB. **GPT-5.6 Luna/low + FAST**. | low | Prompt |
| 14 | [[prompts/fedora-runtime-validation]] | Deploy già concluso; resta `kuma-configure` bounded e readback #39/#40 dopo login umano nel profilo Chrome canonico. **GPT-5.6 Luna/low + FAST**. | low | Prompt |

## Lavoro remoto escluso dalla roadmap

La campagna CI consolidata identificata da 483921 non è un task Codex: l'handoff autorevole MegaVault/ai/repository-ci-handoff.json dichiara next_executor=chatgpt_github, e il README vieta di occupare la roadmap con modifiche che ChatGPT può fare direttamente via GitHub.

Il contratto architetturale Obsidian è già su PersonalHub `main` in `docs/OBSIDIAN_ARCHIVE.md`; in roadmap restano implementazione/toolchain/QA locali.
