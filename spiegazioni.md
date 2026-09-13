# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

La roadmap contiene solo lavoro che richiede Codex/local runtime. Le modifiche remote/documentali vengono fatte direttamente in chat. Dopo un PASS non si apre un nuovo task di micro-ottimizzazione senza un bug/blocco/rischio concreto.

| # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | --- | --- | --- | --- |
| 1 | [[prompts/personalhub-database-schema-upgrade-safety]] | **Cosa fa:** integra nel WordPulse incorporato in PH il boundary Alertness/Fatigue v4 appena verificato, rende disponibile il fatigue score canonico al provider temporale, poi completa migration fail-safe e unica release PH. **Perché:** porting nel DB Room condiviso di PH + migration storiche + release sono un unico failure domain ad alto rischio dati e richiedono toolchain/device locali. | medium | Goal |
