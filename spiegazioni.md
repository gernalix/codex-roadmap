# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

La roadmap contiene solo lavoro che richiede Codex/local runtime. Le modifiche remote/documentali vengono fatte direttamente in chat. Dopo un PASS non si apre un nuovo task di micro-ottimizzazione senza un bug/blocco/rischio concreto.

| # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | --- | --- | --- | --- |
| 1 | [[prompts/personalhub-startup-pixel-verification]] | **Cosa fa:** verifica sul Pixel il `main` ottimizzato dopo che il run precedente ha dimostrato cold start ~1–3 s ma ancora ANR/focus timeout e frame skip; misura tre avvii reali e usa una sola Perfetto solo se il problema persiste. **Perché:** la chat ha già applicato i fix statici sicuri (Hub Context lazy, worker startup a priorità background, marker `PH.*`); restano esclusivamente build/install/ADB e l'eventuale attribuzione runtime su Pixel, che richiedono Codex locale. | low | Prompt |
