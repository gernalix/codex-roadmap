[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=893806 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=3/4 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Aggiungere a Luoghi un journal diagnostico persistente di OGNI tentativo **utente** di check-in basato sul riconoscimento della posizione, inclusi falliti/ambigui/annullati/interrotti, senza contaminare le visite reali.

# Routing — scope stretto
Usa `.codex/CODE_MAP.tsv` solo per `places.checkin`, `places.data`, `database.schema`. Parti da `LuoghiHomeViewModel.checkInAtCurrentLocation()`, `CheckInCapsule`, `CheckInPolicy`, repository/DAO/schema già mappati. Niente audit Luoghi/core.
Facts già verificati:
- oggi permission denied/location unavailable/unknown/ambiguous/cancel/failure non hanno un journal persistente;
- `PlaceEvent` rappresenta visite effettive e NON va riusato per failure diagnostici;
- matching dispone già di distanza/raggio/accuracy utili alla diagnosi.

# Modello dati minimo
Nel `personalhub.db`, con migrazione canonica:
- attempt: id stabile, `startedAt`, `finishedAt`, source, stage/outcome, location disponibile (solo campi realmente forniti), selected/matched place id, error code + messaggio sanificato;
- candidate: attempt id, place id, distanza, soglia/raggio effettivo, ranking/esito minimo necessario.
Colonne normali + FK/index essenziali; niente JSON opaco se lo schema è stabile.

# Lifecycle obbligatorio
1. Persisti l'attempt prima del primo abort possibile.
2. Stati terminali almeno equivalenti a `SUCCESS`, `PERMISSION_DENIED`, `LOCATION_UNAVAILABLE`, `NO_MATCH`, `AMBIGUOUS`, `USER_CANCELLED`, `PERSISTENCE_FAILED`, `INTERRUPTED`.
3. Non usare `getOrNull()` perdendo la causa: registra categoria/messaggio sanificato, UI invariata/user-friendly.
4. Unknown -> form nuovo luogo: conserva lo stesso attempt fino a create/cancel.
5. `IN_PROGRESS` lasciato da process death -> `INTERRUPTED` al recovery, idempotente.
6. Scope funzionale = flow di check-in user-triggered dalla posizione corrente e sue continuazioni. **Geofence/automatic check-in sono fuori scope** salvo riuso naturale dello stesso journal senza nuova esplorazione o codice dedicato. Check-in retroattivi verso luogo già noto restano esclusi.
7. Nessun failure attempt deve creare visita o rumore nel Registro globale.

# UI diagnostica minima
Una voce discreta `Diagnostica check-in`: recenti newest-first, filtro outcome/place, riga comprensibile + dettaglio con timestamp/accuracy/candidate-distanze-raggi/error; copia report testuale singolo. Nessuna telemetria/coordinate esterne.

# Verifica a costo controllato
1. Prima: migration/unit test mirati per schema, lifecycle, candidate e recovery. Failure => leaf fix, niente suite globale.
2. Esegui `checkArchitectureBoundaries` una volta perché cambia persistence ownership/schema.
3. Solo dopo host PASS, avvia UNA sessione Pixel_8a emulator e una sola invocazione androidTest filtrata ai nuovi test: permission denied + unknown/ambiguous + success. Verifica: failure non produce `PlaceEvent`; success produce attempt SUCCESS + visita normale; migration preserva dati fixture.
4. L'invocazione androidTest compila gli APK necessari: niente `assembleDebug` separato. Nessun Pixel/TCL/release in questa fase.

# Non-goal
Niente tuning raggio 75 m, geofence redesign/instrumentazione, mappa, sync cloud, cleanup storico, telemetria remota o bug collaterali non bloccanti.

# Campagna
Fase intermedia: niente bump `version.txt`, Pixel reale, APK/Telegram. Push una volta dopo PASS. La fase 4 NON dovrà ripetere migration/UI test di questa fase se i relativi file restano invariati.

# Acceptance
PASS se ogni tentativo user-triggered è ricostruibile, failure non crea visite, migrazione preserva dati, recovery è idempotente, diagnostica è leggibile e i gate mirati PASS.

# Stop
Acquisisci/rilascia il lease PH secondo `AGENTS.md`. Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 893806 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 893806`

Dopo `status=completed` + `push_verified=git_push_exit_0` fermati. Output massimo 6 righe.