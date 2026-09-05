# Codex Roadmap

[[README|README]] · [[spiegazioni|Spiegazioni]]

Ordine consigliato di esecuzione, riesaminato end-to-end sullo stato corrente di `PersonalHub/main`, sul dump Codex del 2026-09-05 e sull'audit statico dello stesso giorno. Eseguire **un solo task Codex alla volta** sullo stesso progetto secondo il workflow del README.

Stato già acquisito e da NON reimplementare nei task futuri: database PH unificato; Settings/Database & Backup integrati; sync Datasette local-first; Places API key/address suggestions; shortcut pinnabili e percorso diretto ai moduli; protezione dell'app reale dai benchmark/test distruttivi; auto-export SAF generation-based con WorkManager/recovery/error state; hardening del Database Vault con import marker atomico/fail-safe e rollback SAF verificato; Soldi integrato con account, saldi, prodotto canonico e Git exchange; policy delete/FK Places↔Soldi corretta; Timer Alerts passati su `PersonalHub/main` a prompt in-app centrati e immediati con link/deep link cliccabili.

Finding tecnici ancora pendenti: Soldi usa ancora `FinanceAccount.included` per nascondere transazioni invece di limitarlo ai totali; People call-overlay deep-link/race/PII; Timer widget write-result; residui runtime/backup legacy Timer; polling permanente 2 s in `HubAutoExport.start()`; capsulizzazione architetturale incompleta nel data layer. Dettagli storici: `audits/2026-09-05-personalhub-main-audit.md`.

## Ordine pendente

La raccomandazione `Recommended model` + `Reasoning` già contenuta in ciascun prompt resta **invariata**. Accanto a ogni voce qui sotto è aggiunta una seconda scelta, `nuova policy 5.6`, da usare come alternativa sperimentale quando vuoi verificare se un modello più capace riduce errori, retry, tool-call e consumo quota complessivo.

1. [[prompts/personalhub-soldi-account-inclusion-filter-semantics|personalhub-soldi-account-inclusion-filter-semantics]] — **nuova policy 5.6: GPT-5.6 Terra / low**
2. [[prompts/personalhub-remove-idle-polling|personalhub-remove-idle-polling]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
3. [[prompts/personalhub-substances-core-integrity-command-stock-archive|personalhub-substances-core-integrity-command-stock-archive]] — **nuova policy 5.6: GPT-5.6 Sol / high**
4. [[prompts/personalhub-substances-therapy-intake-interactions-notifications|personalhub-substances-therapy-intake-interactions-notifications]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
5. [[prompts/personalhub-substances-prescriptions-stock-crossmodule|personalhub-substances-prescriptions-stock-crossmodule]] — **nuova policy 5.6: GPT-5.6 Sol / high**
6. [[prompts/personalhub-substances-history-data-integration|personalhub-substances-history-data-integration]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
7. [[prompts/personalhub-substances-ui-navigation-final-qa|personalhub-substances-ui-navigation-final-qa]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
8. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]] — **nuova policy 5.6: GPT-5.6 Sol / high**
9. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
10. [[prompts/personalhub-timer-widget-write-result|personalhub-timer-widget-write-result]] — **nuova policy 5.6: GPT-5.6 Terra / low**
11. [[prompts/personalhub-timer-session-tag-picker-ux|personalhub-timer-session-tag-picker-ux]] — **nuova policy 5.6: GPT-5.6 Terra / low**
12. [[prompts/personalhub-timer-legacy-runtime-cleanup|personalhub-timer-legacy-runtime-cleanup]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
13. [[prompts/personalhub-complete-module-capsulization|personalhub-complete-module-capsulization]] — **nuova policy 5.6: GPT-5.6 Sol / high**
14. [[prompts/personalhub-cross-module-entity-linking|personalhub-cross-module-entity-linking]] — **nuova policy 5.6: GPT-5.6 Sol / high**
15. [[prompts/personalhub-places-visit-history-checkin|personalhub-places-visit-history-checkin]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
16. [[prompts/personalhub-places-sorting-map-navigation|personalhub-places-sorting-map-navigation]] — **nuova policy 5.6: GPT-5.6 Terra / low**
17. [[prompts/personalhub-places-geofence-alerts|personalhub-places-geofence-alerts]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
18. [[prompts/personalhub-autoexport-status-indicator|personalhub-autoexport-status-indicator]] — **nuova policy 5.6: GPT-5.6 Terra / low**
19. [[prompts/personalhub-global-screen-version-footer|personalhub-global-screen-version-footer]] — **nuova policy 5.6: GPT-5.6 Terra / low**
20. [[prompts/personalhub-dark-theme|personalhub-dark-theme]] — **nuova policy 5.6: GPT-5.6 Sol / medium**
21. [[prompts/personalhub-global-audit-foundation-safe-undo|personalhub-global-audit-foundation-safe-undo]] — **nuova policy 5.6: GPT-5.6 Sol / high**
22. [[prompts/personalhub-global-audit-register-ui|personalhub-global-audit-register-ui]] — **nuova policy 5.6: GPT-5.6 Terra / low**

## Dipendenze / motivazione dell'ordine

- `personalhub-soldi-account-inclusion-filter-semantics.md` ripristina un correttivo P2 dell'audit che era scomparso dalla roadmap durante il consolidamento: escludere un conto deve toglierlo solo dal totale, non dalla cronologia delle transazioni. È localizzato e indipendente. GPT-5.5 / low / FAST.
- `personalhub-remove-idle-polling.md` resta separato: rimuove/riduce il poll idle solo dopo aver verificato trigger durevoli/event-driven equivalenti per export e sync.
- Substances viene poi completato in cinque fasi consecutive, così nessun altro task interrompe il lavoro sul modulo: integrità/command-stock-archive → terapia/intake/interazioni/countdown/notifiche → prescrizioni/scorte/People/Soldi → History/performance + integrazione col DB globale → UI/navigation/QA finale. Solo la fase finale esegue il passaggio end-to-end su Pixel e TCL.
- `personalhub-substances-core-integrity-command-stock-archive.md` crea prima le invarianti dati condivise, compresa l'unicità del nome/pulsante sostanza, su cui si appoggiano tutte le fasi successive.
- `personalhub-substances-therapy-intake-interactions-notifications.md` mantiene scheduling, intake, interazioni, countdown e notifiche nello stesso task perché condividono la stessa macchina di stato temporale. Le prescrizioni sono separate per evitare un mega-task che includa anche People e Soldi.
- `personalhub-substances-prescriptions-stock-crossmodule.md` ricostruisce la tab Prescriptions su un modello 1 entry = 1 prescrizione, collegandola alla sostanza canonica, al medico People e alla transazione Soldi selezionata; condivide con l'intake solo il minimo contratto necessario per decrementare/ripristinare le dosi residue.
- `personalhub-substances-history-data-integration.md` viene dopo che intake e prescrizioni hanno identità definitive; rende History modificabile/cancellabile, stabile e scalabile e rimuove i vecchi percorsi DB autorevoli del modulo.
- `personalhub-substances-ui-navigation-final-qa.md` chiude il modulo sopra i contratti definitivi: pulsanti che restano visibili dopo il tap, prossimo orario in piccolo, countdown interazioni, FAB contestuale e verifica finale sui due device.
- `personalhub-database-schema-upgrade-safety.md` viene subito dopo il blocco Substances perché consolida lo schema risultante e rende sicuri tutti gli aggiornamenti successivi: ogni vecchia versione supportata deve avere una catena di migrazione completa, il primo avvio del nuovo APK deve validare/migrare senza perdita dati e un futuro bump dello schema deve fallire nei test se manca una migrazione. GPT-5.6 Sol / medium / STRICT.
- People e il widget Timer restano correttivi localizzati e indipendenti, quindi separati e vengono eseguiti dopo il blocco Substances e l'hardening globale degli upgrade DB.
- `personalhub-timer-session-tag-picker-ux.md` viene subito dopo il widget perché è un correttivo UI Timer localizzato: mantiene i tag selezionati come chip/card ben distinguibili e rende sempre disponibile la creazione del nome digitato quando non esiste già esattamente, anche se la ricerca mostra match più lunghi come `shopping` per `shop`.
- `personalhub-timer-legacy-runtime-cleanup.md` accorpa i residui del vecchio MultiTimeTracker su versione/AutoConsistency e first-run backup. Resta separato dal task Timer Alerts perché non deve riaprire il comportamento in-app appena consolidato.
- `personalhub-complete-module-capsulization.md` resta autonomo: è il refactor architetturale trasversale più ampio, mantiene il singolo `personalhub.db`, sposta persistence feature-owned dietro contratti espliciti e restringe Room. GPT-5.6 Sol / medium / STRICT.
- `personalhub-cross-module-entity-linking.md` accorpa fondazione DB/query e UX People ↔ Timer ↔ Places perché sono due metà della stessa feature e condividono schema, repository e test end-to-end. Un Timer interval collegato a un Place è la stessa fonte temporale usata da Places history/stats, senza doppio conteggio; i selector Timer consentono inline `+ Nuova persona` / `+ Nuovo luogo`, con nuovo Place a radius predefinito 75 m. GPT-5.6 Sol / medium / STRICT.
- `personalhub-places-visit-history-checkin.md` accorpa overlap disambiguation, check-in storico manuale e “Dov'ero?” perché lavorano sullo stesso modello/query di visita canonica. Prima rende affidabile l'identità della visita, poi completa la history e infine la interroga.
- `personalhub-places-sorting-map-navigation.md` resta separato perché è principalmente lista/mappa/query UI sulle metriche canoniche finali. `personalhub-places-geofence-alerts.md` resta separato perché coinvolge background location/notification e non deve riusare il vecchio Timer Alert system-notification path appena rimosso; può riusare solo infrastruttura Android realmente condivisa e ancora valida.
- `personalhub-autoexport-status-indicator.md` resta una feature UI localizzata. `personalhub-global-screen-version-footer.md` uniforma poi il dettaglio visivo della versione host su tutte le schermate. `personalhub-dark-theme.md` viene dopo la UI definitiva dei moduli.
- `personalhub-global-audit-foundation-safe-undo.md` accorpa modello/cattura semantica e undo compensativo conflict-safe perché la progettazione delle snapshot e della reversibilità deve servire direttamente l'inverso sicuro. La UI del registro resta separata e viene costruita solo sul backend definitivo.

## Disciplina globale

Ogni prompt deve restare self-contained per una sessione Codex nuova, verificare esplicitamente eventuali prerequisiti invece di assumere una chat precedente e rispettare `AGENTS.md`. Per i task PersonalHub, il bootstrap specializzato autorevole è `MegaVault/ai/personalhubdoc.md`; il protocollo globale va letto solo nei casi di fallback esplicitamente previsti da quel file.

Quando un prompt modifica PersonalHub, deve catturare la versione iniziale una sola volta e fissare per quel goal `target = base + 1`. Retry, rebuild, test o seconde patch dello stesso goal non possono incrementarla di nuovo.

**Ordine solo numerico in roadmap:** l'ordine canonico è esclusivamente la posizione `1.`, `2.`, `3.`, ... in questa lista. I filename/titoli dei prompt devono essere semantici e non devono contenere prefissi o suffissi numerici/alfanumerici d'ordine. Inserire, rimuovere o riordinare un task richiede solo di rinumerare consecutivamente la lista; non si rinominano i file per la posizione. `PROMPT_ID` resta consentito perché è un identificatore casuale, non un indicatore d'ordine.

**Pre-localizzazione obbligatoria:** ogni prompt pendente deve indicare un set iniziale di file/classi reali verificati sullo stato corrente del repository target, sufficiente a iniziare il task senza scansione generale. Se un task precedente ha rinominato/spostato un file indicato, il prompt può autorizzare una singola ricerca mirata per il simbolo/classe noto. La disciplina operativa dettagliata su esplorazione, batching, tool call, retry, device QA, test, Git e stop resta definita dal bootstrap MegaVault governante e non va duplicata nei prompt.

Le fasi successive non devono riaprire l'architettura delle fasi precedenti salvo che un acceptance check dimostri una regressione o un prerequisito mancante.
