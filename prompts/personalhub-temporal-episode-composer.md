[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=742913 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD | campaign_id=PH_FINAL_20260912 | type=Goal`

# Goal — fase 2/3
Rifinisci Home→Cerca/Composer come unica vista temporale per moduli e consenti di salvare un subset come episodio titolato. Nella stessa sessione integra e verifica il fix Places già implementato e pushato su `fix/places-accuracy-aware-checkin`. Niente redesign Context, registry o migration. **Niente bump/final APK/Pixel main/Telegram**.

# Starting point
`HubTemporalSearchScreen` usa già `temporalProviders()`, `[from,to)`, cursori e `mergeTemporalSlices`; `HubContextComposer` rileva record temporali/`HubEntityRef`; repository/runtime persistono `title`; Context richiede ≥2 membri. People del periodo = solo link/Context dei record bounded, mai scan globale. WordPulse usa solo `fatigueScore 0..100` canonico.

Places: il branch remoto `fix/places-accuracy-aware-checkin` contiene già tutto il fix; non reimplementarlo. Modifica solo 3 file rispetto a `main`: `CheckInPolicy.kt`, `LocationCapsule.kt`, `CheckInAccuracyPolicyTest.kt`. Il matching usa `accuracyM` con cap 50 m; il source usa `PRIORITY_HIGH_ACCURACY`, scarta fix >50 m o più vecchi di 2 minuti; il test copre anche il caso reale equivalente a “Carlo Visda” con `radius_m=40`. Integra il branch una sola volta dopo il fetch, se non già contenuto nel branch di lavoro/main.

# Implementa
- Condividi state/componenti Cerca/Composer solo dove elimina duplicazione reale.
- UI primaria: periodo leggibile + sezioni deterministiche per modulo, tutte aperte default e collassabili/saveable; niente chip modulo/kind, raw ID/UUID/moduleId/entityKind. Empty state compatto; paging `Altri` resta per-provider.
- WordPulse: una sola riga `Stanchezza media: N/100`, oppure `non disponibile`; non mostrare sessioni/speed/rhythm/control/sleep/PVT/baseline. Media solo dei fatigueScore validi del periodo; conserva internamente i canonical refs sottostanti.
- `Salva` entra in selection mode senza rifare query già disponibile: checkbox entry, titolo obbligatorio, salva solo refs selezionati, minimo 2 membri. Checkbox WordPulse salva i refs sottostanti; People derivati salva refs People canonici. Selection/title/collapse sopravvivono a recreation; cambiare Da/A invalida risultati/selezioni fuori intervallo.
- Mantieni aggiunta manuale avanzata in `Aggiungi altro`; nessun nuovo registry.

# Scope/verifica
1. Acquisisci lock PH e fai un solo fetch/pull fast-forward; integra `origin/fix/places-accuracy-aware-checkin` se non già contenuto. Non ampliare quel fix salvo failure concreta.
2. Per Cerca/Composer parti solo da `HubTemporalSearchScreen.kt`, `HubContextComposer.kt`, `HubContextRuntime.kt`, `HubContextRepository.kt` e provider/adapter direttamente coinvolti; Timer→People/WordPulse solo su necessità concreta. Niente lettura moduli interi/refactor fuori scope.
3. Test mirati Cerca/Composer: grouping/collapse/no-chip, paging, People bounded, fatigue aggregate, handoff senza doppia query, selection/title/min-2/recreation/persistenza. Il normale gate host deve includere anche `CheckInAccuracyPolicyTest`; non creare un secondo ciclo build solo per Places.
4. Una sola QA isolata emulator/TCL su intervallo noto + salvataggio subset. Non simulare GPS Places sul device se unit/build sono PASS; fallo solo se emerge un failure concreto.
5. Commit/push PH; non cambiare `version.txt`. Stop a PASS; side issue non bloccanti solo segnalati.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 742913 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 742913`

Output ≤7 righe: RESULT, grouping, People, fatigue, episode selection/title, test/QA incl. Places, SHA/blocker.