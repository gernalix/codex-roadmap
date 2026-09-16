# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, in parole semplici, **perché ogni task richiede ancora Codex e se conviene lanciarlo come Prompt normale oppure Goal**. Tutto ciò che è eseguibile direttamente sui repository remoti resta fuori dalla coda Codex.

L'ordine della tabella coincide con `roadmap.md` ed è già ottimizzato per ridurre blocchi e lavoro duplicato. Le motivazioni specifiche stanno soltanto nelle righe dei task, così completamento e rinumerazione della roadmap non lasciano descrizioni introduttive obsolete.

|   # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/personalhub-play-release-local-validation]] | Il primo ciclo `294731` si è fermato correttamente sul Play preflight rosso senza fare build/emulatore. La regressione Gradle e il gate remoto vengono risolti fuori da Codex; il retry resta solo perché richiede Fedora reale, keystore/Maps secret locali, AAB firmato e smoke dell'APK set derivato dall'AAB su `Pixel_8a`. Prompt pin-nato all'HEAD remoto già verificato: nessuna nuova diagnosi CI. **Prompt**, GPT-5.5/low + FAST. | low | Prompt |
| 2 | [[prompts/logseq-updates-pat-safety-closure]] | Il PAT è già rimosso dal tree corrente ma resta nella history. Il rewrite è pre-localizzato con helper pin e gate fail-closed; servono comunque mirror/force-push autenticato, verifica credential e aggiornamento mirato MegaVault. **Prompt**, GPT-5.5/medium + STRICT. | medium | Prompt |
| 3 | [[prompts/fedora-runtime-validation]] | `362714` ha già completato deploy e sincronizzazione runtime; resta solo un `kuma-configure` bounded e readback #39/#40 sul Fedora reale dopo login umano nel profilo Chrome canonico. **Prompt**, GPT-5.5/low + FAST. | low | Prompt |

## Lavoro remoto escluso dalla roadmap

La campagna CI consolidata identificata da `483921` non è un task Codex: l'handoff autorevole `MegaVault/ai/repository-ci-handoff.json` dichiara `next_executor=chatgpt_github`, e il README vieta di occupare la roadmap con modifiche che ChatGPT può fare direttamente via GitHub. Le istruzioni restano in `handoffs/retained-repositories-github-ci-completion.md`.
