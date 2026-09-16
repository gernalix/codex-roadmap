# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, in parole semplici, **perché ogni task richiede ancora Codex e se conviene lanciarlo come Prompt normale oppure Goal**. Tutto ciò che è eseguibile direttamente sui repository remoti resta fuori dalla coda Codex.

L'ordine numerico riduce blocchi e lavoro duplicato. Il task 1 non implementa più nulla: il refactor MegaVault è già su `master` con CI verde. Restano soltanto il fast-forward del checkout Fedora preservando il checklist locale e due smoke read-only sul DB canonico. Il task 2 è un deploy/runtime gate locale breve e senza prerequisiti umani. Il task 3 è il gate locale Play di PersonalHub e dipende solo dal proprio Play preflight remoto pertinente. Il task 4 può richiedere un'azione esterna sulla credential, quindi viene dopo i task non bloccanti. Il task 5 richiede che l'utente abbia effettuato nuovamente il login a Kuma nel profilo Chrome canonico e per questo resta ultimo.

|   # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/megavault-internal-capsule-boundaries]] | I due tentativi `805417` non hanno modificato nulla. Il secondo ha provato che il checklist locale è disgiunto dai file remoti; il blocker era un requisito errato che pretendeva l'hash pre-sync di `megavault.sqlite`, benché il DB tracked sia legittimamente cambiato sul remoto. Codex deve solo fast-forwardare in sicurezza, preservare gli uncommitted locali, accettare gli aggiornamenti tracked canonici e fare `project-show 23` + `project-path --status 23`. **Prompt**, GPT-5.5/low + FAST. | low | Prompt |
| 2 | [[prompts/adb-device-keeper-runtime-redeploy]] | Il remoto contiene già fix, verifier bounded e CI verde; resta solo il lavoro impossibile da fare via GitHub: pull/deploy sul Fedora reale e un unico disconnect/reconnect del Pixel fisico. **Prompt**, GPT-5.5/low + FAST. | low | Prompt |
| 3 | [[prompts/personalhub-play-release-local-validation]] | Tutta la preparazione Play eseguibile da remoto è già nel repo. Restano segreti/runtime locali: AAB firmato col keystore canonico, ispezione del bundle e installazione dell'APK set derivato dallo stesso AAB sull'emulatore Pixel_8a. **Prompt**, GPT-5.5/low + FAST. | low | Prompt |
| 4 | [[prompts/logseq-updates-pat-safety-closure]] | Il PAT è già rimosso dal tree corrente ma resta nella history. Il rewrite è pre-localizzato con helper pin e gate fail-closed; servono comunque mirror/force-push autenticato, verifica credential e aggiornamento mirato MegaVault. **Prompt**, GPT-5.5/medium + STRICT. | medium | Prompt |
| 5 | [[prompts/fedora-runtime-validation]] | `362714` ha già completato deploy e sincronizzazione runtime; resta solo un `kuma-configure` bounded e readback #39/#40 sul Fedora reale dopo login umano nel profilo Chrome canonico. **Prompt**, GPT-5.5/low + FAST. | low | Prompt |

## Lavoro remoto escluso dalla roadmap

La campagna CI consolidata identificata da `483921` non è un task Codex: l'handoff autorevole `MegaVault/ai/repository-ci-handoff.json` dichiara `next_executor=chatgpt_github`, e il README vieta di occupare la roadmap con modifiche che ChatGPT può fare direttamente via GitHub. Le istruzioni restano in `handoffs/retained-repositories-github-ci-completion.md`.
