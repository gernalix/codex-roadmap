[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=742618 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST | type=Prompt`

> Esecuzione diretta. Non rifare discovery o redesign: la feature è già implementata nella PR `gernalix/PersonalHub#2`. Questo task esiste solo perché richiede checkout/toolchain Android/emulatore locali e coordinamento col lock PersonalHub.

# Goal
Verificare localmente la PR #2 `feature/timer-quick-start-tags` e integrarla nel branch canonico solo dopo PASS, senza interferire con altri task PersonalHub.

# Starting point verificato
- PR: `https://github.com/gernalix/PersonalHub/pull/2`, branch `feature/timer-quick-start-tags`;
- implementazione già fatta: launcher tag nella schermata Timer/Now, ricerca, tap singolo=start immediato, long-press=multiselect, selezioni persistenti durante la ricerca, ✔️ per avvio multi-tag, ranking recenza+frequenza 65/35, Snackbar Undo sull'esatta sessione appena creata, gerarchia tag/timed-tag, FAB legacy conservato;
- nessuna migration DB;
- test ranking già aggiunti in `QuickStartTagRankingTest.kt`;
- `version.txt` della feature branch è 44; il remoto corrente al momento dell'esecuzione resta l'autorità se nel frattempo è avanzato.

# Procedura minima
1. Leggi solo `AGENTS.md` e usa il preflight/lock PersonalHub già previsto. Se un altro task PH è attivo => `BLOCKED`; non aspettare e non fare polling.
2. `fetch` una volta. Crea una candidate locale dalla branch canonica corrente + PR #2 senza force/reset/stash. Se c'è un conflitto non banale o main contiene lavoro PH concorrente non ancora stabilizzato => `BLOCKED`, non risolvere modifiche estranee.
3. Se l'unico conflitto è `version.txt`, mantieni monotonicità: se 44 non è più maggiore della versione canonica, usa esattamente `current_main + 1`; nessun altro bump.
4. Esegui solo il test JVM mirato del ranking e il minimo assemble/compile necessario per l'app. Non eseguire suite/lint generali salvo failure concreta che lo richieda.
5. Avvia l'emulatore esclusivamente con `python3 tools/android_target_preflight.py --target emulator`; usa il serial restituito. Installa la candidate sull'emulatore, non sul Pixel reale.
6. Esegui SOLO il checklist QA qui sotto. Su failure correggi soltanto la causa diretta nei file della PR e ripeti soltanto il gate fallito. Vietati refactor, cleanup, audit generale o nuove feature.
7. Dopo PASS rifai un solo `fetch`: se il branch canonico è avanzato da quando hai creato la candidate => `BLOCKED` e non rifare QA. Altrimenti integra/pusha la candidate sul branch canonico senza force e chiudi/mergea la PR #2. Stop immediato.

# Checklist Android — Timer quick-start

## 1. Tap breve
- Con zero sessioni attive, un tap breve su un tag crea immediatamente UNA sola sessione associata a quel tag.
- Non deve aprirsi il dialog completo e non devono servire `+` o ✔️.
- La sessione deve apparire subito tra quelle attive.
- Nessun doppio insert/sessione duplicata.

## 2. Pressione lunga
- Long-press su un tag entra nella modalità multiselezione.
- Il primo tag deve risultare già selezionato.
- Devono comparire ✔️ e controllo annulla/chiudi.
- Il solo long-press non deve creare alcuna sessione.

## 3. Multiselezione
- In multiselect, tap brevi successivi aggiungono/rimuovono tag dalla selezione.
- ✔️ crea UNA sola sessione contenente tutti i tag selezionati.
- Annulla/chiudi esce senza creare sessioni.
- Nessun doppio insert/sessione duplicata.

## 4. Ricerca
- La query filtra immediatamente i tag per nome.
- Funziona sia in modalità normale sia in multiselect.
- Un tag selezionato resta selezionato anche se il filtro lo nasconde temporaneamente.
- Cancellando la query, il tag riappare ancora selezionato.
- Query senza risultati mostra uno stato vuoto leggibile e non genera errori/crash.

## 5. Undo
- Ogni quick-start mostra Snackbar di conferma con `Undo`.
- `Undo` elimina esattamente la sessione appena creata e nessun'altra sessione attiva.
- Se Undo non viene premuto, la sessione resta attiva.
- Verificare sia quick-start singolo sia multiselezione.

## 6. Timed tag
- Tap breve su un timed tag crea una sessione con il normale comportamento timed, incluso `expectedEnd` coerente con la durata configurata.
- Multiselect con un solo timed tag + tag normali è consentito.
- Se si tenta di selezionare un secondo timed tag, l'azione viene rifiutata con feedback comprensibile e senza creare sessioni invalide.
- Il quick-start non deve aggirare durata/notifiche/regole già esistenti dei timed tag.

## 7. Gerarchia tag
- Se il tag scelto ha parent automatici, la sessione quick-start deve ricevere la stessa closure gerarchica del normale editor.
- Nessuna differenza di associazioni rispetto al write path standard.

## 8. Layout senza sessioni attive
- Dopo il caricamento non deve comparire la vecchia card `Nothing running` come contenuto principale.
- Launcher + ricerca occupano sostanzialmente l'area utile del Timer.
- Il FAB `+` resta disponibile come percorso avanzato.
- Stati Loading/Error restano corretti e non vengono sostituiti prematuramente dal launcher.

## 9. Layout con sessioni attive
- Con almeno una sessione attiva, le sessioni occupano la parte superiore e il launcher la parte inferiore, circa 50/50.
- Entrambe le aree restano usabili/scrollabili quando necessario.
- Launcher, FAB, Snackbar e controlli di sistema non si sovrappongono in modo impeditivo.
- Avviare altre sessioni quick-start aggiorna il layout senza crash, salti anomali o perdita dei controlli.

## 10. Ordinamento tag
- I tag recenti/frequenti compaiono prima secondo il ranking implementato 65/35.
- L'ordine resta stabile mentre si osserva la schermata e non si rimescola da solo.
- Tag archiviati/eliminati non compaiono.
- A parità di uso il risultato resta deterministico.

## 11. Read-only / Time Machine
- In stato read-only il quick-start non deve consentire scritture tramite tap breve, long-press o ✔️.

## 12. Regressioni minime
- Stop/modifica/cancellazione delle sessioni esistenti continuano a funzionare.
- Il FAB `+` continua ad aprire il flusso completo precedente.
- Nessun ID, epoch grezzo o encoding backend appare nella UI.
- Background/foreground e riapertura del modulo Timer non fanno perdere le sessioni quick-start già persistite né causano crash.

# Acceptance
PASS solo se:
- test ranking mirato + compile/assemble passano;
- tutti i 12 blocchi del checklist Android passano sull'emulatore;
- nessun crash, doppio insert, perdita di selezione o divergenza dalle regole Timer esistenti;
- la PR resta a scope stretto;
- non viene assorbito lavoro PH concorrente;
- integrazione finale pushata senza force.

Su PASS completa solo `PROMPT_ID=742618` con `roadmap_guard complete`; nessuna build Pixel, APK finale o Telegram in questo task: restano nella fase finale già prevista della campagna.

Output massimo 7 righe: RESULT, SHA, test/build, emulator QA, version handling, PR/integration, blocker.
