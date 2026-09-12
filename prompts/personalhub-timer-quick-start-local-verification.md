[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=742618 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST | type=Prompt`

> Esecuzione diretta. Non rifare discovery o redesign: la feature è già implementata nella PR `gernalix/PersonalHub#2`. Questo task esiste solo perché richiede checkout/toolchain Android/emulatore locali e coordinamento col lock PersonalHub.

# Goal
Verificare localmente la PR #2 `feature/timer-quick-start-tags` e integrarla nel branch canonico solo dopo PASS, senza interferire con altri task PersonalHub.

# Starting point verificato
- PR: `https://github.com/gernalix/PersonalHub/pull/2`, branch `feature/timer-quick-start-tags`;
- implementazione già fatta: launcher tag nella schermata Timer/Now, ricerca, tap singolo=start immediato, long-press=multiselect, selezioni persistenti durante la ricerca, ✔️ per avvio multi-tag, ranking recenza+frequenza 65/35, Snackbar Undo sull'esatta sessione appena creata, gerarchia tag/timed-tag, FAB legacy conservato;
- nessuna migration DB;
- test JVM ranking già presenti in `QuickStartTagRankingTest.kt`;
- test strumentali Compose già presenti in `feature/multitimetracker/src/androidTest/.../QuickStartTagLauncherInstrumentedTest.kt`: tap breve, long-press, multiselect, ricerca con selezioni nascoste persistenti e Undo sull'esatto sessionId appena creato;
- `version.txt` della feature branch è 44; non fare un secondo bump per i test. Il remoto corrente al momento dell'esecuzione resta l'autorità se nel frattempo è avanzato.

# Procedura minima
1. Leggi solo `AGENTS.md` e usa il preflight/lock PersonalHub già previsto. Se un altro task PH è attivo => `BLOCKED`; non aspettare e non fare polling.
2. `fetch` una volta. Crea una candidate locale dalla branch canonica corrente + PR #2 senza force/reset/stash. Se c'è un conflitto non banale o main contiene lavoro PH concorrente non ancora stabilizzato => `BLOCKED`, non risolvere modifiche estranee.
3. Se l'unico conflitto è `version.txt`, mantieni monotonicità: se 44 non è più maggiore della versione canonica, usa esattamente `current_main + 1`; nessun altro bump.
4. Esegui il test JVM mirato del ranking e il minimo compile/assemble necessario. Non eseguire suite/lint generali salvo failure concreta.
5. Avvia l'emulatore esclusivamente con `python3 tools/android_target_preflight.py --target emulator`; usa il serial restituito. Non usare il Pixel reale.
6. Esegui la sola classe strumentale `QuickStartTagLauncherInstrumentedTest`. Deve passare integralmente. Su failure correggi solo la causa diretta e ripeti solo questa classe/test fallito.
7. Per tap breve, long-press, multiselect, ricerca e Undo **non duplicare manualmente** ciò che la classe strumentale ha già provato. Nel QA manuale verifica solo gli aspetti non coperti automaticamente: timed tag, gerarchia tag, layout 0/≥1 sessioni, ranking visivo/stabilità, read-only e regressioni minime sotto.
8. Dopo PASS rifai un solo `fetch`: se il branch canonico è avanzato da quando hai creato la candidate => `BLOCKED` e non rifare QA. Altrimenti integra/pusha la candidate sul branch canonico senza force e chiudi/mergea la PR #2. Stop immediato.

# Copertura strumentale obbligatoria
La classe `QuickStartTagLauncherInstrumentedTest` deve verificare e passare questi casi:
- **tap breve:** un tap su un chip emette esattamente un avvio e solo col tag tappato;
- **pressione lunga:** entra in multiselect, preseleziona il primo tag, mostra il controllo di conferma e non avvia ancora nulla;
- **multiselezione:** aggiunge un secondo tag e ✔️ emette una sola sessione contenente entrambi;
- **ricerca:** filtra i chip, nasconde temporaneamente un tag selezionato senza perderne lo stato, ripristina la selezione quando la query viene cancellata e conferma entrambi i tag;
- **Undo:** attraverso la vera `NowScreen` + fake boundary crea una sessione con ID noto, mostra lo Snackbar e `Undo` cancella esattamente quell'ID.

# QA manuale residuo — solo ciò che i test non coprono

## Timed tag
- Tap breve su un timed tag crea una sessione con il normale comportamento timed, incluso `expectedEnd` coerente.
- Un solo timed tag + tag normali è consentito; un secondo timed tag viene rifiutato con feedback comprensibile.
- Nessun bypass delle regole/notifiche timed esistenti.

## Gerarchia tag
- Tag con parent automatici ricevono la stessa closure gerarchica del normale editor.

## Layout
- Zero sessioni: niente vecchia card `Nothing running`; launcher + ricerca occupano il corpo disponibile; FAB `+` resta accessibile; Loading/Error restano corretti.
- ≥1 sessione: sessioni nella metà superiore e launcher nella metà inferiore circa 50/50; entrambe le aree sono usabili/scrollabili e non si sovrappongono in modo impeditivo a FAB/Snackbar.

## Ranking
- Tag recenti/frequenti prima secondo 65/35; ordine stabile; archiviati/eliminati assenti; tie deterministico.

## Read-only / Time Machine
- Nessuna scrittura tramite quick-start in stato read-only.

## Regressioni minime
- Stop/modifica/cancellazione sessioni esistenti ancora funzionanti.
- FAB `+` apre ancora il flusso completo.
- Nessun ID/epoch/encoding backend visibile.
- Background/foreground e riapertura Timer non causano crash o perdita di sessioni quick-start persistite.

# Acceptance
PASS solo se test ranking + compile/assemble + intera `QuickStartTagLauncherInstrumentedTest` + QA manuale residuo passano; nessun crash/doppio insert/perdita selezione; scope PR stretto; nessun lavoro PH concorrente assorbito; integrazione pushata senza force.

Su PASS completa solo `PROMPT_ID=742618` con `roadmap_guard complete`; nessuna build Pixel, APK finale o Telegram in questo task: restano nella fase finale già prevista della campagna.

Output massimo 7 righe: RESULT, SHA, test/build, instrumented QA, manual residual QA, version/PR integration, blocker.
