# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, in parole semplici, **perché ogni task richiede ancora Codex e se conviene lanciarlo come Prompt normale oppure Goal**. Tutto ciò che è eseguibile direttamente sui repository remoti resta fuori dalla coda Codex.

L'ordine della tabella coincide con `roadmap.md` ed è già ottimizzato per ridurre blocchi e lavoro duplicato. Le motivazioni specifiche stanno soltanto nelle righe dei task, così completamento e rinumerazione della roadmap non lasciano descrizioni introduttive obsolete.

|   # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/personalhub-play-release-local-validation]] | Il primo ciclo `294731` si è fermato correttamente sul Play preflight rosso senza fare build/emulatore. La regressione Gradle e il gate remoto vengono risolti fuori da Codex; il retry resta solo perché richiede Fedora reale, keystore/Maps secret locali, AAB firmato e smoke dell'APK set derivato dall'AAB su `Pixel_8a`. Prompt pin-nato all'HEAD remoto già verificato: nessuna nuova diagnosi CI. **Prompt**, GPT-5.6 Luna/low + FAST. | low | Prompt |
| 2 | [[prompts/datasette5-personalhub-explorer-security-deploy]] | Il codice remoto ha già reso esplicito l'accesso `root` a browse/SQL read-only su `personalhub_read` e i test negano anonimo/write. Resta Codex perché servono ambiente Datasette 1.0a38 reale, profilo/segreti Oracle e deploy/readback autenticato. **Prompt**, GPT-5.6 Terra/medium + STRICT. | medium | Prompt |
| 3 | [[prompts/personalhub-datasette-lite-offline-runtime]] | PH ha già snapshot read-only, shell Data Explorer local/remote, contratto cross-feature e accessi contestuali da tutti e sei i moduli, WebView isolata, configurazione e docs sul branch dedicato. Resta la parte non eseguibile via GitHub: vendorizzare/pinnare Datasette Lite+Pyodide senza fetch esterni, build e test Android, prova realmente offline, QA remoto autenticato, merge/release/device. L'integrazione WebAssembly/WebView giustifica **GPT-5.6 Sol/medium + STANDARD**. | medium | Prompt |
| 4 | [[prompts/logseq-updates-pat-safety-closure]] | Il PAT è già rimosso dal tree corrente ma resta nella history. Il rewrite è pre-localizzato con helper pin e gate fail-closed; servono comunque mirror/force-push autenticato, verifica credential e aggiornamento mirato MegaVault. **Prompt**, GPT-5.6 Sol/medium + STRICT. | medium | Prompt |
| 5 | [[prompts/fedora-runtime-validation]] | `362714` ha già completato deploy e sincronizzazione runtime; resta solo un `kuma-configure` bounded e readback #39/#40 sul Fedora reale dopo login umano nel profilo Chrome canonico. **Prompt**, GPT-5.5/low + FAST. | low | Prompt |

## Lavoro remoto escluso dalla roadmap

La campagna CI consolidata identificata da `483921` non è un task Codex: l'handoff autorevole `MegaVault/ai/repository-ci-handoff.json` dichiara `next_executor=chatgpt_github`, e il README vieta di occupare la roadmap con modifiche che ChatGPT può fare direttamente via GitHub. Le istruzioni restano in `handoffs/retained-repositories-github-ci-completion.md`.
