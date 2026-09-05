# Codex Roadmap

[[README|README]] · [[spiegazioni|Spiegazioni]]

Ordine consigliato di esecuzione, riesaminato end-to-end sullo stato corrente di `PersonalHub/main` e sull'audit statico del 2026-09-05. Eseguire **un solo task Codex alla volta** sullo stesso progetto secondo il workflow del README.

Stato già acquisito e da NON reimplementare nei task futuri: database PH unificato; Settings/Database & Backup integrati; sync Datasette local-first; Places API key/address suggestions; shortcut pinnabili e percorso diretto ai moduli; protezione dell'app reale dai benchmark/test distruttivi; auto-export SAF generation-based con WorkManager/recovery/error state; hardening del Database Vault con import marker atomico/fail-safe e rollback SAF verificato; Soldi integrato con account, saldi, prodotto canonico e Git exchange; policy delete/FK Places↔Soldi corretta.

Finding tecnici ancora pendenti dall'audit: People call-overlay deep-link/race/PII; Timer widget write-result; residui runtime/backup legacy Timer; ripristino alert Timer dopo reboot/update; polling permanente 2 s in `HubAutoExport.start()`; capsulizzazione architetturale incompleta nel data layer. Dettagli: `audits/2026-09-05-personalhub-main-audit.md` e verifica architetturale corrente.

## Ordine pendente

1. [[prompts/personalhub-remove-idle-polling|personalhub-remove-idle-polling]]
2. [[prompts/personalhub-substances-core-integrity-command-stock-archive|personalhub-substances-core-integrity-command-stock-archive]]
3. [[prompts/personalhub-substances-therapy-intake-interactions-notifications|personalhub-substances-therapy-intake-interactions-notifications]]
4. [[prompts/personalhub-substances-prescriptions-stock-crossmodule|personalhub-substances-prescriptions-stock-crossmodule]]
5. [[prompts/personalhub-substances-history-data-integration|personalhub-substances-history-data-integration]]
6. [[prompts/personalhub-substances-ui-navigation-final-qa|personalhub-substances-ui-navigation-final-qa]]
7. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]]
8. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]]
9. [[prompts/personalhub-timer-widget-write-result|personalhub-timer-widget-write-result]]
10. [[prompts/personalhub-timer-legacy-runtime-cleanup|personalhub-timer-legacy-runtime-cleanup]]
11. [[prompts/personalhub-complete-module-capsulization|personalhub-complete-module-capsulization]]
12. [[prompts/personalhub-cross-module-entity-linking|personalhub-cross-module-entity-linking]]
13. [[prompts/personalhub-places-visit-history-checkin|personalhub-places-visit-history-checkin]]
14. [[prompts/personalhub-places-sorting-map-navigation|personalhub-places-sorting-map-navigation]]
15. [[prompts/personalhub-places-geofence-alerts|personalhub-places-geofence-alerts]]
16. [[prompts/personalhub-autoexport-status-indicator|personalhub-autoexport-status-indicator]]
17. [[prompts/personalhub-dark-theme|personalhub-dark-theme]]
18. [[prompts/personalhub-global-audit-foundation-safe-undo|personalhub-global-audit-foundation-safe-undo]]
19. [[prompts/personalhub-global-audit-register-ui|personalhub-global-audit-register-ui]]

## Dipendenze / motivazione dell'ordine

- `personalhub-remove-idle-polling.md` resta separato: rimuove/riduce il poll idle solo dopo aver verificato trigger durevoli/event-driven equivalenti per export e sync.
- Substances viene poi completato in cinque fasi consecutive, così nessun altro task interrompe il lavoro sul modulo: integrità/command-stock-archive → terapia/intake/interazioni/countdown/notifiche → prescrizioni/scorte/People/Soldi → History/performance + integrazione col DB globale → UI/navigation/QA finale. Solo la fase finale esegue il passaggio end-to-end su Pixel e TCL.
- `personalhub-substances-core-integrity-command-stock-archive.md` crea prima le invarianti dati condivise, compresa l'unicità del nome/pulsante sostanza, su cui si appoggiano tutte le fasi successive.
- `personalhub-substances-therapy-intake-interactions-notifications.md` mantiene scheduling, intake, interazioni, countdown e notifiche nello stesso task perché condividono la stessa macchina di stato temporale. Le prescrizioni sono separate per evitare un mega-task che includa anche People e Soldi.
- `personalhub-substances-prescriptions-stock-crossmodule.md` ricostruisce la tab Prescriptions su un modello 1 entry = 1 prescrizione, collegandola alla sostanza canonica, al medico People e alla transazione Soldi selezionata; condivide con l'intake solo il minimo contratto necessario per decrementare/ripristinare le dosi residue.
- `personalhub-substances-history-data-integration.md` viene dopo che intake e prescrizioni hanno identità definitive; rende History modificabile/cancellabile, stabile e scalabile e rimuove i vecchi percorsi DB autorevoli del modulo.
- `personalhub-substances-ui-navigation-final-qa.md` chiude il modulo sopra i contratti definitivi: pulsanti che restano visibili dopo il tap, prossimo orario in piccolo, countdown interazioni, FAB contestuale e verifica finale sui due device.
- `personalhub-database-schema-upgrade-safety.md` viene subito dopo il blocco Substances perché consolida lo schema risultante e rende sicuri tutti gli aggiornamenti successivi: ogni vecchia versione supportata deve avere una catena di migrazione completa, il primo avvio del nuovo APK deve validare/migrare senza perdita dati e un futuro bump dello schema deve fallire nei test se manca una migrazione. GPT-5.6 Sol / medium / STRICT.
- People e il widget Timer restano correttivi localizzati e indipendenti, quindi separati e vengono eseguiti dopo il blocco Substances e l'hardening globale degli upgrade DB.
- `personalhub-timer-legacy-runtime-cleanup.md` accorpa i due residui dello stesso sottosistema legacy Timer: versione/AutoConsistency e vecchio first-run backup. Condividono bootstrap e contesto runtime e possono essere verificati insieme senza riaprire gli alert già completati.
- `personalhub-complete-module-capsulization.md` resta autonomo: è il refactor architetturale trasversale più ampio, mantiene il singolo `personalhub.db`, sposta persistence feature-owned dietro contratti espliciti e restringe Room. GPT-5.6 Sol / medium / STRICT.
- `personalhub-cross-module-entity-linking.md` accorpa fondazione DB/query e UX People ↔ Timer ↔ Places perché sono due metà della stessa feature e condividono schema, repository e test end-to-end. Un Timer interval collegato a un Place è la stessa fonte temporale usata da Places history/stats, senza doppio conteggio; i selector Timer consentono inline `+ Nuova persona` / `+ Nuovo luogo`, con nuovo Place a radius predefinito 75 m. GPT-5.6 Sol / medium / STRICT.
- `personalhub-places-visit-history-checkin.md` accorpa overlap disambiguation, check-in storico manuale e “Dov'ero?” perché lavorano sullo stesso modello/query di visita canonica. Prima rende affidabile l'identità della visita, poi completa la history e infine la interroga.
- `personalhub-places-sorting-map-navigation.md` resta separato perché è principalmente lista/mappa/query UI sulle metriche canoniche finali. `personalhub-places-geofence-alerts.md` resta separato perché coinvolge background location/notification; può riusare solo pattern Android già dimostrati dal task Timer Alerts, senza condividere il dominio.
- `personalhub-autoexport-status-indicator.md` resta una feature UI localizzata; `personalhub-dark-theme.md` viene dopo la UI Substances definitiva.
- `personalhub-global-audit-foundation-safe-undo.md` accorpa modello/cattura semantica e undo compensativo conflict-safe perché la progettazione delle snapshot e della reversibilità deve servire direttamente l'inverso sicuro. La UI del registro resta separata e viene costruita solo sul backend definitivo.

## Disciplina globale

Ogni prompt deve restare self-contained per una sessione Codex nuova, verificare esplicitamente eventuali prerequisiti invece di assumere una chat precedente, rispettare `AGENTS.md` e il protocollo MegaVault autorevole, e incrementare `version.txt` secondo la regola di progetto quando modifica PersonalHub.

**Ordine solo numerico in roadmap:** l'ordine canonico è esclusivamente la posizione `1.`, `2.`, `3.`, ... in questa lista. I filename/titoli dei prompt devono essere semantici e non devono contenere prefissi o suffissi numerici/alfanumerici d'ordine. Inserire, rimuovere o riordinare un task richiede solo di rinumerare consecutivamente la lista; non si rinominano i file per la posizione. `PROMPT_ID` resta consentito perché è un identificatore casuale, non un indicatore d'ordine.

**Pre-localizzazione obbligatoria:** ogni prompt pendente deve indicare un set iniziale di file/classi reali verificati sullo stato di `PersonalHub/main`, sufficiente a iniziare il task senza scansione generale del repository. Se un task precedente ha rinominato/spostato un file indicato, il prompt può autorizzare una singola ricerca mirata per il simbolo/classe noto. Questa è una convenzione specifica della roadmap; la disciplina operativa globale su esplorazione, batching, tool call, retry, test, Git e stop è definita esclusivamente da `MegaVault/ai/MEGAVAULT_PROTOCOL.md` e non va duplicata qui o nei prompt.

Le fasi successive non devono riaprire l'architettura delle fasi precedenti salvo che un acceptance check dimostri una regressione o un prerequisito mancante.
