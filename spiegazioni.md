# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

La roadmap contiene solo lavoro che richiede Codex perché dipende da ambiente locale, device, VM, segreti o toolchain non disponibili nella normale chat. Le modifiche puramente remote/documentali vengono fatte direttamente fuori dalla roadmap.

| # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | --- | --- | --- | --- |
| 1 | [[prompts/personalhub-delivery-runtime-hardening]] | **Cosa cambia:** installa sulla VM Oracle il Telegram Local Bot API, collega il notifier condiviso, prova davvero file >50 MB, introduce un lock per impedire due lavori PersonalHub contemporanei e verifica localmente i fix già pushati del Registro. **Perché è importante:** elimina i rebuild/minificazioni fatti solo per Telegram e impedisce che nuovi commit entrino a metà QA costringendo a rifare test e build. | medium | Prompt |
| 2 | [[prompts/personalhub-random-timing-substances]] | **Cosa cambia:** completa date picker Substances, Random timer, Random alerts e chiusura multipla Since When. È la fase 1 della campagna PH e non produce ancora l'APK finale. **Perché è importante:** concentra il lavoro funzionale e rimanda build/install/delivery finali a una sola fase. | medium | Goal |
| 3 | [[prompts/personalhub-temporal-episode-composer]] | **Cosa cambia:** Cerca e Composer diventano una vista temporale ordinata per moduli; WordPulse mostra solo la stanchezza media e il salvataggio episodio usa checkbox+titolo. Fase 2 della stessa campagna, senza release finale. **Perché è importante:** migliora la leggibilità senza duplicare Workflowy e senza moltiplicare build/installazioni. | medium | Goal |
| 4 | [[prompts/personalhub-ui-people-final-hardening]] | **Cosa cambia:** elimina versioni legacy dai moduli, chiude Soldi theme e verifica i residui People già localizzati. Fase 3 della campagna. **Perché è importante:** è soprattutto lavoro meccanico, quindi passa a reasoning low e non consuma una release autonoma. | low | Prompt |
| 5 | [[prompts/personalhub-database-schema-upgrade-safety]] | **Cosa cambia:** rende fail-safe le migration sullo schema finale e chiude l'intera campagna con l'unico bump versione, build, QA Pixel e invio Telegram. **Perché è importante:** concentra il lavoro costoso una sola volta e mantiene GPT-5.6 Sol solo dove il rischio dati lo giustifica. | medium | Goal |
| 6 | [[prompts/wordpulse-alertness-local-verification-release]] | **Cosa cambia:** genera schema Room 4, esegue test/lint/build e QA Pixel isolata della feature già implementata. **Perché è importante:** è verifica locale, quindi GPT-5.5 medium basta; niente nuova analisi architetturale. | medium | Prompt |
