[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=742913 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD | campaign_id=PH_FINAL_20260912 | type=Goal`

# Goal — fase 2/3
Rifinisci Home→Cerca/Composer come unica vista temporale per moduli e consenti di salvare un subset come episodio titolato. Niente redesign Context, registry o migration. **Niente bump/final APK/Pixel main/Telegram**.

# Starting point
`HubTemporalSearchScreen` usa già `temporalProviders()`, `[from,to)`, cursori e `mergeTemporalSlices`; `HubContextComposer` rileva record temporali/`HubEntityRef`; repository/runtime persistono `title`; Context richiede ≥2 membri. People del periodo = solo link/Context dei record bounded, mai scan globale. WordPulse usa solo `fatigueScore 0..100` canonico.

# Implementa
- Condividi state/componenti Cerca/Composer solo dove elimina duplicazione reale.
- UI primaria: periodo leggibile + sezioni deterministiche per modulo, tutte aperte default e collassabili/saveable; niente chip modulo/kind, raw ID/UUID/moduleId/entityKind. Empty state compatto; paging `Altri` resta per-provider.
- WordPulse: una sola riga `Stanchezza media: N/100`, oppure `non disponibile`; non mostrare sessioni/speed/rhythm/control/sleep/PVT/baseline. Media solo dei fatigueScore validi del periodo; conserva internamente i canonical refs sottostanti.
- `Salva` entra in selection mode senza rifare query già disponibile: checkbox entry, titolo obbligatorio, salva solo refs selezionati, minimo 2 membri. Checkbox WordPulse salva i refs sottostanti; People derivati salva refs People canonici. Selection/title/collapse sopravvivono a recreation; cambiare Da/A invalida risultati/selezioni fuori intervallo.
- Mantieni aggiunta manuale avanzata in `Aggiungi altro`; nessun nuovo registry.

# Scope/verifica
Parti solo da `HubTemporalSearchScreen.kt`, `HubContextComposer.kt`, `HubContextRuntime.kt`, `HubContextRepository.kt` e provider/adapter direttamente coinvolti; Timer→People/WordPulse solo su necessità concreta. Niente lettura moduli interi/refactor fuori scope.
Test mirati: grouping/collapse/no-chip, paging, People bounded, fatigue aggregate, handoff senza doppia query, selection/title/min-2/recreation/persistenza. Una sola QA isolata emulator/TCL su intervallo noto + salvataggio subset. Commit/push PH; non cambiare `version.txt`. Stop a PASS; side issue non bloccanti solo segnalati.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 742913 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 742913`

Output ≤7 righe: RESULT, grouping, People, fatigue, episode selection/title, test/QA, SHA/blocker.
