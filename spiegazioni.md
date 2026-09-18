# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, in parole semplici, **perché ogni task richiede ancora Codex e se conviene lanciarlo come Prompt normale oppure Goal**. Tutto ciò che è eseguibile direttamente sui repository remoti resta fuori dalla coda Codex.

L'ordine è ottimizzato per evitare lavoro duplicato: prima il piccolo deploy del monitor, poi il backend Datasette richiesto dal Data Explorer Android, quindi il completamento Android e solo dopo la validazione Play della build risultante. Le attività indipendenti restano in coda senza spezzare questa dipendenza.

|   # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/codex-usage-verification-status-deploy]] | Il parser e il backfill sono già corretti su GitHub e la CI del nuovo `main` è PASS; restano soltanto fast-forward locale, due test mirati, deploy del runtime Fedora, un ciclo publisher e readback del singolo ciclo `742591`. I vecchi branch remoti erano già integrati/superseded e sono stati eliminati: resta solo `main`. **Prompt**, GPT-5.6 Luna/low; MegaVault non necessario. | low | Prompt |
| 2 | [[prompts/datasette5-personalhub-explorer-security-deploy]] | Il codice remoto contiene già FK cross-modulo, Context graph deduplicato e temporal graph separato: i match già spiegati da FK/Context non generano backlink duplicati, WordPulse usa activity burst e People solo eventi timestampati. Resta Codex esclusivamente per eseguire test nel runtime Datasette 1.0a38, deploy Oracle e readback reale. **Prompt**, GPT-5.6 Terra/medium + STRICT. | medium | Prompt |
| 3 | [[prompts/personalhub-datasette-lite-offline-runtime]] | PH documenta già la stessa policy relazionale/temporale del server. Resta Codex perché la sua implementazione locale dipende dal runtime Datasette Lite+Pyodide vendorizzato e richiede build/test Android realmente offline, UI `Related` vs `Temporal`, QA remoto, signing/install/delivery; assorbe anche il regression gate Luoghi già codificato. **Prompt**, GPT-5.6 Sol/medium + STANDARD. | medium | Prompt |
| 4 | [[prompts/personalhub-play-release-local-validation]] | Va eseguito **dopo** `861305`, così valida l'AAB del `main` realmente finalizzato invece del vecchio snapshot pre-Data-Explorer. È un gate meccanico locale: signing, bundle/manifest/16 KiB e smoke dell'APK set derivato dall'AAB su `Pixel_8a`. **Prompt**, GPT-5.6 Luna/low + FAST. | low | Prompt |
| 5 | [[prompts/logseq-updates-pat-safety-closure]] | Il PAT è già rimosso dal tree corrente ma resta nella history. `main` e `master` oggi puntano allo stesso HEAD; il connettore GitHub non può cambiare il default branch, quindi lo stesso task Codex prima imposta `main` come default ed elimina `master`, poi esegue il rewrite fail-closed, verifica credential e aggiorna MegaVault. **Prompt**, GPT-5.6 Sol/medium + STRICT. | medium | Prompt |
| 6 | [[prompts/fedora-runtime-validation]] | `362714` ha già completato deploy e sincronizzazione runtime; resta solo un `kuma-configure` bounded e readback #39/#40 sul Fedora reale dopo login umano nel profilo Chrome canonico. Il repo remoto ha già solo `main`. **Prompt**, GPT-5.6 Luna/low + FAST. | low | Prompt |

## Lavoro remoto escluso dalla roadmap

La campagna CI consolidata identificata da `483921` non è un task Codex: l'handoff autorevole `MegaVault/ai/repository-ci-handoff.json` dichiara `next_executor=chatgpt_github`, e il README vieta di occupare la roadmap con modifiche che ChatGPT può fare direttamente via GitHub. Le istruzioni restano in `handoffs/retained-repositories-github-ci-completion.md`.
