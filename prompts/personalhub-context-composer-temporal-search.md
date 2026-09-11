[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=526841 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Realizzare in un solo passaggio cross-module due superfici che condividono gli stessi adapter e la stessa semantica temporale: (A) Composer top-level per creare Context N-ari persistenti; (B) Home → Cerca per ricostruire in sola lettura ciò che è successo in `[from,to)`. Inventaria adapter/query una volta, un solo bump versione e un solo QA finale.

Assorbe `214756` + `583921`. Riusa Hub Context esistente (`HubComposerState`, adapter, template/resource, Explorer); nessun secondo grafo o duplicazione dati.

# A — Composer
- rimuovi Context editing dal modal New/Edit Timer session e ogni dipendenza del save Timer dal save Context;
- promuovi/refactorizza il Composer esistente a destinazione Home full-screen Material 3, stato salvabile, selected pieces compatti, max ~5 suggerimenti, search long-tail e controlli avanzati secondari;
- nessun raw ID/entityKind in UI;
- anchor tempo: running Timer se univoco, altrimenti Now/editabile; storico con label leggibili;
- anchor luogo: pipeline Places esistente; inside-radius=>preselect, overlap=>pochi candidati, no match=>max 5 nearest, permission denied=>recent/search;
- ranking deterministico: co-occurrence con selezioni, luogo, recency, frequenza, tie-break stabile;
- rileva dal tempo selezionato Soldi transactions, Substances intake timestamped e WordPulse sessions; aggiungi solo il minimo adapter `substances/intake` se davvero manca;
- auto-selezioni visibili/removibili; cambiare tempo/luogo ricalcola automatici preservando manuali validi;
- preserva template/resources/Explorer e N-ary save/reverse traversal.

# B — Cerca temporale
Aggiungi Home → Cerca con Da/A + filtro moduli e timeline read-only merged. Usa un piccolo contratto condiviso temporale (`module/source/start/end/title...`) implementato dagli adapter/provider, senza nuova search table.

Semantica unica `[from,to)`: point `from<=t<to`; interval `start<to && (end==null || end>from)`. Includi ogni modulo con timestamp/range reale, paging/bounded query e stable tie-break; niente whole-table filtering in UI, nessuna scrittura Context/domain.

# Letture e test
Primo pass raggruppato solo su Home/MainActivity, HubContext Composer/Explorer/Repository/registry, SessionEditDialog e test Composer. Apri DAO/model specifici solo se l'adapter non può rispondere alla query richiesta; una lookup mirata per Places location e una per Substance intake.

Test condivisi: ranking/detection, time boundaries/interval overlap, merge/filter >=3 moduli, read-only, stato Composer recreation. Estendi il device test Composer già esistente anziché duplicarlo. UNA build, install Pixel e QA/screenshot consolidato su Composer + Search; poi Telegram delivery e commit/push.

# PASS
Timer editor senza Context; Composer top-level con anchor/ranking/detection/edit retroattivo; tutti i kind manualmente raggiungibili; Cerca corretta/paginata/read-only su moduli temporali; dati/sync/import invariati; test+QA PASS. Stop immediato.

Output: `PROMPT_ID`, `RESULT`, Composer/Timer changes, temporal contract/modules, ranking/detection, schema impact, test/QA, version/APK/delivery, SHA, blocker.
