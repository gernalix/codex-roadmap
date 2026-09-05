# Audit tecnico PersonalHub ↔ codex-roadmap — 2026-09-05

Snapshot analizzato: `gernalix/PersonalHub` branch `main` e `gernalix/codex-roadmap` branch `main` disponibili durante l'audit. Audit statico GitHub-only: nessuna build, test runtime, emulator/device run o modifica a PersonalHub.

Substances è stato incluso solo per architettura/cross-module; l'audit interno del modulo è separato.

## Executive summary

Finding di correttezza: **P0 0 · P1 3 · P2 8 · P3 3**.

Componenti più problematici: recovery/import DB, relazioni Places↔Soldi, Timer legacy/runtime infrastructure, People call overlay e lifecycle Soldi.

La base PH è comunque solida su vari punti: DB Room unico, writer gate comune anche per gli accessi Timer legacy, validazione forte dei backup, sync journal, shortcut dirette e benchmark isolato risultano implementati realmente.

## Finding

| ID | Sev | Confidenza | Area | Problema | Evidenza principale | Roadmap |
|---|---|---|---|---|---|---|
| DB-01 | P1 | CONFERMATO | DB import/recovery | marker `personalhub-import.pending` scritto/troncato direttamente; recovery fa `require()` sul contenuto senza fallback | `core/database/.../DatabaseVault.kt`: `importDatabase()`, `recoverInterruptedImport()` | nuovo 03a |
| XMOD-01 | P1 | ALTAMENTE PROBABILE | Places↔Soldi | Places può hard-delete un luogo; Finance ha FK `RESTRICT` verso `places.uuid`; UI non gestisce il constraint | `FinanceEntities.kt`, `PlaceRepository.deletePlace`, `PlacesCapsule.delete`, `LuoghiHomeViewModel.deletePlace` | nuovo 03b |
| PPL-01 | P1 | CONFERMATO | People call overlay | “Open contact” crea `supercontacts://contact/...` con Intent implicito ma nessun intent-filter lo risolve | `CallSystemOverlayController.openContact`, `ContactDeepLink`, manifest app/module | nuovo 03d |
| FIN-01 | P2 | CONFERMATO | Soldi | `FinanceAccount.included` filtra anche la transaction list invece di controllare solo il totale | `feature/soldi/.../SoldiActivity.kt` transaction filter | nuovo 03c |
| FIN-02 | P2 | CONFERMATO | Soldi lifecycle | draft/form/tab/search/month sono `remember` e si perdono su Activity recreation | `SoldiScreen` | nuovo 03c |
| PLC-01 | P2 | CONFERMATO | Places check-in | più geofence contenenti il punto diventano `Ambiguous` solo se i due centri differiscono ≤10 m | `CheckInPolicy.choosePlace()` | prompt 06 modificato |
| TMR-01 | P2 | CONFERMATO | Timer alarms | reconciliation avviene al load, ma non esiste receiver boot/package-update per ripristinare alarm senza riaprire Timer | app manifest + `MainViewModelSnapshotCoordinator` | 09a |
| TMR-02 | P2 | CONFERMATO | Timer widget | write sessione silenziata con `runCatching`; audit/feedback possono dichiarare “started” senza commit | `QuickSessionRunner`, `QuickSessionWidgetClickActivity` | nuovo 03e |
| TMR-03 | P2 | CONFERMATO | Timer version/consistency | Timer usa BuildConfig/patch 539 mentre PH usa versione globale; AutoConsistency marca alcuni failure path come già eseguiti | Timer `build.gradle.kts`, `MainViewModel`, `AutoConsistencyEngine` | nuovo 03f |
| TMR-04 | P2 | CONFERMATO | Timer first-run/backup | first-run Timer usa propria SAF prefs/UI mentre `SqliteVault` è ormai adapter disattivato verso il backup globale | `MainActivity`, `BackupFolderStore`, `SqliteVault` | nuovo 03g |
| PPL-02 | P2 | ALTAMENTE PROBABILE | People call overlay | `IDLE` può arrivare mentre `show()` attende lookup IO; il risultato tardivo può aggiungere overlay dopo la fine chiamata | `CallSystemOverlayController.show/dismiss` | nuovo 03d |
| PPL-03 | P3 | CONFERMATO | People privacy | numero telefonico completo scritto in log INFO | `CallSystemOverlayController.showResolved` | nuovo 03d |
| PERF-01 | P3 | CONFERMATO | auto-export/sync | `HubAutoExport.start()` mantiene scheduler in-process ogni 2 s che controlla dirty + Datasette | `HubAutoExport.kt` | nuovo 03h |
| DB-02 | P3 | DA VERIFICARE A RUNTIME | SAF export | rollback del rename del precedente `personalhub.db` ignora il risultato | `DatabaseVault.exportNow()` | 03a |

## Finding esclusi dopo verifica

- Il processo `:restart` non riapre automaticamente il DB: inizializzazioni WordPulse/PH pertinenti sono lazy nel percorso relay.
- Il vecchio restore Places “clear+replace” non è il restore attivo: il percorso corrente delega al DB globale.
- I nomi/classi legacy di backup Places sono in gran parte adapter; non sono stati classificati come bug solo per il naming.
- Non è stato trovato un secondo writer indipendente del `personalhub.db`: `LegacyDatabase.get()` prende il `SupportSQLiteDatabase` Room wrappato dal `DatabaseGate`.
- Provider Places/Timer nel manifest PH sono `exported=false`; non è emersa una lettura dati pubblica non protetta.
- Il core accounting Soldi usa correttamente opening balance + signed transactions e reconcile `desired-current`; il finding Soldi riguarda filtro/lifecycle, non la formula base.

## Roadmap audit

### 04 cross-module shared entities
Serve ancora. Prima dell'audit era troppo presto nell'ordine e usava `MegaVault: STANDARD` pur introducendo una migrazione DB cross-module. Correzione: eseguirlo dopo DB-01/XMOD-01 e usare **GPT-5.6 Sol / medium / STRICT**. Deve verificare delete/archive semantics, migrations, sync/export e query rappresentative.

### 06 Places overlap
Serve ancora ma il flusso `Ambiguous` esiste già. Il lavoro è principalmente una correzione di `CheckInPolicy`: più di un place contenente il punto => scelta utente. Correzione: **GPT-5.5 / low / FAST**, scope iniziale molto stretto.

### 07 manual historical visit
Serve ancora. Per validazione temporale/history usare **GPT-5.5 / medium / FAST** anziché low.

### 08 Dov'ero?
Serve ancora; nessuna correzione sostanziale richiesta dall'audit.

### vecchio 09 Timer+Places alerts
Troppo grande: accoppia repair Timer alerts e nuova infrastruttura Android geofence Places. Sostituito da `09a` e `09c`.

### vecchio 10 dark theme + export indicator
Due obiettivi indipendenti. Sostituito da `10a` e `10b`; il dark theme deve avvenire dopo FIN-02 e dopo la UI Substances definitiva.

### completed 01
Garanzia benchmark clone/fail-closed ancora presente su main.

### completed 02
La durabilità generation/WorkManager è presente, ma la dichiarazione “idle-loop fix” era troppo forte: resta un poll permanente 2 s. Questo residuo è ora `03h`.

### completed 05/05b
Schema e funzionalità principali Soldi sono presenti; FIN-01/FIN-02 sono correttivi post-completion e non invalidano l'intero completamento.

## Test anti-regressione ad alto valore

- marker import vuoto/troncato/path invalido: niente crash-loop, last-good preservato;
- provider SAF che fallisce publish/rollback;
- Place referenziato da Finance: nessuna uncaught constraint exception e policy archive/block coerente;
- account Soldi escluso: fuori dal totale ma storico ancora visibile;
- recreation durante editor Soldi: draft preservato;
- Places 0/1/2+ geofence: 2+ sempre Ambiguous;
- Timer alarm schedule → reboot/package replace → restoration senza aprire Timer;
- Timer widget write failure: niente toast/audit/broadcast di successo;
- AutoConsistency failure: repair revision non marcata completata e retry successivo;
- fresh/empty PH: Timer apre senza legacy SAF gate;
- call-overlay deep link risolvibile esplicitamente;
- call overlay lookup ritardato + RINGING→IDLE: nessun overlay tardivo.

## Coverage / limiti

Analizzati: AGENTS/protocollo pertinente, app shell/home/settings/back, manifest/permissions/intents/shortcuts, DB e migrations, import/export/recovery/auto-export, Datasette journal/settings, Places check-in/provider/backup adapter, Soldi schema/domain/UI/Git exchange, Timer persistence/widget/alarms/versioning/backup legacy, People repository/backup/call overlay/deep links, WordPulse integration, benchmark e test principali, README/roadmap/calibration e prompt pendenti disponibili nello snapshot originale.

Non eseguiti: runtime/build/device/emulator. `DB-02`, effetto UI finale di `XMOD-01`, race `PPL-02` e reboot `TMR-01` richiedono verifica runtime per il comportamento finale. Substances interno resta fuori scope e continua a essere gestito dal suo audit/task separato `09b`.
