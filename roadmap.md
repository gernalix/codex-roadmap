# Codex Roadmap

Ordine consigliato di esecuzione, riesaminato end-to-end sullo stato corrente di `PersonalHub/main` e sull'audit statico del 2026-09-05. Eseguire **un solo task Codex alla volta** sullo stesso progetto secondo il workflow del README.

Stato già acquisito e da NON reimplementare nei task futuri: database PH unificato; Settings/Database & Backup integrati; sync Datasette local-first; Places API key/address suggestions; shortcut pinnabili e percorso diretto ai moduli; protezione dell'app reale dai benchmark/test distruttivi; auto-export SAF generation-based con WorkManager/recovery/error state; Soldi integrato con account, saldi, prodotto canonico e Git exchange.

Finding tecnici ancora pendenti dall'audit: recovery import marker non atomico; policy delete/FK Places↔Soldi; filtro/lifecycle Soldi; People call-overlay deep-link/race/PII; Timer widget write-result; Timer version/AutoConsistency legacy; first-run backup Timer legacy; ripristino alert Timer dopo reboot/update; polling permanente 2 s in `HubAutoExport.start()`; capsulizzazione architetturale incompleta nel data layer (`core:database` conosce/ospita dettagli persistence concreti dei feature e Room è esposto troppo ampiamente). Dettagli: `audits/2026-09-05-personalhub-main-audit.md` e verifica architetturale corrente.

## Ordine pendente

1. `prompts/03a-personalhub-database-vault-transfer-hardening.md`
2. `prompts/03b-personalhub-canonical-entity-delete-fk-policy.md`
3. `prompts/03c-personalhub-soldi-account-filter-lifecycle.md`
4. `prompts/03d-personalhub-people-call-overlay-hardening.md`
5. `prompts/03e-personalhub-timer-widget-write-result.md`
6. `prompts/03f-personalhub-timer-version-autoconsistency.md`
7. `prompts/03g-personalhub-timer-remove-legacy-first-run-backup.md`
8. `prompts/09a-personalhub-timer-alerts.md`
9. `prompts/03h-personalhub-remove-idle-polling.md`
10. `prompts/03i-personalhub-complete-module-capsulization.md`
11. `prompts/04-personalhub-cross-module-shared-entities.md`
12. `prompts/04b-personalhub-cross-module-linked-entities-ui.md`
13. `prompts/06-personalhub-places-overlap-disambiguation.md`
14. `prompts/07-personalhub-places-manual-checkin.md`
15. `prompts/08-personalhub-places-where-was-i.md`
16. `prompts/08b-personalhub-places-sorting-map-navigation.md`
17. `prompts/09c-personalhub-places-geofence-alerts.md`
18. `prompts/09b1-personalhub-substances-core-integrity-command-stock-archive.md`
19. `prompts/09b2-personalhub-substances-scheduling-intake-interactions-macros.md`
20. `prompts/09b3-personalhub-substances-prescriptions-notifications.md`
21. `prompts/09b4-personalhub-substances-history-performance.md`
22. `prompts/09b5-personalhub-substances-global-import-export-cleanup.md`
23. `prompts/09b6-personalhub-substances-ui-navigation-final-qa.md`
24. `prompts/10a-personalhub-autoexport-status-indicator.md`
25. `prompts/10b-personalhub-dark-theme.md`
26. `prompts/11a-personalhub-global-audit-foundation.md`
27. `prompts/11b-personalhub-global-audit-safe-undo.md`
28. `prompts/11c-personalhub-global-audit-register-ui.md`

## Dipendenze / motivazione dell'ordine

- `03a` e `03b` precedono nuove migrazioni/relazioni: prima si mette in sicurezza recovery e comportamento delle entità canoniche già referenziate da FK.
- `03c`–`03g` chiudono regressioni concrete e debito legacy localizzato prima di ampliare l'architettura. Sono mantenuti separati perché riguardano failure mode indipendenti e hanno acceptance/test diversi.
- `09a` stabilizza il sottosistema alert Timer e il restore dopo reboot/update prima di introdurre nuovi alert geofence in Places.
- `03h` rimuove/riduce il poll idle solo dopo aver verificato trigger durevoli/event-driven equivalenti per export e sync; non è un secondo audit dell'auto-export.
- `03i` viene dopo la stabilizzazione DB/export/sync e prima di nuove relazioni cross-module: completa i confini di capsulizzazione mantenendo il singolo `personalhub.db`, spostando i dettagli persistence feature-owned dietro contratti espliciti e restringendo l'esposizione di Room senza modificare inutilmente lo schema. Usa GPT-5.6 Sol / medium / STRICT perché è un refactor architetturale trasversale e deve lasciare invariati dati e comportamento.
- `04` è la **fase 1** cross-module: schema, FK/delete semantics e repository/query contracts. Oltre ai link People/Places, stabilisce che un Timer interval collegato a un Place possa essere la stessa fonte temporale usata da Places history/stats, senza una seconda visita indipendentemente autorevole e senza doppio conteggio. Usa GPT-5.6 Sol / medium / STRICT perché modifica il DB canonico.
- `04b` è la **fase 2 user-facing**: rende selezionabili/visibili/navigabili le relazioni People ↔ Timer ↔ Places e aggiunge inline creation dai selector Timer (`+ Nuova persona`, `+ Nuovo luogo`). Un luogo creato da quel flusso nasce con radius canonico predefinito di **75 m**. Salvare un Timer interval con Place deve renderlo anche una visita Places secondo la single-source semantics di `04`, senza duplicare il fatto temporale.
- `06 → 07 → 08` resta una catena coerente: correggere la disambiguazione, aggiungere visite manuali, poi usare tutta la history per “Dov'ero?”.
- `08b` viene dopo la stabilizzazione della history perché ordina Places usando distanza attuale, ultima visita, tempo totale e numero visite (ASC/DESC) e usa le metriche canoniche finali, incluse eventuali visite Timer-backed una sola volta. Nello stesso task la mappa globale viene centrata sulla posizione attuale quando disponibile e un marker individuale apre la scheda canonica del Place.
- `09c` aggiunge solo geofence alerts Places dopo il pattern alert Timer; è GPT-5.5 / medium / STANDARD perché non richiede un nuovo framework di automazione.
- Il vecchio mega-prompt `09b-personalhub-substances-v2-rebuild.md` è eliminato e sostituito da `09b1`–`09b6`. Le fasi seguono le dipendenze reali: integrità/command layer → scheduling/intake/interazioni/macro → prescrizioni/notifiche → History/performance → import/export globale → UI/navigation/QA finale. Solo l'ultima fase esegue il passaggio end-to-end su Pixel e TCL.
- `10a` resta una feature UI localizzata e `10b` viene dopo la UI Substances definitiva, così il dark theme copre le superfici finali invece di essere rifatto.
- Il vecchio mega-prompt `11-personalhub-global-activity-audit-undo.md` è eliminato e sostituito da tre fasi: `11a` cattura semantica/schema, `11b` undo compensativo conflict-safe, `11c` home card/register/filter UI. Restano in fondo perché devono osservare i write-path e le impostazioni definitive dei moduli precedenti.

## Disciplina globale

Ogni prompt deve restare self-contained per una sessione Codex nuova, verificare esplicitamente eventuali prerequisiti invece di assumere una chat precedente, rispettare `AGENTS.md`/MegaVault e incrementare `version.txt` secondo la regola di progetto quando modifica PersonalHub.

Ottimizzare il lavoro totale: niente esplorazione generale preventiva, batch di letture/search quando possibile, nessun retry identico senza nuova evidenza, test mirati prima di suite più ampie, nessun refactor/cleanup fuori scope e stop immediato dopo il PASS. Le fasi successive non devono riaprire l'architettura delle fasi precedenti salvo che un acceptance check dimostri una regressione o un prerequisito mancante.
