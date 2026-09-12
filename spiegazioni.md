# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

La roadmap contiene solo lavoro che richiede Codex/local runtime. Le modifiche remote/documentali vengono fatte direttamente in chat.

| # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | --- | --- | --- | --- |
| 1 | [[prompts/personalhub-main-baseline-local-verification]] | **Cosa fa:** verifica sul `main` il repair Timer sul vecchio stato persistente e i confini capsule/runtime. Il falso FAIL del gate architetturale è già stato corretto in chat. **Ottimizzazione:** Codex esegue static gate+unit test+build prima di accendere l'AVD; solo su PASS avvia l'emulatore e installa l'APK già costruito, evitando startup/stop inutili e una seconda invocazione Gradle. | low | Prompt |
| 2 | [[prompts/personalhub-workflowy-days-oracle-feed-endpoint]] | **Cosa fa:** chiude il collegamento reale Workflowy-days→PersonalHub sulla VM Oracle, riusando HTTPS/Datasette/nginx esistenti e aggiungendo auth read-only solo se serve. **Perché:** può modificare PH, quindi va chiuso prima della campagna/release finale. | medium | Prompt |
| 3 | [[prompts/wordpulse-alertness-local-verification-release]] | **Cosa fa:** genera lo schema Room 4 e verifica localmente Alertness/Fatigue con test/build e QA isolata. **Perché:** l'implementazione esiste già; resta solo evidenza locale. È tenuto fuori dalla campagna PH per non interromperla. | medium | Prompt |
| 4 | [[prompts/personalhub-random-timing-substances]] | **Cosa fa:** fase 1/3 PH: date picker Substances, Random timer/alerts, chiusura multipla Since When e residui UI/People già localizzati (versioni legacy, Soldi theme, overlay tests). **Perché:** assorbe il vecchio prompt UI meccanico nello stesso bootstrap/build/QA invece di aprire una sessione separata. | medium | Goal |
| 5 | [[prompts/personalhub-temporal-episode-composer]] | **Cosa fa:** fase 2/3 PH: Cerca/Composer diventano una vista temporale ordinata per moduli, WordPulse mostra solo stanchezza media e l'episodio salva un subset titolato. **Perché:** è cross-module ma senza migration; GPT-5.5 medium + STANDARD è sufficiente. | medium | Goal |
| 6 | [[prompts/personalhub-database-schema-upgrade-safety]] | **Cosa fa:** fase 3/3 e unica release PH: migration fail-safe, gate consolidati, unico bump/build/install Pixel/delivery dell'esatto APK. **Perché:** è l'unico task con rischio dati/schema che giustifica GPT-5.6 Sol + STRICT. | medium | Goal |
