# PersonalHub — rendere l'auto-export SAF realmente durevole

**Modello consigliato:** GPT-5.5  
**Reasoning:** Medium  
**MegaVault:** STANDARD — persistenza/backup dati reali; usa però esplorazione stretta  
**Calibrazione:** applica `codex-calibration.md`; PROMPT_ID=428619 mostra che il costo va ridotto soprattutto limitando tool-call/esplorazione/verifiche ridondanti, non abbassando il reasoning di task diagnostici/safety comparabili.

```text
PROMPT_ID=736205
project_id=49

GOAL: trovare e correggere la causa per cui l'auto-export SAF di PersonalHub può restare vecchio per molte ore nonostante modifiche al DB, rendendo verificabile la garanzia "DB change -> durable SAF export" anche dopo process death/reboot/background restrictions.

OTTIMIZZAZIONE TOKEN/TOOL-CALL OBBLIGATORIA:
- riusa MegaVault, AGENTS/protocollo ed evidenza sotto; niente esplorazione generale del repo;
- parti SOLO da HubAutoExport, DatabaseVault.exportNow, hook generation, Application startup e WorkManager config; amplia soltanto se una prova concreta lo richiede;
- raggruppa ispezioni/comandi quando possibile; niente verifiche equivalenti/ridondanti e niente retry identici senza nuova evidenza;
- testa prima il failure mode provato e il fix; amplia i test solo se rischio/fallimento lo richiede;
- nessun audit/refactor/cleanup collaterale; segnala soltanto problemi non bloccanti;
- appena acceptance criteria sono provati: STOP, niente audit post-PASS.

EVIDENZA GIÀ RACCOLTA — riusala, non riverificarla senza motivo:
- durante PROMPT_ID=641827 l'utente ha osservato che l'ultimo auto-export SAF era vecchio di ~12 ore;
- il protocollo MegaVault richiede `saf_sqlite=autoexport_all_app_data_on_db_change;atomic;validate_after_write;failure_visible;preserve_last_good;test_required`;
- `HubAutoExport.start()` usa un executor in-process che controlla `dirty()` ogni 2 secondi + un periodic WorkManager da 15 minuti;
- `dirty()` confronta `hub_generation.generation` con `personalhub_transfer.exported_generation`;
- `request()` usa unique work `personalhub-autoexport` con `ExistingWorkPolicy.KEEP` e delay 1200 ms;
- `HubExportWorker` esegue `DatabaseVault.exportNow()` finché `dirty()` diventa false e su Exception restituisce retry;
- nel PROMPT_ID=641827 `Application.onCreate()` è stato modificato per spostare autoexport/Datasette/cleanup post-first-frame, con requisito esplicito di NON perdere process-death/reboot durability, sync o auto-export;
- quando PH è stata accidentalmente disinstallata, l'ultima copia locale valida trovata era ~09:05 CEST e i dati successivi erano a rischio: quindi questo non è un problema cosmetico.

Non assumere che lo spostamento post-first-frame sia la causa: stabiliscilo con prove. L'osservazione delle ~12 ore potrebbe precedere o essere indipendente dalla modifica di startup.

1. Individua la failure mode concreta che permette generation dirty senza export SAF tempestivo usando lo scope iniziale sopra.
2. Verifica solo le ipotesi necessarie tra: process death/reboot, app non riaperta, executor in-process, unique work KEEP, worker pending/running, retry/backoff, URI permission SAF, error visibility, commit-before-enqueue race.
3. Verifica che i write path canonici incrementino la generation usando schema/capsule/write entrypoint canonici; niente audit generale salvo evidenza di gap.
4. Implementa il minimo fix durevole. La correttezza non deve dipendere da polling in-process o riapertura di PH.
5. Dopo una mutation DB completata deve esistere un trigger persistente WorkManager equivalente che sopravvive a process death; periodic recovery solo rete di sicurezza se evitabile.
6. Mantieni export atomico, validazione post-write, last-good e retry idempotente.
7. Rendi failure/staleness osservabile almeno con last successful export, generation esportata/corrente, ultimo errore e stato stale.
8. Test minimi obbligatori, preferibilmente mirati/parametrizzati invece di suite ridondanti:
   - mutation -> durable trigger/export + mutation ravvicinate/coalescing;
   - process death/recovery, includendo finestra commit->enqueue;
   - failure/retry incluse URI/provider failure;
   - last-good preservato ed exported_generation aggiornato solo dopo export valido.
   Aggiungi test separati per reboot o altri casi solo se non sono già coperti dalla stessa invariabile o se l'implementazione li rende distinti.
9. Device validation solo non distruttiva e con backup verificato. NON uninstall/pm clear/reinstall del package reale; usa emulator/clone se serve isolamento.
10. Incrementa `version.txt` solo se richiesto dal protocollo governante. Commit + push canonici.

Acceptance criteria:
- root cause provata, non ipotizzata;
- ogni mutation canonica produce un trigger durevole;
- process death/reboot non può lasciare silenziosamente SAF stale per ore;
- failure visibile e retry idempotente;
- last-good preservato;
- test mirati sufficienti PASS;
- commit + push canonici;
- nessuna esplorazione/verifica successiva al PASS.

Output finale conciso:
PROMPT_ID=
ROOT_CAUSE=
WHY_12H_STALE_WAS_POSSIBLE=
FIX=
DURABLE_TRIGGER=
FAILURE_VISIBILITY=
PROCESS_DEATH_REBOOT=
TESTS=
DATA_SAFETY=
COMMIT=
PUSH=
```
