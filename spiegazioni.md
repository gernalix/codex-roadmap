# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, in parole semplici, **perché ogni task vale la pena di essere fatto e cosa migliorerà concretamente**. I dettagli tecnici restano nei singoli prompt.

|   # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/fedora-storage-root-cause-and-kuma-heartbeat-recovery]] | **Perché è importante:** Fedora Storage ha sia un vero problema di spazio sia heartbeat Kuma intermittenti. Il task ripristina gli heartbeat e attribuisce il filesystem esatto; se per liberare spazio servono decisioni sui dati personali, lascia l'alert correttamente visibile ma chiude la diagnosi con quantità e azione precise invece di bloccare tutta la roadmap. | medium | Prompt |
| 2 | [[prompts/personalhub-places-checkin-attempt-journal]] | **Perché è importante:** quando un check-in fallisce oggi manca la prova di cosa sia successo. Il task registra ogni tentativo e le candidate utili al debugging senza creare visite false. Nella stessa unica sessione emulator chiude anche il piccolo debito UI Hub/episodi con un test dedicato emulator-safe. GPT-5.5 Medium + STRICT basta perché schema e lifecycle sono già pre-localizzati. | medium | Goal |
| 3 | [[prompts/personalhub-random-timer-background-deadline]] | **Perché è importante:** il Random Timer deve completarsi e notificare anche con app non aperta. Riusa lo scheduler Android esistente e conclude la campagna con un solo build, un solo APK Pixel-tested e la stessa identica artefatto consegnato. | medium | Goal |
| 4 | [[prompts/repository-publication-secret-audit]] | **Perché è importante:** prima di cambiare visibility bisogna controllare history, tree e workflow senza esporre secret nei log. Lo scan è batch/deterministico, quindi GPT-5.5 Medium è sufficiente; il task produce anche un handoff per la CI, ma la modifica dei workflow GitHub verrà fatta direttamente in chat e non consumerà quota Codex. | medium | Goal |
