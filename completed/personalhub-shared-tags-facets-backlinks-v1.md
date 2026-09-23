PROMPT_ID=522084
/goal

Porta `gernalix/PersonalHub` a completare integralmente il sistema condiviso Tags + Facets + backlink cross-module definito in `docs/TAGS_FACETS_LINKS.md`, preservando tutti i dati esistenti e senza introdurre un secondo graph parallelo a Hub Context.

MODEL=GPT-5.6 Sol
REASONING=medium
MEGAVAULT=STRICT
PROJECT_ID=49
REPO=gernalix/PersonalHub

## Starting point autoritativo

Usa il current remote canonical tip e il worktree assegnato da:
`python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 522084`

Procedi solo se il claim conferma `running`.

Per localizzare il codice parti SOLO da:
- `docs/TAGS_FACETS_LINKS.md` — specifica funzionale/architetturale vincolante;
- `.codex/CODE_MAP.tsv`, voce `hub.tags_facets`;
- `docs/ARCHITECTURE.md`;
- Hub Context esistente e i file direttamente indicati dal CODE_MAP.

Non fare audit generale del repo. Amplia la discovery solo quando un acceptance criterion non è risolvibile dai path già noti. Riusa risultati già verificati nella sessione. Nessun comando/test equivalente ripetuto senza nuova evidenza.

## Outcome obbligatorio

Implementa un solo motore tecnico condiviso dei tag per:
- People
- Timer
- Places
- Substances
- Soldi

WordPulse e Salute sono fuori scope.

Il vocabolario resta namespaced: un tag locale di Places non deve contaminare Soldi ecc. Supporta tag esplicitamente globali/cross-module solo quando richiesto dalla specifica.

Mantieni distinta la semantica:
- Entity = Person / Place / Substance / Account ecc.;
- Event/record = transazione, Timer session, intake ecc.;
- Tag = classificazione libera;
- Facet = rappresentazione comune ricercabile/selezionabile di Entity o Tag.

NON trasformare People, Places, Substances, transazioni o Timer session in semplici tag.

## Timer — requisito inderogabile

Separa realmente i tre vocabolari:
- `timer.now`
- `timer.events`
- `timer.since_when`

Now/Timeline/session/task/time-fence/chains usano `timer.now`.
Events/templates/entries/macros usano `timer.events`.
Since When/life periods usa `timer.since_when`.

Create/rename/archive/delete/merge di un tag in un namespace non deve mutare un omonimo negli altri.

Migrazione legacy lossless:
1. tag referenziato da una sola superficie -> relativo namespace;
2. tag referenziato da più superfici -> copie indipendenti + remap per superficie;
3. tag senza riferimenti -> `timer.now`;
4. preserva associazioni e metadata applicabili;
5. nessun merge implicito per omonimia cross-namespace.

Se rimane una schermata Timer Tags, deve mostrare chiaramente `Now | Events | Since when`.

## Facet, picker e linking

Estendi l'attuale Hub Context / HubEntityBinding; non creare un secondo sistema di relazioni.

Implementa un picker semantico condiviso capace di cercare i provider compatibili e i tag da un unico campo, con risultati tipizzati, per esempio:
`[👤 Ahsan] [📍 Copenhagen] [💊 Meth] [🏷 holiday]`.

Il picker deve supportare almeno:
- autocomplete live;
- entity adapter + tag compatibili;
- icona/tipo visibile;
- `#foo` come scorciatoia tag;
- recenti / pinned / frequenti;
- creazione tag inline dove ammessa;
- namespace isolation;
- suggerimenti contestuali/co-occurrence come suggerimenti, non auto-applicazione di default.

Mantieni separati i campi strutturali obbligatori del dominio.

I link cross-module devono essere salvati una volta e navigabili in entrambe le direzioni tramite Hub Context. Supporta many-to-many e ruoli semantici quando disponibili.

Caso minimo obbligatorio:
una transazione Soldi con Person A + Place P + Tag T1 + Tag T2 deve comparire nei backlink di People/A, Places/P, Tags/T1 e Tags/T2; ogni tap apre la transazione originale, senza copie del record.

## Migrazione/consolidamento tag esistenti

Migra realmente nel motore comune, senza lasciare motori live concorrenti:
- People: `tags` / `contact_tags`;
- Places: `place_tags` / `place_tag_cross_ref`;
- Soldi: `finance_tags`, transaction tags, recurrence tags;
- Timer: sistema legacy secondo lo split sopra;
- Substances: nuovo tagging comune senza convertire i campi strutturali in tag.

Soldi: correggi obbligatoriamente il bug per cui il tag selezionato nell'editor transazione non viene persistito.

## Funzioni condivise obbligatorie

Implementa una volta e riusa:
- multi add/remove;
- chip comuni + overflow `+N`;
- autocomplete e inline create;
- AND / OR / NOT;
- filtro `No tags`;
- recenti / frequenza / last-used / usage count;
- rename;
- archive/unarchive;
- delete sicuro;
- merge;
- aliases;
- pinned/favorite;
- bulk add/remove;
- copia tag da record compatibile;
- duplicate/near-duplicate prevention;
- provenance `manual | suggested | automatic`;
- undo tramite infrastruttura Activity/audit esistente;
- saved combinations come saved filters/query, NON come nuovi tag.

Aggiungi una UI PH-level Tags con ricerca, namespace, usage per modulo/entity kind, recent linked items e manutenzione tag.

## Integrazione per modulo

People:
- motore comune, filtri, bulk tagging, Related/backlink e manutenzione condivisa.

Places:
- motore comune, list/map filters, multi-tag, bulk tagging, Related/backlink; eventuale marker styling da tag/icon/color senza duplicare la categoria strutturata.

Timer:
- split namespace sopra;
- analytics/filtri Timeline su `timer.now`;
- Events su `timer.events`;
- Since When su `timer.since_when`;
- ranking/quick-start limitati al namespace corretto.

Substances:
- sostanza/dose/unità/timestamp/prescription restano strutturati;
- tag solo per contesto/classificazione;
- filtri, facet, backlink, aggregazioni descrittive;
- nessuna inferenza medica.

Soldi:
- persistenza tag funzionante;
- tag multipli;
- universal facet picker per contesto opzionale;
- search per tag/facet + AND/OR/NOT/untagged;
- photos-only compatibile con gli stessi filtri;
- aggregazioni spesa per tag/periodo;
- recurrence tags sul motore comune;
- Account/Category/Amount/Transaction restano strutturati.

## Room e sicurezza dati

Questa è una migrazione DB ad alto rischio:
- `personalhub.db` resta unica authority writable;
- migrazione Room esplicita, deterministica e crash-safe;
- nessun destructive migration/reset;
- nessun CSV/stringa delimitata per le associazioni;
- FK integre;
- schema export aggiornato;
- backup/import/export coerenti col nuovo modello;
- preserva gli ID canonici quando possibile;
- se lo split richiede nuovi ID, mapping deterministico e testato.

Prima di cambiare API Room/pubbliche esegui i consumer-preflight richiesti da `AGENTS.md`. Rispetta i feature boundaries: niente dipendenze feature->feature.

## Strategia di implementazione/token

Fai SOLO questo goal. Nessun cleanup, modernizzazione o refactor fuori scope.

Procedi per strati coerenti sullo stesso worktree:
1. modello/migrazione condivisa;
2. adapter/repository comuni;
3. migrazione dei consumer esistenti;
4. facet picker + backlink/shared UI;
5. integrazioni module-specific;
6. test mirati e QA.

Dopo ogni failure usa l'evidenza del primo gate fallito per la correzione minima. Non ricominciare discovery generale.

Non creare follow-up per failure tecnici correggibili in-scope. Un problema collaterale non bloccante va segnalato senza investigarlo.

## Gate obbligatori

Testa almeno:
- migrazione People;
- migrazione Places;
- Soldi transaction + recurrence tags;
- split Timer: Now-only, Events-only, SinceWhen-only, 2 superfici, 3 superfici, tag inutilizzato;
- indipendenza rename/archive/delete/merge tra i tre namespace Timer;
- namespace isolation cross-module;
- global tags espliciti;
- alias + merge + duplicate normalization;
- AND/OR/NOT/untagged;
- picker multi-provider;
- Person <-> transaction backlink;
- Place <-> transaction backlink;
- Tag <-> transaction backlink;
- deep-link al record originale;
- Soldi salva davvero tag;
- photos-only + facet filter;
- backup/export/import round-trip;
- `checkArchitectureBoundaries`.

Preferisci test leaf e compile mirate. Amplia solo se rischio o failure lo richiede.

Per QA Android usa esclusivamente il workflow emulator canonico già documentato. Verifica almeno:
- tag in People, Places, Soldi, Substances;
- tre tag omonimi indipendenti in Timer Now/Events/Since when;
- rename di uno senza mutare gli altri;
- transazione Soldi con Person + Place + tag;
- backlink da People, Places e Tag;
- universal facet search;
- merge;
- No tags;
- bulk tagging.

Non usare device fisici salvo necessità concreta derivata dai gate; se necessario, usa solo gli helper di `AGENTS.md` e preserva i dati reali.

## Acceptance / stop

PASS solo quando `docs/TAGS_FACETS_LINKS.md` è implementato integralmente oppure ogni punto eventualmente già presente è stato verificato equivalente, con:
- unico motore condiviso;
- migrazione legacy lossless;
- Timer Now/Events/Since when indipendenti;
- universal facet picker;
- backlink bidirezionali;
- Soldi persistence corretta;
- ricerca/filtri/manutenzione condivisi;
- WordPulse/Salute non coinvolti;
- migration/architecture/unit/device gates pertinenti PASS;
- nessuna perdita dati.

Non dichiarare PASS per sola architettura, scaffolding o migrazione parziale.

Al PASS finalizza una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 522084 --confirm-executed`

Per hard blocker esterno o FAIL usa `roadmap_result.py` con lo stesso PROMPT_ID e risultato corretto.

Dopo PASS: STOP immediato. Nessun audit ulteriore.

Output finale max 12 righe:
PROMPT_ID
RESULT
SCHEMA_MIGRATION
TIMER_NAMESPACES
MODULES
FACET_PICKER
BACKLINKS
SOLDI_TAG_PERSISTENCE
SEARCH_MAINTENANCE
TESTS
ANDROID_QA
DATA_LOSS/BLOCKER