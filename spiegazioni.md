# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, in parole semplici, **perché ogni task richiede ancora Codex e se conviene lanciarlo come Prompt normale oppure Goal**. Tutto ciò che è eseguibile direttamente sui repository remoti resta fuori dalla coda Codex.

L'ordine è ottimizzato per evitare lavoro duplicato: prima il piccolo deploy del monitor, poi il backend Datasette richiesto dal Data Explorer Android, quindi il completamento Android e solo dopo la validazione Play della build risultante. Le attività indipendenti restano in coda senza spezzare questa dipendenza.

|   # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/codex-usage-verification-status-deploy]] | Il parser e il backfill sono già corretti su GitHub e la CI del nuovo `main` è PASS; restano soltanto fast-forward locale, due test mirati, deploy del runtime Fedora, un ciclo publisher e readback del singolo ciclo `742591`. I vecchi branch remoti erano già integrati/superseded e sono stati eliminati: resta solo `main`. **Prompt**, GPT-5.6 Luna/low; MegaVault non necessario. | low | Prompt |
| 2 | [[prompts/datasette5-personalhub-explorer-security-deploy]] | Il diff di sicurezza del Data Explorer è già stato fast-forwardato in `main` e il vecchio feature branch è stato eliminato. Resta Codex perché servono ambiente Datasette 1.0a38 reale, profilo/segreti Oracle, deploy e readback autenticato. Deve precedere il task Android perché il QA remoto di PH dipende da `personalhub_read`. **Prompt**, GPT-5.6 Terra/medium + STRICT. | medium | Prompt |
| 3 | [[prompts/personalhub-datasette-lite-offline-runtime]] | La shell del Data Explorer è già in `main`; tutti i branch PH obsoleti sono stati rimossi. Architecture boundaries e Play preflight erano PASS sul commit applicativo già integrato. Resta la parte locale difficile: vendorizzare/pinnare Datasette Lite+Pyodide senza fetch runtime, testare offline/read-only, fare QA locale+remota e produrre/installare/consegnare il debug finale. **Prompt**, GPT-5.6 Sol/medium + STANDARD. | medium | Prompt |
| 4 | [[prompts/personalhub-play-release-local-validation]] | Va eseguito **dopo** `861305`, così valida l'AAB del `main` realmente finalizzato invece del vecchio snapshot pre-Data-Explorer. È un gate meccanico locale: signing, bundle/manifest/16 KiB e smoke dell'APK set derivato dall'AAB su `Pixel_8a`. **Prompt**, GPT-5.6 Luna/low + FAST. | low | Prompt |
| 5 | [[prompts/logseq-updates-pat-safety-closure]] | Il PAT è già rimosso dal tree corrente ma resta nella history. `main` e `master` oggi puntano allo stesso HEAD; il connettore GitHub non può cambiare il default branch, quindi lo stesso task Codex prima imposta `main` come default ed elimina `master`, poi esegue il rewrite fail-closed, verifica credential e aggiorna MegaVault. **Prompt**, GPT-5.6 Sol/medium + STRICT. | medium | Prompt |
| 6 | [[prompts/fedora-runtime-validation]] | `362714` ha già completato deploy e sincronizzazione runtime; resta solo un `kuma-configure` bounded e readback #39/#40 sul Fedora reale dopo login umano nel profilo Chrome canonico. Il repo remoto ha già solo `main`. **Prompt**, GPT-5.6 Luna/low + FAST. | low | Prompt |

## Lavoro remoto escluso dalla roadmap

La campagna CI consolidata identificata da `483921` non è un task Codex: l'handoff autorevole `MegaVault/ai/repository-ci-handoff.json` dichiara `next_executor=chatgpt_github`, e il README vieta di occupare la roadmap con modifiche che ChatGPT può fare direttamente via GitHub. Le istruzioni restano in `handoffs/retained-repositories-github-ci-completion.md`.
