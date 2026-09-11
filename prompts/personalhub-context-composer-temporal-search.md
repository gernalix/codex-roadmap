[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=526841 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STANDARD`

> Esecuzione diretta: questo file è il task Codex completo. Non eseguire `roadmap_guard.py select` e non rileggere roadmap/README/spiegazioni. Usa direttamente quanto segue come specifica autoritativa.

# Goal
Completare in un solo passaggio cross-module due superfici che condividono adapter e semantica temporale: (A) Composer top-level per Context N-ari persistenti; (B) Home → Cerca read-only su `[from,to)`. L'architettura temporale di base è già stata preparata: **non ridisegnarla e non fare inventory generale**.

# Starting point già verificato
Usa `.codex/CODE_MAP.tsv` solo come routing e parti direttamente da questi fatti/file:

## Hub Context / Composer
- `core/hub-context/.../HubContextComposer.kt` contiene già `HubComposerState`, Saver, template/resource support, N-ary members, search/create/save e `HubContextComposerDialog`;
- oggi `HubComposerState` richiede un `anchor: HubEntityRef` non-null e il Composer è solo un `AlertDialog`, quindi non è ancora una destinazione Home top-level;
- `HubContextRepository`, `HubContextExplorer` e reverse traversal esistono già: preservali, nessun secondo grafo/table;
- `app/MainActivity.kt` è ancora solo launcher Home/Settings: non esiste Composer/Search top-level.

## Timer coupling da rimuovere
`feature/multitimetracker/.../SessionEditDialog.kt` oggi:
- crea `contextEditor = rememberSessionContextEditorState(session.id)`;
- mostra `SessionContextEditor(contextEditor, readOnly)`;
- per nuova sessione chiama `saveContextForCreatedTimerSession(...)` prima di dismiss;
- per sessione esistente `contextEditor.save(session.id)` precede `onSaveMeta`.
Rimuovi questo editing/coupling dal dialog: il salvataggio Timer non deve più dipendere dal salvataggio Context. `HubContextLinks` read-only può restare solo se utile e non reintroduce editing.

## Contratto temporale già aggiunto
Riusa, non duplicare:
- `HubTemporalRecord.kt`: `HubTemporalKind.POINT|INTERVAL`, semantica esatta `POINT: from<=t<to`, `INTERVAL: start<to && (end==null || end>from)`, stable merge `mergeTemporalSlices(...)`;
- `HubTemporalProvider.kt`: `HubTemporalQuery(fromMs,toMs,limit<=200,cursor)`, `HubTemporalPage`, `HubTemporalProvider`; il contratto impone query bounded nel data layer, non whole-table filtering UI;
- test `HubTemporalRecordTest` e `HubTemporalProviderTest` già coprono boundaries, running intervals, stable tie-break, filtro >=3 moduli e limiti.
Prima esegui questi test; modifica il contratto solo su failure/requisito concreto.

## Adapter già verificati
Non cercare da zero:
- Timer `TimerSessionHubAdapter`: `timer/session`, capabilities `time_interval,activity`, summary ha già `start_ms`/`end_ms`;
- WordPulse `WordSessionHubAdapter`: `wordpulse/word_session`, `time_interval,activity`, summary ha già `start_ms`/`end_ms`;
- Soldi `SoldiTransactionHubAdapter`: `soldi/transaction` esiste, ma summary non espone ancora temporal attributes; il model ha `occurredAt`;
- Substances `SubstanceHubAdapter`: copre solo `substances/substance`; **manca davvero** il minimo entity/provider per intake timestamped se necessario alla detection/search;
- Places `PlacesHubAdapter`: copre solo `places/place`; le visite temporali vanno lette dal boundary Places esistente, non trasformate in un secondo grafo.
`PersonalHubApplication` registra già People/Timer/Places/Soldi/Substances/WordPulse/Resource adapter; estendi il registry minimo per temporal provider invece di creare un runtime parallelo.

# A — Composer top-level
Promuovi/refactorizza il Composer esistente a destinazione Home full-screen Material 3 con stato salvabile. Riusa `HubComposerState`, repository, template/resources/Explorer.

Requisiti:
- supporta creazione top-level senza anchor obbligatorio; quando viene aperto da un'entità può ancora avere anchor iniziale;
- selected pieces compatti, max ~5 suggerimenti, search long-tail, controlli avanzati secondari; nessun raw ID/entityKind visibile;
- anchor tempo: running Timer se univoco, altrimenti Now/editabile; storico con label leggibili;
- anchor luogo: riusa pipeline Places: inside-radius=>preselect, overlap=>pochi candidati, no match=>max 5 nearest, permission denied=>recent/search;
- ranking deterministico: co-occurrence con selezioni, luogo, recency, frequenza, tie-break stabile;
- dal tempo selezionato rileva Soldi transactions, Substances intake e WordPulse sessions usando i provider temporali; auto-selezioni visibili/removibili;
- cambiare tempo/luogo ricalcola solo gli automatici preservando manuali validi;
- tutti i kind restano manualmente raggiungibili; preserva template/resources/Explorer e N-ary save/reverse traversal.

# B — Home → Cerca temporale
Aggiungi Home → Cerca con Da/A + filtro moduli e timeline merged read-only usando **solo** `HubTemporalProvider` + `mergeTemporalSlices` già preparati.

Implementa provider bounded/paged per ogni modulo con timestamp/range reale. Parti direttamente da Timer, WordPulse, Soldi, Substances intake e Places visits; includi People solo se il suo boundary autorevole espone eventi timestamped pertinenti. Query/DAO devono applicare `[from,to)` prima di restituire i dati. Stable cursor/tie-break; nessuna search table, nessuna scrittura Context/domain.

# Letture consentite
Primo pass soltanto:
1. `app/MainActivity.kt`;
2. `HubContextComposer.kt`, `HubContextRuntime.kt`, `HubContextRepository.kt`, `HubContextExplorer.kt`;
3. `SessionEditDialog.kt`;
4. i cinque adapter verificati sopra;
5. DAO/model diretto soltanto per implementare il provider che manca.
Non leggere interi moduli. Per Places apri soltanto query visite/location direttamente necessarie; per Substances soltanto intake query/entity; per People solo se incluso per timestamp reale.

# Test / QA
- prima: `HubTemporalRecordTest` + `HubTemporalProviderTest`;
- poi: ranking/detection, provider time boundaries/paging, merge/filter >=3 moduli, read-only, Composer recreation/top-level/no-anchor;
- aggiorna il test Composer esistente invece di duplicare harness;
- test mirato che Timer save non invoca più Context save;
- UNA build, un solo bump versione, install Pixel e QA consolidata Composer + Search; Telegram delivery; commit/push.

# PASS / stop
Timer editor senza Context editing/coupling; Composer top-level con anchor/ranking/detection/edit retroattivo; tutti i kind manualmente raggiungibili; Cerca corretta/paginata/read-only sui moduli temporali; dati/sync/import invariati; test+QA PASS. Nessun audit generale o refactor fuori scope.

Su PASS, dopo il push del repo target, finalizza questo task nella roadmap con `python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 526841 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 526841`. `push_verified=git_push_exit_0` è prova sufficiente: non fare verifiche Git successive sulla roadmap e non aprire il task successivo. Su BLOCKED/FAIL non avanzare la roadmap. Stop immediato.

Output conciso: `PROMPT_ID`, `RESULT`, Composer/Timer changes, temporal providers/modules, ranking/detection, schema impact, test/QA, version/APK/delivery, SHA, blocker.
