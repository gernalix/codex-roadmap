# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

La tabella segue esattamente l'ordine di `roadmap.md`. `Livello ragionamento` rispecchia il valore dichiarato nel prompt; `Tipo prompt` indica se il task va trattato come **Prompt** prescrittivo oppure come **Goal** più autonomo e architetturale.

| # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | --- | --- | --- | --- |
| 1 | [[prompts/github-autosync-local-audit-verification]] | Il fix remoto è già scritto: gli 11 repo invariati vengono auditati localmente, i commit locali ahead possono essere pushati, il clone rispetta il worktree canonico e dry-run/upstream non fanno fetch inutili. Codex deve solo pullare, eseguire i test e fare una singola verifica del servizio Fedora, correggendo esclusivamente failure concrete. | medium | Prompt |
| 2 | [[prompts/personalhub-context-composer-temporal-search]] | Unisce Composer e Cerca perché entrambi devono capire persone, luoghi, Timer, Soldi, Substances e WordPulse. Codex inventaria adapter e semantica temporale una sola volta: Composer crea Context persistenti con suggerimenti e rilevazioni, mentre Cerca ricostruisce in sola lettura ciò che è successo in un intervallo senza creare collegamenti permanenti. | medium | Goal |
| 3 | [[prompts/personalhub-random-timing-substances]] | Stock zero è già risolto e testato; anche il date picker riutilizzabile è pronto. Restano il cablaggio di due campi e soprattutto Random timer + Random alerts condividendo scheduler/settings/notification già esistenti. | medium | Goal |
| 4 | [[prompts/personalhub-global-activity-register-safe-undo]] | Aggiunge un unico Registro attività per le modifiche di tutti i moduli, con cronologia paginata, filtri e annullamento sicuro. Riusa gli audit già presenti in Timer/Places, evita doppioni e registra l'undo come nuova operazione invece di cancellare la storia. | medium | Goal |
| 5 | [[prompts/personalhub-database-schema-upgrade-safety]] | Parte da difetti già localizzati: migration ancora inline, `canMigrateFrom` numerico e nessun startup migration gate. Costruisce il registry/gate finale e testa tutte le versioni storiche senza riscrivere backup/import già sicuri. | medium | Goal |
| 6 | [[prompts/personalhub-ui-people-final-hardening]] | Home export status, host/Timer dark mode e i fix call-overlay People sono già implementati; restano compile/test, Soldi system theme, label/footer versioni e una sola QA finale. | medium | Prompt |
