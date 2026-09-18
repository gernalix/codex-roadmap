# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, in parole semplici, **perché ogni task richiede ancora Codex e se conviene lanciarlo come Prompt normale oppure Goal**. Tutto ciò che è eseguibile direttamente sui repository remoti resta fuori dalla coda Codex.

L'ordine evita lavoro duplicato: dopo i due task runtime indipendenti, PersonalHub procede in serie (profili/cleanup Timer → timestamp → Salute schema/history → Salute UI/Hub/Obsidian), poi il branch Salute viene mergiato manualmente e si torna su main per il gate Git History, Datasette Lite e infine Play. La migrazione/rischio-dati di Salute è separata dalla feature/UI per mantenere failure domain chiari.

|   # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/codex-usage-verification-status-deploy]] | Il parser e il backfill sono già corretti su GitHub e la CI del nuovo main è PASS; restano soltanto fast-forward locale, due test mirati, deploy Fedora, un ciclo publisher e readback. **Prompt**, GPT-5.6 Luna/low. | low | Prompt |
| 2 | [[prompts/datasette5-personalhub-explorer-security-deploy]] | Il codice remoto contiene già FK cross-modulo, Context graph deduplicato e temporal graph separato. Resta Codex esclusivamente per test nel runtime Datasette, deploy Oracle e readback reale. **Prompt**, GPT-5.6 Terra/medium + STRICT. | medium | Prompt |
| 3 | [[prompts/personalhub-global-profiles-timer-demotion]] | Il branch PH contiene già l'implementazione remota dei profili globali e la rimozione delle superfici duplicate dal Timer. Resta Codex perché servono compile/consumer closure, fault injection sullo switch DB, riconciliazione widget/alarm/geofence e rimozione sicura del codice Timer interno ancora intrecciato. **Prompt**, GPT-5.6 Sol/medium + STRICT. | medium | Prompt |
| 4 | [[prompts/personalhub-epoch-timestamps-migration]] | Il contratto HubTimestamp e lo scanner sono già nel branch; resta audit/migrazione mirata dei veri timestamp residui e QA timezone/profile. È rischio-dati e richiede toolchain locale + eventuale schema export + AVD. **Prompt**, GPT-5.6 Sol/medium + STRICT. | medium | Prompt |
| 5 | [[prompts/personalhub-salute-canonical-integration]] | Il branch Salute contiene già modello dati e contratto patch. Questa fase fa solo schema Room/migration, sample/turnaround, AI persistence e history sintetica: separata dalla UI per non mischiare rischio-dati e feature ordinarie. **Prompt**, GPT-5.6 Terra/medium + STRICT. | medium | Prompt |
| 6 | [[prompts/personalhub-salute-ui-hub-obsidian]] | Dopo lo schema PASS, sostituisce il consumer esterno, collega Salute a Hub/Temporal/Datasette, genera la proiezione Obsidian e chiude la UI Android minimale con QA AVD. Il branch resta separato per review/merge manuale. **Prompt**, GPT-5.6 Terra/medium + STANDARD. | medium | Prompt |
| 7 | [[prompts/personalhub-git-history-data-sync-validation]] | Dopo il merge manuale di Salute, Git Data/History va validato sul main con profili, timestamp epoch-ms e health_* inclusi. Resta Codex per fault injection, fake GitHub, restore/revert e AVD. **Prompt**, GPT-5.6 Sol/medium + STRICT. | medium | Prompt |
| 8 | [[prompts/personalhub-datasette-lite-offline-runtime]] | Dopo il gate Git History, completa Datasette Lite offline e la presentazione relazionale/temporale includendo Salute. Richiede build e QA Android. **Prompt**, GPT-5.6 Sol/medium + STANDARD. | medium | Prompt |
| 9 | [[prompts/personalhub-play-release-local-validation]] | Dopo Datasette Lite valida l'AAB finale versione 51: signing, manifest, 16 KiB e smoke dell'APK set derivato dall'AAB su Pixel_8a. **Prompt**, GPT-5.6 Luna/low + FAST. | low | Prompt |
| 10 | [[prompts/logseq-updates-pat-safety-closure]] | Il PAT è già rimosso dal tree corrente ma resta nella history. Serve Codex per cambio default branch, rewrite fail-closed, verifica credential e aggiornamento MegaVault. È indipendente dalla scelta Obsidian per Salute. **Prompt**, GPT-5.6 Sol/medium + STRICT. | medium | Prompt |
| 11 | [[prompts/fedora-runtime-validation]] | Il deploy runtime è già completato; resta solo kuma-configure bounded e readback #39/#40 sul Fedora reale dopo login umano. **Prompt**, GPT-5.6 Luna/low + FAST. | low | Prompt |

## Lavoro remoto escluso dalla roadmap

La campagna CI consolidata identificata da 483921 non è un task Codex: l'handoff autorevole MegaVault/ai/repository-ci-handoff.json dichiara next_executor=chatgpt_github, e il README vieta di occupare la roadmap con modifiche che ChatGPT può fare direttamente via GitHub.
