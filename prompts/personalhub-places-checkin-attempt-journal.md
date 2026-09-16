[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=893806 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=3/4 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Aggiungere a Luoghi un journal diagnostico persistente di OGNI tentativo di check-in basato sul riconoscimento della posizione, inclusi tentativi falliti/ambigui/annullati/interrotti, senza contaminare la cronologia delle visite reali.

# Starting point verificato
Usa `.codex/CODE_MAP.tsv` (`places.checkin`, `places.data`, `database.schema`) e parti SOLO dai path mappati. In chat è già stato verificato che:
- `LuoghiHomeViewModel.checkInAtCurrentLocation()` oggi ottiene la posizione con `runCatching(...).getOrNull()`, poi decide match/ambiguous/unknown e persiste una visita solo nel ramo matched;
- permission denied, location unavailable, unknown place, ambiguous choice/cancel e molti failure path restano solo stato UI e non vengono persistiti come tentativi;
- `CheckInCapsule`/PlaceEvent rappresentano visite effettive, quindi NON vanno riusati per i tentativi falliti;
- `CheckInPolicy` usa matching su distanza/raggio/accuracy e dispone già delle informazioni utili alla diagnosi.
Questo task modifica lo schema Room condiviso: trattalo come migrazione/rischio dati, non come refactor generale.

# Modello dati richiesto
Introduci un journal separato e normalizzato nel `personalhub.db` (nomi finali coerenti col repo), preferibilmente:
- tabella tentativi: id stabile, `startedAt`, `finishedAt`, source, stage/outcome, posizione osservata quando disponibile (lat/lon/accuracy/timestamp/provider o equivalente realmente disponibile), matched/selected place id quando esiste, error code + messaggio diagnostico sanificato;
- tabella candidate per attempt: attempt id, place id, distanza, soglia/raggio effettivo e ranking/esito necessario a ricostruire perché il matching ha vinto/fallito.
Evita blob JSON opachi se le colonne sono stabili. FK/index minimi utili a query per tempo/outcome/place.

# Lifecycle obbligatorio
1. Crea/persisti l'attempt PRIMA del primo punto che può abortire la procedura.
2. Ogni tentativo deve finire in uno stato terminale esplicito. Copri almeno: `SUCCESS`, `PERMISSION_DENIED`, `LOCATION_UNAVAILABLE`, `NO_MATCH/UNKNOWN_PLACE`, `AMBIGUOUS`, `USER_CANCELLED`, `PERSISTENCE_FAILED`, `INTERRUPTED`; usa naming coerente col progetto.
3. Non perdere le eccezioni tramite `getOrNull()`: registra categoria/messaggio diagnostico, mantenendo però la UI user-friendly.
4. Se viene mostrato il form “crea nuovo luogo” dopo un unknown match, lo stesso attempt deve rimanere collegato fino a create/cancel; non creare un secondo tentativo fittizio.
5. Se il processo muore con attempt `IN_PROGRESS`, al successivo avvio/recovery marcane il terminale `INTERRUPTED` in modo idempotente.
6. Includi anche i percorsi automatici/geofence SOLO quando eseguono davvero una decisione di check-in/matching; NON registrare come tentativi i meri update di posizione né i check-in retroattivi già indirizzati a un luogo noto.
7. Il journal non deve creare false visite né riempire il Registro globale di eventi tecnici ad ogni attempt.

# Superficie diagnostica minima
Da Luoghi aggiungi una voce discreta `Diagnostica check-in` con lista recente newest-first e filtri minimi outcome/place. Ogni riga deve spiegare in linguaggio comprensibile cosa è successo; dettaglio espandibile con timestamp, accuracy, candidate/distanze/raggi ed errore. Deve essere possibile copiare un singolo report testuale per debugging. Non inviare coordinate o report a servizi esterni.

# Migrazione e test
- applica la migrazione Room canonica dalla versione corrente alla nuova senza distruzione dati;
- aggiungi/aggiorna schema export e migration test;
- unit test mirati per lifecycle attempt + candidate matching + recovery `IN_PROGRESS -> INTERRUPTED`;
- test strumentale minimo: permission denied e un percorso unknown/ambiguous simulabile devono produrre un attempt terminale senza PlaceEvent falso; success path deve produrre attempt SUCCESS + normale visita;
- esegui `checkArchitectureBoundaries` perché tocchi persistence ownership/public boundary;
- poi un solo build debug finale. Niente audit completo, benchmark, Pixel/TCL o release in questa fase.

# Non-goal
Niente tuning del raggio 75 m, redesign mappa/Luoghi, nuovo algoritmo di geofencing, cleanup storico, sync cloud o telemetria remota. Se scopri un bug collaterale non bloccante, riportalo senza investigarlo.

# Campagna / release
Fase intermedia: NON incrementare `version.txt`, NON installare sul Pixel e NON inviare APK/Telegram. Push una sola volta dopo PASS.

# Acceptance
PASS se ogni attempt di riconoscimento è ricostruibile a posteriori con outcome e prove sufficienti, nessun attempt fallito diventa visita reale, migrazione preserva i dati, recovery è idempotente e i test mirati/build PASS.

# Stop
Acquisisci/rilascia il lease PH secondo `AGENTS.md`. Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 893806 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 893806`

Dopo `status=completed` + `push_verified=git_push_exit_0` fermati. Output massimo 6 righe.