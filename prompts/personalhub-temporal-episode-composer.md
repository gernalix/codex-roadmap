[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=742913 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

> Esecuzione diretta: questo file è il task Codex completo. Non eseguire `roadmap_guard.py select` e non rileggere roadmap/README/spiegazioni. Usa direttamente quanto segue come specifica autoritativa.

# Goal
Rifinire le superfici Home → Cerca e Composer già implementate affinché lavorino come una vista temporale unica, ordinata per moduli e adatta a creare un singolo “episodio” titolato. Eliminare i chip di selezione modulo/kind dalla UI primaria, mostrare tutti i risultati del periodo raggruppati in sezioni espanse/collassabili e consentire, al salvataggio, di scegliere con checkbox solo le entry che appartengono davvero all'episodio.

# Starting point già verificato — NON rifare discovery generale
Il precedente task temporal/context è già completato. Parti direttamente da questi fatti:

## Cerca
`app/src/main/java/com/gernalix/personalhub/HubTemporalSearchScreen.kt` oggi:
- usa `HubContextRuntime.temporalProviders()`;
- mantiene `selected` moduli e mostra un `FilterChip` per ciascun `moduleId`;
- interroga i provider con `[from,to)` e cursori per modulo;
- mergea i risultati con `mergeTemporalSlices(...)`;
- mostra poi una **lista piatta** di `HubTemporalRecord`.

Questa struttura dati/paging va riusata; va cambiata soprattutto la presentazione e il passaggio al salvataggio episodio.

## Composer
`core/hub-context/src/main/java/com/gernalix/personalhub/core/hubcontext/HubContextComposer.kt` oggi:
- `HubContextComposerScreen` ha Da/A, detection temporale, lista membri e `FilterChip` per scegliere adapter/kind;
- `HubComposerState.detect(...)` legge già i record temporali e può risolvere `HubEntityRef` canonici;
- `HubComposerState.save()` salva i membri ma non espone ancora il titolo nella UI;
- `HubContextRepository.createContext/updateContext(..., title)` e `HubContextRuntime.createContext/updateContext(..., title)` **supportano già un titolo persistente**: riusali, nessuna nuova tabella/colonna/migration;
- repository valida almeno 2 membri per Context: preserva questo contratto.

## People nel periodo
Non inventare timestamp People. Per mostrare persone associate al periodo, parti dai record temporali bounded già trovati (es. Timer session) e usa i Context/link esistenti per risolvere le persone collegate a quei record. Deduplica per `HubEntityRef`. Non fare una scansione globale People e non introdurre un secondo modello temporale.

## WordPulse fatigue — source of truth già esistente
La metrica fatigue canonica è già implementata in `gernalix/wordpulse` (es. `domain/TypingPerformance.kt` espone `fatigueScore: Int?` 0–100; `Alertness.kt`/test definiscono la semantica). **Non inventare né ricalcolare una seconda formula di stanchezza nel Hub.**

Nel tree PersonalHub usa l'implementazione/esposizione WordPulse già presente al momento dell'esecuzione. Se il modulo embedded non espone ancora `fatigueScore`, consulta soltanto i file canonici WordPulse direttamente necessari e porta/esponi il minimo valore già calcolato; niente redesign Alertness, Health Connect o PVT in questo task.

# UX unica Cerca / Composer
Costruisci/riusa un componente/state model condiviso per i risultati del periodo; non duplicare due implementazioni diverse.

Per un intervallo, mostra in alto una label leggibile del tipo:
`Periodo da 11.09.26 11:15 a 11.09.26 11:49`
(usando locale/formattazione già esistente, non hardcodare questo esempio).

Sotto mostra direttamente sezioni per modulo, per esempio:
- Places
  - Casa
- People
  - Mario
  - Gianni
- Transazioni
  - Lidl · spesa
- Timer
  - ...
- Substances
  - ...
- WordPulse
  - Stanchezza media: 42/100

Regole:
- **nessun chip modulo** in Cerca;
- **nessuna fila di chip modulo/kind come navigazione primaria** nel Composer temporale;
- tutte le sezioni rilevanti sono visibili nella stessa schermata e **aperte di default**;
- ogni sezione può essere collassata/espansa individualmente; stato `rememberSaveable`;
- ordine sezioni deterministico e label umane (`Transazioni`, non raw `soldi`; niente raw `moduleId/entityKind`);
- sezioni senza risultati possono mostrare un empty-state compatto invece di sparire, così la schermata resta prevedibile;
- preserva paging bounded per provider. Se esiste `nextCursor`, `Altri`/load-more deve appartenere alla relativa sezione, non a una lista piatta globale;
- niente ammasso: header sezione chiaro, spacing, card/row compatte, niente duplicati canonici.

# WordPulse nella vista temporale
Per il periodo selezionato, Cerca e Composer devono mostrare **solo una entry aggregata WordPulse**:
`Stanchezza media: N/100`

Non mostrare in queste due superfici:
- singole sessioni/word WordPulse;
- alertness;
- speed/rhythm/control/session-drift/sleep;
- baseline, PVT o altri dettagli.

Calcola/ottieni la media usando esclusivamente i valori `fatigueScore` canonici appartenenti al periodo secondo il boundary WordPulse disponibile. Se non esistono campioni validi mostra `Stanchezza media: non disponibile`, senza inventare zero. Mantieni internamente i `HubEntityRef` WordPulse sottostanti: l'entry aggregata può rappresentare più record canonici senza creare una synthetic table/entity.

# Salva come episodio
Cerca e Composer devono convergere sullo stesso flow:
1. browsing normale: mostra tutte le sezioni/entry, senza checkbox;
2. azione `Salva` / `Salva come episodio` entra nello **stesso screen** in selection mode oppure apre il Composer preservando esattamente intervallo e risultati, senza rifare query inutile;
3. in selection mode tutte le entry selezionabili mostrano checkbox;
4. l'utente seleziona solo le entry che appartengono al medesimo episodio;
5. mostra un campo titolo obbligatorio e salva il titolo tramite il `title` già supportato da Hub Context;
6. il commit finale salva **solo** i canonical refs selezionati, rispettando il minimo di 2 membri già imposto dal repository;
7. nessun risultato non selezionato deve finire nel Context.

Per la singola entry aggregata WordPulse: una checkbox rappresenta l'aggregato; se selezionata, salva i canonical WordPulse refs sottostanti pertinenti al periodo, ma continua a mostrare una sola riga `Stanchezza media` in UI. Non creare un'entità sintetica solo per l'aggregato.

Per People derivati da Context/link, la checkbox salva i relativi `HubEntityRef` People canonici.

Selection/title/collapse state devono sopravvivere alla recreation. Cambiare Da/A e rilanciare la ricerca invalida risultati/selezioni non più appartenenti al nuovo intervallo in modo deterministico.

# Manual add / advanced
Non eliminare la capacità del Composer di aggiungere manualmente entità non emerse dal periodo, template/resource/Explorer o editing Context esistente. Sposta l'eventuale ricerca manuale per kind in una sezione/azione secondaria `Aggiungi altro`/advanced senza chip permanenti dei moduli nella schermata principale. Riusa gli adapter e `HubComposerState`; niente nuovo registry.

# Letture consentite al primo pass
1. `app/.../HubTemporalSearchScreen.kt` e `MainActivity.kt` solo per handoff/navigation;
2. `core/hub-context/.../HubContextComposer.kt`, `HubContextRuntime.kt`, `HubContextRepository.kt`;
3. temporal record/provider/adapter già usati dal task completato, solo se servono grouping/paging;
4. adapter/context link Timer→People soltanto per risolvere People dal set temporale;
5. WordPulse: solo boundary dati/adapter per ottenere `fatigueScore`; se manca nel tree PH, solo i file canonici `gernalix/wordpulse` strettamente necessari come source-of-truth.

Non leggere interi moduli e non rieseguire inventory del task completato.

# Verification
Aggiungi/aggiorna test mirati per:
- nessun module FilterChip in Cerca e nessun module/kind chip permanente nel Composer primary flow;
- grouping deterministico per modulo, tutte sezioni expanded di default + collapse indipendente/recreation;
- query `[from,to)` e cursori per sezione invariati;
- People derivati solo da link dei record temporali bounded, senza scan globale;
- WordPulse: una sola riga media fatigue, media corretta su campioni validi, `non disponibile` senza campioni, nessun altro dettaglio WordPulse;
- Search → save handoff senza query duplicata quando i risultati sono già disponibili;
- selection mode: checkbox, titolo obbligatorio, solo selected refs persistiti, min 2 membri, aggregate WordPulse→underlying refs, recreation;
- Context title realmente persistito e riletto.

Una build, un solo bump versione se previsto dal bootstrap del repo, install Pixel e una QA consolidata: scegli periodo noto → verifica sezioni/collapse → entra in Salva → seleziona subset di almeno 2 entry → titolo → salva → riapri Context e verifica titolo+membri. Verifica WordPulse soltanto come `Stanchezza media`.

# PASS / stop
PASS solo se Cerca e Composer mostrano tutti i moduli in sezioni ordinate/collassabili senza chip primari, WordPulse espone esclusivamente la fatigue media del periodo, il flow Salva crea un Context titolato con soltanto le checkbox selezionate e nessun nuovo schema temporale/context viene introdotto. Nessun redesign fuori scope.

Su PASS, dopo il push del repo target, finalizza questo task nella roadmap con `python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 742913 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 742913`. `push_verified=git_push_exit_0` è prova sufficiente: non fare verifiche Git successive sulla roadmap e non aprire il task successivo. Su BLOCKED/FAIL non avanzare la roadmap. Stop immediato.

Output conciso: `PROMPT_ID`, `RESULT`, grouped modules/collapse, People derivation, WordPulse fatigue average, episode selection/title, schema impact, tests/Pixel, version/APK/delivery, SHA, blocker.
