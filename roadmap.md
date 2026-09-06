# Codex Roadmap

[[README|README]] · [[spiegazioni|Spiegazioni]]

Ordine consigliato di esecuzione, riesaminato end-to-end sullo stato corrente di `PersonalHub/main`, sul dump Codex del 2026-09-05 e sull'audit statico dello stesso giorno. Eseguire **un solo task Codex alla volta** sullo stesso progetto secondo il workflow del README, salvo i blocchi esplicitamente marcati come continuous campaign.

Stato già acquisito e da NON reimplementare nei task futuri: database PH unificato; Settings/Database & Backup integrati; sync Datasette local-first; Places API key/address suggestions; shortcut pinnabili e percorso diretto ai moduli; protezione dell'app reale dai benchmark/test distruttivi; auto-export SAF generation-based con WorkManager/recovery/error state; hardening del Database Vault con import marker atomico/fail-safe e rollback SAF verificato; Soldi integrato con account, saldi, prodotto canonico e Git exchange; policy delete/FK Places↔Soldi corretta; Timer Alerts passati su `PersonalHub/main` a prompt in-app centrati e immediati con link/deep link cliccabili.

Finding tecnici ancora pendenti: People call-overlay deep-link/race/PII; Timer widget write-result; residui runtime/backup legacy Timer; capsulizzazione architetturale incompleta nel data layer. Dettagli storici: `audits/2026-09-05-personalhub-main-audit.md`.

## Ordine pendente

La raccomandazione `Recommended model` + `Reasoning` già contenuta in ciascun prompt resta **invariata** per l'esecuzione autonoma del singolo file. Accanto a ogni voce qui sotto è aggiunta una seconda scelta, `nuova policy 5.6`, da usare come alternativa sperimentale quando vuoi verificare se un modello più capace riduce errori, retry, tool-call e consumo quota complessivo.

### Continuous campaign: Hub Context Graph — task 1–6

I task **1–6** costituiscono un'unica **continuous campaign** ai sensi del README. Se il primo task pendente è il task 1, Codex deve eseguire consecutivamente **tutti e sei i task nella stessa sessione**, passando alla fase successiva solo dopo i targeted acceptance check della fase corrente; `FAIL`/`BLOCKED` interrompe immediatamente la campagna. **Campaign recommendation: GPT-5.6 Sol / medium.** Valgono le regole campaign del README: riuso del contesto già verificato, un solo target `version.txt = base + 1` per l'intero blocco, niente final APK/build-install/QA completi nelle fasi 1–5, una sola build/installazione/QA consolidata alla fine della fase 6 e aggiornamento della roadmap soltanto al completamento dell'intera campagna.

1. [[prompts/personalhub-complete-module-capsulization|personalhub-complete-module-capsulization]] — **nuova policy 5.6: GPT-5.6 Sol / high**
2. [[prompts/personalhub-hub-context-graph-foundation|personalhub-hub-context-graph-foundation]] — **nuova policy 5.6: GPT-5.6 Sol / high**
3. [[prompts/personalhub-hub-context-people-timer-places-vertical-slice|personalhub-hub-context-people-timer-places-vertical-slice]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
4. [[prompts/personalhub-hub-context-dynamic-composer|personalhub-hub-context-dynamic-composer]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
5. [[prompts/personalhub-hub-context-recursive-explorer|personalhub-hub-context-recursive-explorer]] — **nuova policy 5.6: GPT-5.6 Sol / high**
6. [[prompts/personalhub-hub-context-all-modules-resources-hardening|personalhub-hub-context-all-modules-resources-hardening]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
7. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]] — **nuova policy 5.6: GPT-5.6 Sol / high**
8. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
9. [[prompts/personalhub-timer-widget-write-result|personalhub-timer-widget-write-result]] — **nuova policy 5.6: GPT-5.6 Terra / low**
10. [[prompts/personalhub-timer-session-tag-picker-ux|personalhub-timer-session-tag-picker-ux]] — **nuova policy 5.6: GPT-5.6 Terra / low**
11. [[prompts/personalhub-timer-legacy-runtime-cleanup|personalhub-timer-legacy-runtime-cleanup]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
12. [[prompts/personalhub-places-visit-history-checkin|personalhub-places-visit-history-checkin]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
13. [[prompts/personalhub-places-sorting-map-navigation|personalhub-places-sorting-map-navigation]] — **nuova policy 5.6: GPT-5.6 Terra / low**
14. [[prompts/personalhub-places-geofence-alerts|personalhub-places-geofence-alerts]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
15. [[prompts/personalhub-autoexport-status-indicator|personalhub-autoexport-status-indicator]] — **nuova policy 5.6: GPT-5.6 Terra / low**
16. [[prompts/personalhub-global-screen-version-footer|personalhub-global-screen-version-footer]] — **nuova policy 5.6: GPT-5.6 Terra / low**
17. [[prompts/personalhub-dark-theme|personalhub-dark-theme]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
18. [[prompts/personalhub-global-audit-foundation-safe-undo|personalhub-global-audit-foundation-safe-undo]] — **nuova policy 5.6: GPT-5.6 Sol / high**
19. [[prompts/personalhub-global-audit-register-ui|personalhub-global-audit-register-ui]] — **nuova policy 5.6: GPT-5.6 Terra / low**

## Dipendenze / motivazione dell'ordine

- I primi sei task da `personalhub-complete-module-capsulization.md` a `personalhub-hub-context-all-modules-resources-hardening.md` sono la priorità assoluta e formano la **continuous campaign Hub Context Graph**. Restano prompt/fasi separati e self-contained, ma quando il blocco parte dalla posizione 1 vengono eseguiti nella stessa sessione secondo il README, riusando contesto e compilazioni già effettuate e rimandando build/installazione/QA finale alla fase 6. Campaign recommendation: GPT-5.6 Sol / medium.
- `personalhub-complete-module-capsulization.md` è il prerequisito: mantiene il singolo `personalhub.db`, elimina dipendenze feature-implementation → feature-implementation, mette persistence e contratti al posto giusto e prepara un composition root capace di ospitare in seguito un servizio neutro cross-module senza far controllare i moduli fra loro. GPT-5.6 Sol / medium / STRICT.
- `personalhub-hub-context-graph-foundation.md` crea il layer neutro HubEntity/Context N-ario, adapter registry, Context Type come dati e query forward/reverse/intersection. È deliberatamente privo di UI e adapter reali: nuove combinazioni future devono diventare configurazione, non nuove tabelle pairwise. GPT-5.6 Sol / medium / STRICT.
- `personalhub-hub-context-people-timer-places-vertical-slice.md` è il primo uso reale della fondazione: collega Person, Timer Session e Place canonici tramite lo stesso Context. Un Timer interval collegato a un Place resta l'unica fonte temporale della visita Places, senza doppio conteggio; selector e inline creation mantengono il nuovo Place a radius 75 m. GPT-5.5 / medium / STRICT.
- `personalhub-hub-context-dynamic-composer.md` rende le combinazioni creabili interamente dalla UI Android: Context ad hoc, modifica membri, Context Type/template, cardinalità, ordine, prefill e “salva come template”. Una nuova combinazione fra entity kind già registrati non deve richiedere codice. GPT-5.5 / medium / STRICT.
- `personalhub-hub-context-recursive-explorer.md` implementa la navigazione associativa del diagramma: da qualunque entità si restringe progressivamente uno scope (`Giovanni → Piazza Savona → Sessioni...`) usando l'intersezione dei Context compatibili, con reverse traversal, breadcrumb e sezioni correlate configurabili senza backlink duplicati. GPT-5.6 Sol / medium / STRICT.
- `personalhub-hub-context-all-modules-resources-hardening.md` applica infine lo stesso adapter pattern a tutti gli altri moduli presenti al momento dell'esecuzione, incluso un eventuale settimo modulo, aggiunge Resources generiche (URL/deep link/Workflowy/SAF) e consolida migration, export/import, sync, performance e QA cross-module. Non introduce integrazioni pairwise e non sostituisce le relazioni domain-specific che hanno semantica propria. GPT-5.5 / medium / STRICT.
- `personalhub-database-schema-upgrade-safety.md` viene subito dopo il blocco Hub Context per consolidare lo schema risultante e rendere sicuri gli aggiornamenti successivi: ogni vecchia versione supportata deve avere una catena di migrazione completa, il primo avvio del nuovo APK deve validare/migrare senza perdita dati e un futuro bump dello schema deve fallire nei test se manca una migrazione. GPT-5.6 Sol / medium / STRICT.
- People, widget Timer e tag picker restano correttivi localizzati e indipendenti e vengono eseguiti dopo la priorità Hub Context e il consolidamento globale degli upgrade DB.
- `personalhub-timer-session-tag-picker-ux.md` mantiene i tag selezionati come chip/card ben distinguibili e rende sempre disponibile la creazione del nome digitato quando non esiste già esattamente, anche se la ricerca mostra match più lunghi come `shopping` per `shop`.
- `personalhub-timer-legacy-runtime-cleanup.md` accorpa i residui del vecchio MultiTimeTracker su versione/AutoConsistency e first-run backup. Resta separato dal task Timer Alerts perché non deve riaprire il comportamento in-app appena consolidato.
- `personalhub-places-visit-history-checkin.md` viene dopo il blocco Hub Context perché usa ormai la semantica definitiva delle visite: accorpa overlap disambiguation, check-in storico manuale e “Dov'ero?” sullo stesso modello/query canonico senza reintrodurre una seconda fonte per le visite Timer-backed.
- `personalhub-places-sorting-map-navigation.md` resta separato perché è principalmente lista/mappa/query UI sulle metriche canoniche finali. `personalhub-places-geofence-alerts.md` resta separato perché coinvolge background location/notification e non deve riusare il vecchio Timer Alert system-notification path appena rimosso; può riusare solo infrastruttura Android realmente condivisa e ancora valida.
- `personalhub-autoexport-status-indicator.md` resta una feature UI localizzata. `personalhub-global-screen-version-footer.md` uniforma poi il dettaglio visivo della versione host su tutte le schermate. `personalhub-dark-theme.md` viene dopo la UI definitiva dei moduli.
- `personalhub-global-audit-foundation-safe-undo.md` accorpa modello/cattura semantica e undo compensativo conflict-safe perché la progettazione delle snapshot e della reversibilità deve servire direttamente l'inverso sicuro. La UI del registro resta separata e viene costruita solo sul backend definitivo.

## Disciplina globale

Ogni prompt deve restare self-contained e verificare esplicitamente eventuali prerequisiti; fuori da un blocco continuo non deve assumere una chat precedente. Per i task PersonalHub, il bootstrap specializzato autorevole è `MegaVault/ai/personalhubdoc.md`; il protocollo globale va letto solo nei casi di fallback esplicitamente previsti da quel file. Nei blocchi continui esplicitamente marcati, le fasi successive possono riusare esclusivamente il contesto verificato nelle fasi precedenti della stessa sessione, senza rilanciare bootstrap/esplorazione equivalenti.

Quando un prompt modifica PersonalHub, deve catturare la versione iniziale una sola volta e fissare per quel goal `target = base + 1`. Per una continuous campaign l'intero blocco è un unico goal di versionamento: il target viene fissato alla prima fase e riusato fino alla fine. Retry, rebuild, test o fasi successive dello stesso goal non possono incrementarlo di nuovo.

**Ordine solo numerico in roadmap:** l'ordine canonico è esclusivamente la posizione `1.`, `2.`, `3.`, ... in questa lista. I filename/titoli dei prompt devono essere semantici e non devono contenere prefissi o suffissi numerici/alfanumerici d'ordine. Inserire, rimuovere o riordinare un task richiede solo di rinumerare consecutivamente la lista; non si rinominano i file per la posizione. `PROMPT_ID` resta consentito perché è un identificatore casuale, non un indicatore d'ordine.

**Pre-localizzazione obbligatoria:** ogni prompt pendente deve indicare un set iniziale di file/classi reali verificati sullo stato corrente del repository target, sufficiente a iniziare il task senza scansione generale. Se un task precedente ha rinominato/spostato un file indicato, il prompt può autorizzare una singola ricerca mirata per il simbolo/classe noto. La disciplina operativa dettagliata su esplorazione, batching, tool call, retry, device QA, test, Git e stop resta definita dal bootstrap MegaVault governante e non va duplicata nei prompt.

Le fasi successive non devono riaprire l'architettura delle fasi precedenti salvo che un acceptance check dimostri una regressione o un prerequisito mancante.
