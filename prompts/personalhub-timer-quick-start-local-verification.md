[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=742618 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST | type=Prompt`

> Esecuzione diretta. Non rifare discovery o redesign: la feature è già implementata nella PR `gernalix/PersonalHub#2`. Questo task esiste solo perché richiede checkout/toolchain Android/emulatore locali e coordinamento col lock PersonalHub.

# Goal
Verificare localmente la PR #2 `feature/timer-quick-start-tags` e integrarla nel branch canonico solo dopo PASS, senza interferire con altri task PersonalHub.

# Starting point verificato
- PR: `https://github.com/gernalix/PersonalHub/pull/2`, branch `feature/timer-quick-start-tags`;
- implementazione già fatta: launcher tag nella schermata Timer/Now, ricerca, tap singolo=start immediato, long-press=multiselect, selezioni persistenti durante la ricerca, ✔️ per avvio multi-tag, ranking recenza+frequenza 65/35, Snackbar Undo sull'esatta sessione appena creata, gerarchia tag/timed-tag, FAB/editor legacy conservato;
- nessuna migration DB;
- test JVM ranking già presenti in `QuickStartTagRankingTest.kt`;
- `QuickStartTagLauncherInstrumentedTest.kt` copre tap breve, long-press, multiselect, ricerca, Undo e layout con una/più sessioni attive;
- `QuickStartIdleLayoutInstrumentedTest.kt` copre layout senza sessioni attive, ricerca/no-results, FAB legacy e Loading→Error;
- `QuickStartTimedHierarchyInstrumentedTest.kt` copre timed tag + gerarchia: durata/expectedEnd, confine di scadenza, regole di scheduling, notification NONE, timed+normale, rifiuto secondo timed, closure transitiva, parent condivisi e timed introdotto indirettamente dalla gerarchia;
- `SessionEditDialogRegressionInstrumentedTest.kt` copre il normale editor: create singola, titolo/tag, gerarchia, regola singolo timed, cleanup draft fantasma, delete con conferma, vincoli sugli orari e read-only;
- `NowTimerRulesRegressionInstrumentedTest.kt` copre le regole Timer storiche attraverso la vera `NowScreen`: tap=stop, long-press=editor, metadata save senza stop, delete confermato, read-only, toggle remaining/elapsed timed e filtro di righe ended/deleted;
- `version.txt` della feature branch è 44; non fare un secondo bump per i test. Il remoto corrente al momento dell'esecuzione resta l'autorità se nel frattempo è avanzato.

# Procedura minima
1. Leggi solo `AGENTS.md` e usa il preflight/lock PersonalHub già previsto. Se un altro task PH è attivo => `BLOCKED`; non aspettare e non fare polling.
2. `fetch` una volta. Crea una candidate locale dalla branch canonica corrente + PR #2 senza force/reset/stash. Se c'è un conflitto non banale o main contiene lavoro PH concorrente non ancora stabilizzato => `BLOCKED`, non risolvere modifiche estranee.
3. Se l'unico conflitto è `version.txt`, mantieni monotonicità: se 44 non è più maggiore della versione canonica, usa esattamente `current_main + 1`; nessun altro bump.
4. Esegui il test JVM mirato del ranking e il minimo compile/assemble necessario. Non eseguire suite/lint generali salvo failure concreta.
5. Avvia l'emulatore esclusivamente con `python3 tools/android_target_preflight.py --target emulator`; usa il serial restituito. Non usare il Pixel reale.
6. Esegui integralmente SOLO queste cinque classi strumentali:
   - `QuickStartTagLauncherInstrumentedTest`
   - `QuickStartIdleLayoutInstrumentedTest`
   - `QuickStartTimedHierarchyInstrumentedTest`
   - `SessionEditDialogRegressionInstrumentedTest`
   - `NowTimerRulesRegressionInstrumentedTest`
   Su failure correggi solo la causa diretta e ripeti solo la classe/test fallito.
7. Non duplicare manualmente i casi già coperti dalle cinque classi. Nel QA manuale verifica soltanto gli aspetti residui elencati sotto.
8. Dopo PASS rifai un solo `fetch`: se il branch canonico è avanzato da quando hai creato la candidate => `BLOCKED` e non rifare QA. Altrimenti integra/pusha la candidate sul branch canonico senza force e chiudi/mergea la PR #2. Stop immediato.

# Copertura strumentale obbligatoria

## `QuickStartTagLauncherInstrumentedTest`
- tap breve: un solo avvio col tag corretto;
- long-press: multiselect, primo tag preselezionato, nessun avvio prematuro;
- multiselezione: ✔️ crea una sola sessione con tutti i tag scelti;
- ricerca: filtro + selezioni nascoste persistenti;
- Undo: elimina esattamente la sessione appena creata;
- 1 e ≥2 sessioni attive: sessioni sopra, launcher sotto circa 50/50 e ancora utilizzabile.

## `QuickStartIdleLayoutInstrumentedTest`
- zero sessioni: niente vecchia card `Nothing running`; quick-start/ricerca/chip/FAB visibili nel corpo;
- ricerca idle + no-results;
- FAB apre il precedente editor completo;
- Loading/Error nascondono il launcher finché lo stato non è ready.

## `QuickStartTimedHierarchyInstrumentedTest`
- tap quick-start su timed tag usa `nowMs` come start e `requireTimedSessionExpectation` produce `expectedEnd` coerente con la durata configurata;
- appena prima della scadenza il piano mantiene l'alarm futuro; esattamente a `expectedEnd` la sessione entra negli expired e non resta alcun alarm futuro;
- `ALARM` conserva `alarmStyle=true`; `notificationType=NONE` mantiene la scadenza ma non schedula notifiche/alarm;
- timed + tag normale è consentito;
- un secondo timed tag in multiselect viene rifiutato e non entra nella sessione;
- un child quick-start riceve tutti i parent transitivi prima della create;
- due child con parent condiviso producono un solo parent nella sessione;
- un parent timed aggiunto automaticamente dalla closure + un altro timed esplicito viene bloccato dopo l'espansione gerarchica, senza write invalida.

## `SessionEditDialogRegressionInstrumentedTest`
- il normale editor crea un nuovo draft una sola volta con titolo/start/tag corretti;
- la selezione tag applica la closure transitiva dei parent;
- il secondo timed tag viene rifiutato preservando il primo;
- annullare una nuova sessione già materializzata elimina esattamente il draft fantasma;
- cancellare una sessione esistente richiede conferma e usa l'ID corretto;
- una sessione running con start futuro non può salvare gli orari;
- una sessione chiusa con end < start mostra errore e non salva;
- in read-only Save ed Edit times sono disabilitati.

## `NowTimerRulesRegressionInstrumentedTest`
- tap sulla card running ferma esattamente quella sessione a `effectiveNow`;
- long-press apre il normale editor senza fermare/cancellare la sessione;
- Save dell'editor esistente aggiorna solo metadata, non tempi/delete;
- delete da Now → editor richiede conferma e cancella esattamente la sessione selezionata;
- read-only impedisce stop/editor e non emette write;
- tap sulla durata timed alterna remaining→elapsed senza fermare la sessione;
- righe già concluse o soft-deleted non vengono mostrate come running.

# QA manuale residuo — solo ciò che i test non possono certificare bene

## Android alarm/notification
- Per un timed tag con notifica abilitata, verifica solo che l'AlarmManager/notifica Android venga effettivamente consegnato all'orario previsto sull'emulatore. Non rifare calcolo durata, expiry o regola del singolo timed già automatizzati.

## Layout residuo
- Solo controllo visivo rapido che scroll, FAB e Snackbar non si sovrappongano in modo impeditivo.

## Ranking visivo
- Conferma rapidamente che l'ordine mostrato corrisponda al ranking 65/35 già coperto dal test JVM e che archiviati/eliminati non compaiano.

## Persistenza/lifecycle
- Background/foreground e riapertura Timer non causano crash o perdita delle sessioni quick-start persistite.

## UI data safety
- Nessun ID/epoch/encoding backend visibile.

# Acceptance
PASS solo se test ranking + compile/assemble + tutte e cinque le classi strumentali + QA manuale residuo passano; nessun crash/doppio insert/perdita selezione; scope PR stretto; nessun lavoro PH concorrente assorbito; integrazione pushata senza force.

Su PASS completa solo `PROMPT_ID=742618` con `roadmap_guard complete`; nessuna build Pixel, APK finale o Telegram in questo task: restano nella fase finale già prevista della campagna.

Output massimo 7 righe: RESULT, SHA, test/build, instrumented QA, manual residual QA, version/PR integration, blocker.
