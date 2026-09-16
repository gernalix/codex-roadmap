# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, in parole semplici, **perché ogni task vale la pena di essere fatto e cosa migliorerà concretamente**. I dettagli tecnici restano nei singoli prompt.

|   # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/fedora-storage-root-cause-and-kuma-heartbeat-recovery]] | **Perché è importante:** Fedora Storage ha sia un vero problema di spazio quasi esaurito sia heartbeat Kuma che ricompaiono come mancanti. Il task deve separare le due cause, ripristinare gli heartbeat senza allentare i monitor e intervenire sullo spazio solo quando il cleanup è chiaramente sicuro. | medium | Prompt |
| 2 | [[prompts/personalhub-places-checkin-attempt-journal]] | **Perché è importante:** quando un check-in in un luogo fallisce, oggi spesso non rimane abbastanza informazione per capire il motivo. Il task registra ogni tentativo, riuscito o fallito, così la causa diventa ricostruibile. Nella stessa unica sessione emulator chiude anche il piccolo debito QA rimasto da Hub/episodi con un test dedicato emulator-safe, senza alterare i test fisici. | medium | Goal |
| 3 | [[prompts/personalhub-random-timer-background-deadline]] | **Perché è importante:** il Random Timer deve funzionare anche quando PersonalHub non è aperto davanti a te. Questo task fa sì che la domanda arrivi al momento giusto anche con l'app in background o chiusa, e conclude la serie di modifiche producendo la versione finale da installare sul Pixel. | medium | Goal |
| 4 | [[prompts/repository-publication-secret-audit]] | **Perché è importante:** prima di rendere pubblici i repository bisogna essere sicuri che non contengano password, chiavi, dati privati o altri file che non dovrebbero finire online. Questo task controlla tutto e lascia pubblici solo i repository che risultano sicuri. | medium | Goal |
| 5 | [[prompts/retained-repositories-github-ci-completion]] | **Perché è importante:** molti controlli sul codice possono essere fatti automaticamente da GitHub invece di consumare tempo sul tuo PC o token Codex. Questo task automatizza tutto ciò che può esserlo, così gli errori vengono scoperti prima e Codex resta necessario solo per i test che richiedono davvero il tuo hardware o i tuoi account. | medium | Goal |
