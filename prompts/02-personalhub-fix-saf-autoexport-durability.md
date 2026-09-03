# PersonalHub — rendere l'auto-export SAF realmente durevole

**Modello consigliato:** GPT-5.5  
**Reasoning:** Medium  
**MegaVault:** STANDARD — riguarda persistenza/backup dati reali

```text
PROMPT_ID=736205
project_id=49

GOAL: trovare e correggere la causa per cui l'auto-export SAF di PersonalHub può restare vecchio per molte ore nonostante modifiche al DB, rendendo verificabile la garanzia "DB change -> durable SAF export" anche dopo process death/reboot/background restrictions.

EVIDENZA GIÀ RACCOLTA — riusala, non ripetere esplorazione generale:
- durante PROMPT_ID=641827 l'utente ha osservato che l'ultimo auto-export SAF era vecchio di ~12 ore;
- il protocollo MegaVault richiede `saf_sqlite=autoexport_all_app_data_on_db_change;atomic;validate_after_write;failure_visible;preserve_last_good;test_required`;
- `HubAutoExport.start()` usa un executor in-process che controlla `dirty()` ogni 2 secondi + un periodic WorkManager da 15 minuti;
- `dirty()` confronta `hub_generation.generation` con `personalhub_transfer.exported_generation`;
- `request()` usa unique work `personalhub-autoexport` con `ExistingWorkPolicy.KEEP` e delay 1200 ms;
- `HubExportWorker` esegue `DatabaseVault.exportNow()` finché `dirty()` diventa false e su Exception restituisce retry;
- nel PROMPT_ID=641827 `Application.onCreate()` è stato modificato per spostare autoexport/Datasette/cleanup post-first-frame, con requisito esplicito di NON perdere process-death/reboot durability, sync o auto-export;
- quando PH è stata accidentalmente disinstallata, l'ultima copia locale valida trovata era ~09:05 CEST e i dati successivi erano a rischio: quindi questo non è un problema cosmetico.

Non assumere che lo spostamento post-first-frame sia la causa: stabiliscilo con prove. L'osservazione delle ~12 ore potrebbe precedere o essere indipendente dalla modifica di startup.

1. Parti da HubAutoExport, DatabaseVault.exportNow, hook che incrementano hub_generation, Application startup e WorkManager config. Individua la failure mode concreta che permette generation dirty senza export SAF tempestivo.
2. Verifica in particolare: process death/reboot, app non riaperta, executor in-process, unique work KEEP, worker già pending/running, retry/backoff, URI permission SAF, error visibility e commit-before-enqueue race.
3. Determina se OGNI write path reale incrementa la generation. Non fare audit generale: usa schema/capsule/write entrypoint canonici e amplia solo se trovi un gap.
4. Implementa il minimo fix durevole. La correttezza non deve dipendere da un polling thread in-process o dal fatto che l'utente riapra PH.
5. Dopo una mutation DB completata, deve esistere un trigger persistente WorkManager equivalente che sopravvive a process death; il periodic recovery resta solo rete di sicurezza, non meccanismo principale se evitabile.
6. Mantieni export atomico, validazione post-write, ultima copia buona e retry idempotente. Nessuna mutation deve essere persa o duplicata.
7. Rendi failure/staleness osservabile: almeno last successful export, generation esportata/corrente, ultimo errore e stato stale. Non nascondere Exception dietro retry senza traccia persistente/visibile.
8. Aggiungi test mirati per:
   - mutation -> export;
   - più mutation ravvicinate/coalescing;
   - process death tra commit ed enqueue;
   - restart/reboot recovery equivalente;
   - export failure + retry;
   - URI/provider failure;
   - preservation last-good;
   - exported_generation aggiornato solo dopo export valido;
   - nessuna finestra di ore con dirty generation e nessun work recuperabile.
9. Device validation solo in modalità non distruttiva e con backup verificato prima. NON uninstall/pm clear/reinstall del package reale; se serve isolamento usa emulator/clone.
10. Non refactor/cleanup fuori scope. Ferma appena gli acceptance criteria sono verificati.

Acceptance criteria:
- root cause provata, non ipotizzata;
- ogni mutation canonica produce un trigger durevole;
- process death/reboot non può lasciare silenziosamente SAF stale per ore;
- failure visibile e retry idempotente;
- last-good preservato;
- test mirati PASS;
- commit + push canonici.

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
