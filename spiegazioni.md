# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

La roadmap contiene solo lavoro che richiede Codex/local runtime. Le modifiche remote/documentali vengono fatte direttamente in chat. Dopo un PASS non si apre un nuovo task di micro-ottimizzazione senza un bug/blocco/rischio concreto.

| # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | --- | --- | --- | --- |
| 1 | [[prompts/wordpulse-alertness-local-verification-release]] | **Cosa fa:** genera lo schema Room 4 e verifica localmente Alertness/Fatigue nel repo standalone WordPulse con un solo gate build/migration e QA isolata. **Perché viene prima:** la nuova Cerca temporale di PH è già pronta a mostrare `fatigueScore`, ma il WordPulse incorporato in PH non produce ancora quel dato; prima si congela una versione v4 verificata da usare come riferimento. | low | Prompt |
| 2 | [[prompts/personalhub-database-schema-upgrade-safety]] | **Cosa fa:** integra nel WordPulse incorporato in PH il boundary Alertness/Fatigue v4 appena verificato, rende disponibile il fatigue score canonico al provider temporale, poi completa migration fail-safe e unica release PH. **Perché:** porting nel DB Room condiviso di PH + migration storiche + release sono un unico failure domain ad alto rischio dati e richiedono toolchain/device locali. | medium | Goal |
