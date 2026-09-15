# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

La roadmap contiene solo lavoro che richiede Codex/local runtime. Le modifiche remote/documentali vengono fatte direttamente in chat. Dopo un PASS non si apre un nuovo task di micro-ottimizzazione senza un bug/blocco/rischio concreto.

| # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | --- | --- | --- | --- |
| 1 | [[prompts/personalhub-startup-pixel-verification]] | **Cosa fa:** misura tre cold start reali di PersonalHub sul Pixel dopo il fix che ha tolto il repair Timer dalla critical path; profila e corregge un solo hotspot ulteriore solo se i numeri restano materialmente lenti. **Perché:** il miglioramento finale dipende da build/installazione e ADB sul Pixel fisico, quindi questa parte non è verificabile dalla chat remota. | low | Prompt |
