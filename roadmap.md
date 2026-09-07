# Codex Roadmap

[[README|README]] · [[spiegazioni|Spiegazioni]]

Ordine consigliato di esecuzione, riesaminato end-to-end sullo stato corrente di `PersonalHub/main`, sul dump Codex del 2026-09-05 e sull'audit statico dello stesso giorno. Eseguire **un solo task Codex alla volta** sullo stesso progetto secondo il workflow del README, salvo i blocchi esplicitamente marcati come continuous campaign.

Stato già acquisito e da NON reimplementare nei task futuri: database PH unificato; Settings/Database & Backup integrati; sync Datasette local-first; Places API key/address suggestions; shortcut pinnabili e percorso diretto ai moduli; protezione dell'app reale dai benchmark/test distruttivi; auto-export SAF generation-based con WorkManager/recovery/error state; hardening del Database Vault con import marker atomico/fail-safe e rollback SAF verificato; Soldi integrato con account, saldi, prodotto canonico e Git exchange; policy delete/FK Places↔Soldi corretta; Timer Alerts passati su `PersonalHub/main` a prompt in-app centrati e immediati con link/deep link cliccabili; capsulizzazione dei moduli completata; Hub Context Graph generico disponibile per People, Timer, Places, Soldi, Substances, WordPulse e Resources, con navigazione all'entità esatta, risoluzione batch, ricerca Timer/Places bounded e Context Type di sistema bloccati.

Finding tecnici ancora pendenti: blocco New session Timer dovuto al tentativo di salvare Hub Context contro il draft ID `-1` prima della creazione della sessione reale; UI Composer v29 embedded/nested in Timer giudicata inutilizzabile e da sostituire con una sezione top-level dedicata; People call-overlay deep-link/race/PII; Timer widget write-result; residui runtime/backup legacy Timer. Dettagli storici: `audits/2026-09-05-personalhub-main-audit.md`.

## Ordine pendente

La raccomandazione `Recommended model` + `Reasoning` già contenuta in ciascun prompt resta **invariata** per l'esecuzione autonoma del singolo file. Accanto a ogni voce qui sotto è aggiunta una seconda scelta, `nuova policy 5.6`, da usare come alternativa sperimentale quando vuoi verificare se un modello più capace riduce errori, retry, tool-call e consumo quota complessivo.

1. [[prompts/personalhub-timer-new-session-canonical-entity-save-bug|personalhub-timer-new-session-canonical-entity-save-bug]] — **nuova policy 5.6: GPT-5.6 Terra / medium**
2. [[prompts/personalhub-context-composer-redesign|personalhub-context-composer-redesign]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
3. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]] — **nuova policy 5.6: GPT-5.6 Sol / high**
4. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
5. [[prompts/personalhub-timer-widget-write-result|personalhub-timer-widget-write-result]] — **nuova policy 5.6: GPT-5.6 Terra / low**
6. [[prompts/personalhub-timer-session-tag-picker-ux|personalhub-timer-session-tag-picker-ux]] — **nuova policy 5.6: GPT-5.6 Terra / low**
7. [[prompts/personalhub-timer-legacy-runtime-cleanup|personalhub-timer-legacy-runtime-cleanup]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
8. [[prompts/personalhub-places-visit-history-checkin|personalhub-places-visit-history-checkin]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
9. [[prompts/personalhub-places-sorting-map-navigation|personalhub-places-sorting-map-navigation]] — **nuova policy 5.6: GPT-5.6 Terra / low**
10. [[prompts/personalhub-places-geofence-alerts|personalhub-places-geofence-alerts]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
11. [[prompts/personalhub-autoexport-status-indicator|personalhub-autoexport-status-indicator]] — **nuova policy 5.6: GPT-5.6 Terra / low**
12. [[prompts/personalhub-global-screen-version-footer|personalhub-global-screen-version-footer]] — **nuova policy 5.6: GPT-5.6 Terra / low**
13. [[prompts/personalhub-dark-theme|personalhub-dark-theme]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
14. [[prompts/personalhub-global-audit-foundation-safe-undo|personalhub-global-audit-foundation-safe-undo]] — **nuova policy 5.6: GPT-5.6 Sol / high**
15. [[prompts/personalhub-global-audit-register-ui|personalhub-global-audit-register-ui]] — **nuova policy 5.6: GPT-5.6 Terra / low**

## Dipendenze / motivazione dell'ordine

- `personalhub-timer-new-session-canonical-entity-save-bug.md` viene per primo perché l'app corrente non riesce ad avviare una nuova sessione Timer: il draft usa ID `-1`, ma il dialog prova a salvare i link Hub Context prima che `createNewSession` abbia creato la sessione canonica. Il fix deve usare l'ID reale restituito dalla creazione senza indebolire gli invarianti del graph e senza anticipare il redesign Composer. GPT-5.5 / medium / FAST.
- `personalhub-context-composer-redesign.md` viene subito dopo e sostituisce la UI Hub Context v29 embedded/nested in Timer con una sezione top-level `Composer`: ripristina il New Session originale, usa geolocalizzazione e tempo come anchor automatici/editabili, mostra solo pochi suggerimenti ad alta probabilità, impara deterministicamente dalle co-occorrenze storiche e rileva automaticamente transazioni/intake/WordSession dal tempo selezionato. GPT-5.6 Sol / medium / STRICT.
- `personalhub-database-schema-upgrade-safety.md` viene dopo i task Hub Context perché consolida lo schema risultante e rende sicuri tutti gli aggiornamenti successivi: ogni vecchia versione supportata deve avere una catena di migrazione completa, il primo avvio del nuovo APK deve validare/migrare senza perdita dati e un futuro bump dello schema deve fallire nei test se manca una migrazione. GPT-5.6 Sol / medium / STRICT.
- People, widget Timer e tag picker restano correttivi localizzati e indipendenti e vengono eseguiti dopo il consolidamento Hub Context e DB.
- `personalhub-timer-session-tag-picker-ux.md` mantiene i tag selezionati come chip/card ben distinguibili e rende sempre disponibile la creazione del nome digitato quando non esiste già esattamente, anche se la ricerca mostra match più lunghi come `shopping` per `shop`.
- `personalhub-timer-legacy-runtime-cleanup.md` accorpa i residui del vecchio MultiTimeTracker su versione/AutoConsistency e first-run backup. Resta separato dal task Timer Alerts perché non deve riaprire il comportamento in-app appena consolidato.
- `personalhub-places-visit-history-checkin.md` usa ormai la semantica definitiva delle visite: accorpa overlap disambiguation, check-in storico manuale e “Dov'ero?” sullo stesso modello/query canonico senza reintrodurre una seconda fonte per le visite Timer-backed.
- `personalhub-places-sorting-map-navigation.md` resta separato perché è principalmente lista/mappa/query UI sulle metriche canoniche finali. `personalhub-places-geofence-alerts.md` resta separato perché coinvolge background location/notification e non deve riusare il vecchio Timer Alert system-notification path appena rimosso; può riusare solo infrastruttura Android realmente condivisa e ancora valida.
- `personalhub-autoexport-status-indicator.md` resta una feature UI localizzata. `personalhub-global-screen-version-footer.md` uniforma poi il dettaglio visivo della versione host su tutte le schermate. `personalhub-dark-theme.md` viene dopo la UI definitiva dei moduli.
- `personalhub-global-audit-foundation-safe-undo.md` accorpa modello/cattura semantica e undo compensativo conflict-safe perché la progettazione delle snapshot e della reversibilità deve servire direttamente l'inverso sicuro. La UI del registro resta separata e viene costruita solo sul backend definitivo.

## Disciplina globale

Ogni prompt deve restare self-contained e verificare esplicitamente eventuali prerequisiti; fuori da un blocco continuo non deve assumere una chat precedente. Per i task PersonalHub, il bootstrap specializzato autorevole è `MegaVault/ai/personalhubdoc.md`; il protocollo globale va letto solo nei casi di fallback esplicitamente previsti da quel file. Nei blocchi continui esplicitamente marcati, le fasi successive possono riusare esclusivamente il contesto verificato nelle fasi precedenti della stessa sessione, senza rilanciare bootstrap/esplorazione equivalenti.

Quando un prompt modifica PersonalHub, deve catturare la versione iniziale una sola volta e fissare per quel goal `target = base + 1`. Per una continuous campaign l'intero blocco è un unico goal di versionamento: il target viene fissato alla prima fase e riusato fino alla fine. Retry, rebuild, test o fasi successive dello stesso goal non possono incrementarlo di nuovo.

**Ordine solo numerico in roadmap:** l'ordine canonico è esclusivamente la posizione `1.`, `2.`, `3.`, ... in questa lista. I filename/titoli dei prompt devono essere semantici e non devono contenere prefissi o suffissi numerici/alfanumerici d'ordine. Inserire, rimuovere o riordinare un task richiede solo di rinumerare consecutivamente la lista; non si rinominano i file per la posizione. `PROMPT_ID` resta consentito perché è un identificatore casuale, non un indicatore d'ordine.

**Pre-localizzazione obbligatoria:** ogni prompt pendente deve indicare un set iniziale di file/classi reali verificati sullo stato corrente del repository target, sufficiente a iniziare il task senza scansione generale. Se un task precedente ha rinominato/spostato un file indicato, il prompt può autorizzare una singola ricerca mirata per il simbolo/classe noto. La disciplina operativa dettagliata su esplorazione, batching, tool call, retry, device QA, test, Git e stop resta definita dal bootstrap MegaVault governante e non va duplicata nei prompt.

Le fasi successive non devono riaprire l'architettura delle fasi precedenti salvo che un acceptance check dimostri una regressione o un prerequisito mancante.
