# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

La roadmap contiene solo lavoro che richiede Codex/local runtime. Le modifiche remote/documentali vengono fatte direttamente in chat.

| # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | --- | --- | --- | --- |
| 1 | [[prompts/personalhub-soldi-v2-local-verification]] | **Cosa fa:** verifica localmente la PR Soldi v2 con Android SDK 37, Gradle, schema/migrazione Room 11→12 e smoke su emulatore QA; corregge solo failure concrete dei gate e pusha il branch, senza merge/release. **Perché:** la review statica è già stata fatta in chat, ma il runner GitHub pubblico non dispone di Android 37 e non può sostituire toolchain/emulatore locali. | medium | Prompt |
| 2 | [[prompts/codex-usage-monitor-sqlite-connection-lifecycle]] | **Cosa fa:** elimina le connessioni SQLite lasciate aperte dal monitor/test e verifica in locale che commit/rollback e runtime Fedora restino corretti. **Perché:** i `ResourceWarning` emersi nei test indicano un vero problema di lifecycle: il context manager SQLite standard non chiude la connessione. La prova warning-free e systemd richiede il runtime locale. | medium | Prompt |
| 3 | [[prompts/wordpulse-alertness-local-verification-release]] | **Cosa fa:** genera lo schema Room 4 e verifica localmente Alertness/Fatigue con test/build e QA isolata. **Perché:** l'implementazione esiste già; resta solo evidenza locale. È tenuto fuori dalla campagna PH per non interromperla. | medium | Prompt |
| 4 | [[prompts/personalhub-random-timing-substances]] | **Cosa fa:** fase 1/3 PH: date picker Substances, Random timer/alerts, chiusura multipla Since When e residui UI/People già localizzati (versioni legacy, Soldi theme, overlay tests). **Perché:** assorbe il vecchio prompt UI meccanico nello stesso bootstrap/build/QA invece di aprire una sessione separata. | medium | Goal |
| 5 | [[prompts/personalhub-temporal-episode-composer]] | **Cosa fa:** fase 2/3 PH: Cerca/Composer diventano una vista temporale ordinata per moduli, WordPulse mostra solo stanchezza media e l'episodio salva un subset titolato. **Perché:** è cross-module ma senza migration; GPT-5.5 medium + STANDARD è sufficiente. | medium | Goal |
| 6 | [[prompts/personalhub-database-schema-upgrade-safety]] | **Cosa fa:** fase 3/3 e unica release PH: migration fail-safe, gate consolidati, unico bump/build/install Pixel/delivery dell'esatto APK. **Perché:** è l'unico task con rischio dati/schema che giustifica GPT-5.6 Sol + STRICT. | medium | Goal |
