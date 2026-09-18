# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, in parole semplici, **perché ogni task richiede ancora Codex e se conviene lanciarlo come Prompt normale oppure Goal**. Tutto ciò che è eseguibile direttamente sui repository remoti resta fuori dalla coda Codex.

L'ordine evita lavoro duplicato: dopo i due task runtime indipendenti, PersonalHub procede in serie sul branch dedicato (profili/cleanup Timer → audit timestamp mirato), poi torna su main per il gate Git History, Datasette Lite e infine Play. Le attività indipendenti restano dopo la catena PH.

|   # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/codex-usage-verification-status-deploy]] | Il parser e il backfill sono già corretti su GitHub e la CI del nuovo main è PASS; restano soltanto fast-forward locale, due test mirati, deploy Fedora, un ciclo publisher e readback. **Prompt**, GPT-5.6 Luna/low. | low | Prompt |
| 2 | [[prompts/datasette5-personalhub-explorer-security-deploy]] | Il codice remoto contiene già FK cross-modulo, Context graph deduplicato e temporal graph separato. Resta Codex esclusivamente per test nel runtime Datasette, deploy Oracle e readback reale. **Prompt**, GPT-5.6 Terra/medium + STRICT. | medium | Prompt |
| 3 | [[prompts/personalhub-global-profiles-timer-demotion]] | Il branch PH contiene già l'implementazione remota dei profili globali e la rimozione delle superfici duplicate dal Timer. Resta Codex perché servono compile/consumer closure, fault injection sullo switch DB, riconciliazione widget/alarm/geofence e rimozione sicura del codice Timer interno ancora intrecciato. **Prompt**, GPT-5.6 Sol/medium + STRICT. | medium | Prompt |
| 4 | [[prompts/personalhub-epoch-timestamps-migration]] | Il contratto HubTimestamp e lo scanner sono già nel branch; resta la migrazione Room v15→v16 di timestamp TEXT/ISO a INTEGER epoch-ms, l'aggiornamento dei consumer e la QA timezone/profile. È rischio-dati e richiede toolchain locale + schema export + AVD. Dopo PASS integra il branch in main. **Prompt**, GPT-5.6 Sol/medium + STRICT. | medium | Prompt |
| 5 | [[prompts/personalhub-salute-canonical-integration]] | Il branch `feature/salute-canonical-domain` contiene già il modello dati, il workflow ChatGPT→PH e due SVG di prodotto. Resta Codex perché bisogna trasformare l'attuale Salute esterno in schema Room canonico, eseguire migration/schema export, consumer closure, Hub/Temporal, patch/history, Obsidian deterministico e QA AVD senza committare dati sanitari reali. Il branch resta separato per review/merge manuale dell'utente. **Prompt**, GPT-5.6 Sol/medium + STRICT. | medium | Prompt |
| 6 | [[prompts/personalhub-git-history-data-sync-validation]] | Git Data/History è già implementato; dopo Salute va validato sul nuovo main con profili globali, timestamp epoch-ms e tabelle health incluse. Resta Codex per compile, fault injection, fake GitHub, restore/revert e AVD. **Prompt**, GPT-5.6 Sol/medium + STRICT. | medium | Prompt |
| 7 | [[prompts/personalhub-datasette-lite-offline-runtime]] | Dopo il gate Git History, completa il runtime Datasette Lite offline e la presentazione relazionale/temporale includendo anche il nuovo dominio Salute. Richiede build e QA Android. **Prompt**, GPT-5.6 Sol/medium + STANDARD. | medium | Prompt |
| 8 | [[prompts/personalhub-play-release-local-validation]] | Dopo Datasette Lite valida l'AAB finale versione 52: signing, manifest, 16 KiB e smoke dell'APK set derivato dall'AAB su Pixel_8a. **Prompt**, GPT-5.6 Luna/low + FAST. | low | Prompt |
| 9 | [[prompts/logseq-updates-pat-safety-closure]] | Il PAT è già rimosso dal tree corrente ma resta nella history. Serve Codex per cambio default branch, rewrite fail-closed, verifica credential e aggiornamento MegaVault. È indipendente dalla scelta Obsidian per Salute. **Prompt**, GPT-5.6 Sol/medium + STRICT. | medium | Prompt |
| 10 | [[prompts/fedora-runtime-validation]] | Il deploy runtime è già completato; resta solo kuma-configure bounded e readback #39/#40 sul Fedora reale dopo login umano. **Prompt**, GPT-5.6 Luna/low + FAST. | low | Prompt |

## Lavoro remoto escluso dalla roadmap

La campagna CI consolidata identificata da 483921 non è un task Codex: l'handoff autorevole MegaVault/ai/repository-ci-handoff.json dichiara next_executor=chatgpt_github, e il README vieta di occupare la roadmap con modifiche che ChatGPT può fare direttamente via GitHub.
