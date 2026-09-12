[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=742913 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST | campaign_id=PH_FINAL_20260912`

> Esecuzione diretta. Non usare `select` e non rileggere roadmap/README/spiegazioni. Fase 2/4 della campagna: **niente bump versione/final APK/Pixel main/Telegram**.

# Goal
Rifinire Home→Cerca/Composer come vista temporale unica per moduli, con salvataggio selettivo di un episodio titolato. Nessun redesign del modello Context e nessuna nuova migration.

# Starting point verificato
- Cerca: `HubTemporalSearchScreen.kt` usa già `temporalProviders()`, query `[from,to)`, cursori e `mergeTemporalSlices`;
- Composer: `HubContextComposer.kt` rileva record temporali e risolve `HubEntityRef`; repository/runtime supportano già `title` persistente;
- Context richiede almeno 2 membri;
- People del periodo vanno derivati solo da link/Context dei record bounded, mai da scan globale;
- fatigue canonica WordPulse è `fatigueScore 0..100`; non inventare una seconda formula.

# UX
Condividi state/componenti tra Cerca e Composer dove riduce duplicazione reale.

Mostra sempre il periodo leggibile e sezioni deterministiche per modulo (Places, People, Transazioni, Timer, Substances, WordPulse…), tutte aperte di default e collassabili singolarmente con stato saveable. Elimina chip modulo/kind dalla UI primaria. Le sezioni senza risultati possono avere empty-state compatto. Mantieni paging per-provider: `Altri` appartiene alla sua sezione.

Niente raw moduleId/entityKind/ID/UUID.

## WordPulse
Una sola riga aggregata: `Stanchezza media: N/100`; `non disponibile` senza campioni validi. Non mostrare sessioni, speed/rhythm/control/sleep/PVT/baseline. Usa solo fatigueScore canonici del periodo. Conserva internamente i canonical refs sottostanti.

## Salva come episodio
Browsing normale senza checkbox. `Salva` entra nello stesso selection flow preservando intervallo/risultati senza query duplicata quando già disponibili. In selection mode: checkbox sulle entry selezionabili, titolo obbligatorio, salva solo refs selezionati, minimo 2 membri. Checkbox WordPulse aggregata salva i refs sottostanti; People derivati salva refs People canonici. Selection/title/collapse sopravvivono a recreation; cambiare Da/A invalida deterministically risultati/selezioni fuori intervallo.

Mantieni l'aggiunta manuale/advanced del Composer in una sezione secondaria `Aggiungi altro`; niente nuovo registry.

# Letture iniziali
`HubTemporalSearchScreen.kt`, `HubContextComposer.kt`, `HubContextRuntime.kt`, `HubContextRepository.kt`, temporal provider/adapter direttamente coinvolti. Timer→People e WordPulse solo se necessari. Niente lettura di interi moduli.

# Verification fase
Test mirati per grouping/collapse, assenza chip primari, paging invariato, People bounded, fatigue aggregate, handoff senza doppia query, selection/title/min-2/recreation e persistenza titolo. QA isolata emulator/TCL su un intervallo noto e salvataggio subset. Niente package reale Pixel.

Commit/push PersonalHub al PASS; **non modificare `version.txt`** e non fare final delivery.

Su PASS completa solo `PROMPT_ID=742913`; `push_verified=git_push_exit_0` è terminale.

Output ≤7 righe: RESULT, grouping/collapse, People, fatigue, episode selection/title, test/QA, SHA/blocker.
