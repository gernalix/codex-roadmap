# Codex Roadmap

Ordine consigliato di esecuzione, ricalcolato sullo stato corrente di PersonalHub. Un task Codex alla volta sullo stesso progetto.

Stato già acquisito e quindi NON da duplicare nei task futuri: database PH unificato e migrazione verificata; settings/database-backup integrati; sync Datasette local-first; Places API key/address suggestions fix; shortcut pinnabili e percorso diretto ottimizzato; protezione app reale dai benchmark distruttivi; auto-export SAF generation-based durevole con recovery/error state e fix del loop idle.

1. `prompts/04-personalhub-cross-module-shared-entities.md`
2. `prompts/05-personalhub-add-soldi-module-normalize-db.md`
3. `prompts/06-personalhub-places-overlap-disambiguation.md`
4. `prompts/07-personalhub-places-manual-checkin.md`
5. `prompts/08-personalhub-places-where-was-i.md`
6. `prompts/09-personalhub-timer-places-alerts.md`
7. `prompts/10-personalhub-dark-theme.md`

L'indicatore home `✅/❌` con dettaglio stato/ultimo export è intenzionalmente accorpato al task UI/theme 10: non merita bootstrap, esplorazione, build e test di una sessione Codex autonoma. I task devono preservare le garanzie auto-export già verificate e non riesplorare/reimplementare tali feature salvo dipendenza strettamente necessaria.