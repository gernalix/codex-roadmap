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
6. QA mirata Timer:
   - zero sessioni: niente card “Nothing running”; launcher + ricerca occupano il corpo disponibile;
   - tap breve su un tag: crea subito una sola sessione con quel tag; Snackbar Undo elimina solo quella sessione;
   - long-press: entra in multiselect col primo tag già selezionato; tap successivi toggle; la ricerca non perde selezioni nascoste; ✔️ crea una sola sessione con tutti i tag scelti;
   - secondo timed-tag non viene accettato; parent tag continuano a essere applicati dal percorso esistente;
   - con almeno una sessione attiva: sessioni nella metà superiore e launcher nella metà inferiore, entrambi usabili;
   - il FAB `+` continua ad aprire il flusso completo precedente;
   - nessun ID/backend encoding grezzo appare nella UI.
7. Su failure correggi solo la causa diretta nei file della PR e ripeti solo il gate fallito. Vietati refactor/cleanup/audit generale.
8. Dopo PASS rifai un solo `fetch`: se il branch canonico è avanzato da quando hai creato la candidate => `BLOCKED` e non rifare QA. Altrimenti integra/pusha la candidate sul branch canonico senza force e chiudi/mergea la PR #2. Stop immediato.

# Acceptance
PASS solo se test mirato + compile/assemble + QA emulatore passano, la PR resta a scope stretto, non è stato assorbito lavoro PH concorrente e l'integrazione finale è pushata senza force.

Su PASS completa solo `PROMPT_ID=742618` con `roadmap_guard complete`; nessuna build Pixel, APK finale o Telegram in questo task: restano nella fase finale già prevista della campagna.

Output massimo 7 righe: RESULT, SHA, test/build, emulator QA, version handling, PR/integration, blocker.
