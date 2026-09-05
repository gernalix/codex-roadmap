# Codex Roadmap

Ordine consigliato di esecuzione, ricalcolato sull'audit statico di `PersonalHub/main` del 2026-09-05. Un task Codex alla volta sullo stesso progetto.

Stato già acquisito e da NON reimplementare nei task futuri: database PH unificato; Settings/Database & Backup integrati; sync Datasette local-first; Places API key/address suggestions; shortcut pinnabili e percorso diretto ai moduli; protezione dell'app reale dai benchmark/test distruttivi; auto-export SAF generation-based con WorkManager/recovery/error state; Soldi integrato con account, saldi, prodotto canonico e Git exchange.

Correzioni emerse dall'audit e NON ancora acquisite: il recovery import ha un marker non atomico; le FK Places↔Soldi non sono integrate nel flusso di cancellazione; Soldi usa `included` anche per filtrare lo storico e perde draft su recreation; il call overlay People ha deep-link/race/log PII; il widget Timer può dichiarare successo dopo write fallita; Timer usa version/gating legacy e first-run backup proprio; gli alert Timer non sono ripristinati autonomamente dopo reboot/update; `HubAutoExport.start()` mantiene ancora un poll permanente ogni 2 secondi. Il dettaglio è in `audits/2026-09-05-personalhub-main-audit.md`.

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
10. `prompts/04-personalhub-cross-module-shared-entities.md`
11. `prompts/06-personalhub-places-overlap-disambiguation.md`
12. `prompts/07-personalhub-places-manual-checkin.md`
13. `prompts/08-personalhub-places-where-was-i.md`
14. `prompts/09c-personalhub-places-geofence-alerts.md`
15. `prompts/09b-personalhub-substances-v2-rebuild.md`
16. `prompts/10a-personalhub-autoexport-status-indicator.md`
17. `prompts/10b-personalhub-dark-theme.md`
18. `prompts/11-personalhub-global-activity-audit-undo.md`

## Dipendenze / motivazione dell'ordine

- `03a` e `03b` vengono prima di qualsiasi nuova migrazione/relazione: rendono robusto il recovery e stabiliscono il comportamento delle entità canoniche già referenziate da FK.
- `03c`–`03g` chiudono regressioni concrete e debito legacy a costo contenuto prima di ampliare l'architettura.
- `09a` separa il repair degli alert Timer dalla nuova feature geofence Places; il vecchio prompt 09 accorpava due sottosistemi Android distinti.
- `03h` rimuove/riduce il poll idle solo dopo aver verificato che export e sync dispongano di trigger durevoli/event-driven equivalenti.
- `04` resta il principale task architetturale cross-module, ma viene eseguito solo dopo le correzioni di integrità sopra; essendo una migrazione DB usa MegaVault STRICT.
- `06` sfrutta un flusso `Ambiguous` già esistente: deve correggere la policy, non ricostruire il check-in UI da zero.
- `07` precede `08` perché le visite manuali diventano automaticamente una fonte utile per “Dov'ero?”.
- `09c` implementa solo gli alert geofence Places dopo che il pattern alert Timer è stato stabilizzato da `09a`.
- `09b` resta il rebuild Substances derivato dal suo audit separato; è mantenuto fuori dai finding interni di questo audit, ma deve precedere theme e registro audit globale perché ridefinisce write-path/UI/notifiche del modulo.
- Il vecchio prompt 10 è diviso: l'indicatore auto-export (`10a`) è localizzato; il dark theme (`10b`) è realmente cross-module e viene eseguito dopo il fix lifecycle Soldi e dopo Substances v2.
- Il registro globale `11` resta ultimo: deve intercettare i write-path finali di tutti i moduli e non va reintegrato dopo modifiche strutturali immediatamente successive.

I task devono preservare le garanzie già verificate, evitare esplorazione generale quando i file iniziali sono indicati, usare test mirati e fermarsi immediatamente quando gli acceptance criteria sono provati.
