# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, in parole semplici, **perché ogni task richiede ancora Codex e se conviene lanciarlo come Prompt normale oppure Goal**. Tutto ciò che è eseguibile direttamente sui repository remoti resta fuori dalla coda Codex.

L'ordine della tabella coincide con `roadmap.md` ed è già ottimizzato per ridurre blocchi e lavoro duplicato. Le motivazioni specifiche stanno soltanto nelle righe dei task, così completamento e rinumerazione della roadmap non lasciano descrizioni introduttive obsolete.

|   # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/adb-device-keeper-runtime-redeploy]] | Il remoto contiene già fix, verifier bounded e CI verde; resta solo il lavoro impossibile da fare via GitHub: pull/deploy sul Fedora reale e un unico disconnect/reconnect del Pixel fisico. **Prompt**, GPT-5.5/low + FAST. | low | Prompt |
| 2 | [[prompts/personalhub-play-release-local-validation]] | Tutta la preparazione Play eseguibile da remoto è già nel repo. Restano segreti/runtime locali: AAB firmato col keystore canonico, ispezione del bundle e installazione dell'APK set derivato dallo stesso AAB sull'emulatore Pixel_8a. È un gate deterministico ben specificato, quindi `low` è sufficiente. **Prompt**, GPT-5.5/low + FAST. | low | Prompt |
| 3 | [[prompts/logseq-updates-pat-safety-closure]] | Il PAT è già rimosso dal tree corrente ma resta nella history. Il rewrite è pre-localizzato con helper pin e gate fail-closed; servono comunque mirror/force-push autenticato, verifica credential e aggiornamento mirato MegaVault. **Prompt**, GPT-5.5/medium + STRICT. | medium | Prompt |
| 4 | [[prompts/fedora-runtime-validation]] | `362714` ha già completato deploy e sincronizzazione runtime; resta solo un `kuma-configure` bounded e readback #39/#40 sul Fedora reale dopo login umano nel profilo Chrome canonico. **Prompt**, GPT-5.5/low + FAST. | low | Prompt |

## Lavoro remoto escluso dalla roadmap

La campagna CI consolidata identificata da `483921` non è un task Codex: l'handoff autorevole `MegaVault/ai/repository-ci-handoff.json` dichiara `next_executor=chatgpt_github`, e il README vieta di occupare la roadmap con modifiche che ChatGPT può fare direttamente via GitHub. Le istruzioni restano in `handoffs/retained-repositories-github-ci-completion.md`.
