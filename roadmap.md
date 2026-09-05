# Codex Roadmap

Ordine consigliato di esecuzione, riesaminato end-to-end sullo stato corrente di `PersonalHub/main` e sull'audit statico del 2026-09-05. Eseguire **un solo task Codex alla volta** sullo stesso progetto secondo il workflow del README.

Stato già acquisito e da NON reimplementare nei task futuri: database PH unificato; Settings/Database & Backup integrati; sync Datasette local-first; Places API key/address suggestions; shortcut pinnabili e percorso diretto ai moduli; protezione dell'app reale dai benchmark/test distruttivi; auto-export SAF generation-based con WorkManager/recovery/error state; Soldi integrato con account, saldi, prodotto canonico e Git exchange.

Finding tecnici ancora pendenti dall'audit: recovery import marker non atomico; policy delete/FK Places↔Soldi; filtro/lifecycle Soldi; People call-overlay deep-link/race/PII; Timer widget write-result; Timer version/AutoConsistency legacy; first-run backup Timer legacy; ripristino alert Timer dopo reboot/update; polling permanente 2 s in `HubAutoExport.start()`; capsulizzazione architetturale incompleta nel data layer (`core:database` conosce/ospita dettagli persistence concreti dei feature e Room è esposto troppo ampiamente). Dettagli: `audits/2026-09-05-personalhub-main-audit.md` e verifica architetturale corrente.

## Ordine pendente

1. `prompts/personalhub-database-vault-transfer-hardening.md`
2. `prompts/personalhub-canonical-entity-delete-fk-policy.md`
3. `prompts/personalhub-soldi-account-filter-lifecycle.md`
4. `prompts/personalhub-people-call-overlay-hardening.md`
5. `prompts/personalhub-timer-widget-write-result.md`
6. `prompts/personalhub-timer-version-autoconsistency.md`
7. `prompts/personalhub-timer-remove-legacy-first-run-backup.md`
8. `prompts/personalhub-timer-alerts.md`
9. `prompts/personalhub-remove-idle-polling.md`
10. `prompts/personalhub-complete-module-capsulization.md`
11. `prompts/personalhub-cross-module-shared-entities.md`
12. `prompts/personalhub-cross-module-linked-entities-ui.md`
13. `prompts/personalhub-places-overlap-disambiguation.md`
14. `prompts/personalhub-places-manual-checkin.md`
15. `prompts/personalhub-places-where-was-i.md`
16. `prompts/personalhub-places-sorting-map-navigation.md`
17. `prompts/personalhub-places-geofence-alerts.md`
18. `prompts/personalhub-substances-core-integrity-command-stock-archive.md`
19. `prompts/personalhub-substances-scheduling-intake-interactions-macros.md`
20. `prompts/personalhub-substances-prescriptions-notifications.md`
21. `prompts/personalhub-substances-history-performance.md`
22. `prompts/personalhub-substances-global-import-export-cleanup.md`
23. `prompts/personalhub-substances-ui-navigation-final-qa.md`
24. `prompts/personalhub-autoexport-status-indicator.md`
25. `prompts/personalhub-dark-theme.md`
26. `prompts/personalhub-global-audit-foundation.md`
27. `prompts/personalhub-global-audit-safe-undo.md`
28. `prompts/personalhub-global-audit-register-ui.md`

## Dipendenze / motivazione dell'ordine

- `personalhub-database-vault-transfer-hardening.md` e `personalhub-canonical-entity-delete-fk-policy.md` precedono nuove migrazioni/relazioni: prima si mette in sicurezza recovery e comportamento delle entità canoniche già referenziate da FK.
- I correttivi Soldi, People e Timer immediatamente successivi chiudono regressioni concrete e debito legacy localizzato prima di ampliare l'architettura. Restano separati perché riguardano failure mode indipendenti e hanno acceptance/test diversi.
- `personalhub-timer-alerts.md` stabilizza il sottosistema alert Timer e il restore dopo reboot/update prima di introdurre nuovi alert geofence in Places.
- `personalhub-remove-idle-polling.md` rimuove/riduce il poll idle solo dopo aver verificato trigger durevoli/event-driven equivalenti per export e sync; non è un secondo audit dell'auto-export.
- `personalhub-complete-module-capsulization.md` viene dopo la stabilizzazione DB/export/sync e prima di nuove relazioni cross-module: completa i confini di capsulizzazione mantenendo il singolo `personalhub.db`, spostando i dettagli persistence feature-owned dietro contratti espliciti e restringendo l'esposizione di Room senza modificare inutilmente lo schema. Usa GPT-5.6 Sol / medium / STRICT perché è un refactor architetturale trasversale e deve lasciare invariati dati e comportamento.
- `personalhub-cross-module-shared-entities.md` è la fase architetturale cross-module: schema, FK/delete semantics e repository/query contracts. Oltre ai link People/Places, stabilisce che un Timer interval collegato a un Place possa essere la stessa fonte temporale usata da Places history/stats, senza una seconda visita indipendentemente autorevole e senza doppio conteggio. Usa GPT-5.6 Sol / medium / STRICT perché modifica il DB canonico.
- `personalhub-cross-module-linked-entities-ui.md` è la fase user-facing: rende selezionabili/visibili/navigabili le relazioni People ↔ Timer ↔ Places e aggiunge inline creation dai selector Timer (`+ Nuova persona`, `+ Nuovo luogo`). Un luogo creato da quel flusso nasce con radius canonico predefinito di **75 m**. Salvare un Timer interval con Place deve renderlo anche una visita Places secondo la single-source semantics del task architetturale, senza duplicare il fatto temporale.
- La catena `personalhub-places-overlap-disambiguation.md` → `personalhub-places-manual-checkin.md` → `personalhub-places-where-was-i.md` resta coerente: correggere la disambiguazione, aggiungere visite manuali, poi usare tutta la history per “Dov'ero?”.
- `personalhub-places-sorting-map-navigation.md` viene dopo la stabilizzazione della history perché ordina Places usando distanza attuale, ultima visita, tempo totale e numero visite (ASC/DESC) e usa le metriche canoniche finali, incluse eventuali visite Timer-backed una sola volta. Nello stesso task la mappa globale viene centrata sulla posizione attuale quando disponibile e un marker individuale apre la scheda canonica del Place.
- `personalhub-places-geofence-alerts.md` aggiunge solo geofence alerts Places dopo il pattern alert Timer; è GPT-5.5 / medium / STANDARD perché non richiede un nuovo framework di automazione.
- Le sei fasi Substances seguono le dipendenze reali: integrità/command layer → scheduling/intake/interazioni/macro → prescrizioni/notifiche → History/performance → import/export globale → UI/navigation/QA finale. Solo la fase UI/QA esegue il passaggio end-to-end su Pixel e TCL.
- `personalhub-autoexport-status-indicator.md` resta una feature UI localizzata e `personalhub-dark-theme.md` viene dopo la UI Substances definitiva, così il dark theme copre le superfici finali invece di essere rifatto.
- Le tre fasi del Registro attività restano in fondo: fondazione/cattura semantica → undo compensativo conflict-safe → home card/register/filter UI. Devono osservare i write-path e le impostazioni definitive dei moduli precedenti.

## Disciplina globale

Ogni prompt deve restare self-contained per una sessione Codex nuova, verificare esplicitamente eventuali prerequisiti invece di assumere una chat precedente, rispettare `AGENTS.md`/MegaVault e incrementare `version.txt` secondo la regola di progetto quando modifica PersonalHub.

**Ordine solo numerico in roadmap:** l'ordine canonico è esclusivamente la posizione `1.`, `2.`, `3.`, ... in questa lista. I filename/titoli dei prompt devono essere semantici e non devono contenere prefissi o suffissi numerici/alfanumerici d'ordine (`04-`, `04b-`, `09b1-`, `task-12-`, ecc.). Inserire, rimuovere o riordinare un task richiede solo di rinumerare consecutivamente la lista; non si rinominano i file per la posizione. Le dipendenze vanno citate con filename/titolo semantico o significato funzionale, mai con un codice d'ordine. `PROMPT_ID` resta consentito perché è un identificatore casuale, non un indicatore d'ordine.

**Pre-localizzazione obbligatoria:** ogni prompt pendente deve indicare un set iniziale di file/classi reali verificati sullo stato di `PersonalHub/main`, sufficiente a iniziare il task senza scansione generale del repository. Codex deve leggere quei file in batch e ampliare solo quando una dipendenza diretta o un test fallito fornisce nuova evidenza. Se un task precedente ha rinominato/spostato un file indicato, è ammessa una singola ricerca mirata per il simbolo/classe noto; non una scansione di directory/repository. I task futuri aggiunti alla roadmap devono seguire la stessa regola.

Ottimizzare il lavoro totale: niente esplorazione generale preventiva, batch di letture/search quando possibile, nessun retry identico senza nuova evidenza, test mirati prima di suite più ampie, nessun refactor/cleanup fuori scope e stop immediato dopo il PASS. Le fasi successive non devono riaprire l'architettura delle fasi precedenti salvo che un acceptance check dimostri una regressione o un prerequisito mancante.
