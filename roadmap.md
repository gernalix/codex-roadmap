# Codex Roadmap

Ordine consigliato di esecuzione, ricalcolato sullo stato corrente di PersonalHub. Un task Codex alla volta sullo stesso progetto.

Stato già acquisito e quindi NON da duplicare nei task futuri: database PH unificato e migrazione verificata; settings/database-backup integrati; sync Datasette local-first; Places API key/address suggestions fix; shortcut pinnabili e percorso diretto ottimizzato; protezione app reale dai benchmark distruttivi; auto-export SAF generation-based durevole con recovery/error state e fix del loop idle.

1. `prompts/03-personalhub-autoexport-multitimer-parity.md`
2. `prompts/04-personalhub-cross-module-shared-entities.md`
3. `prompts/05-personalhub-add-soldi-module-normalize-db.md`
4. `prompts/06-personalhub-places-overlap-disambiguation.md`
5. `prompts/07-personalhub-places-manual-checkin.md`
6. `prompts/08-personalhub-places-where-was-i.md`
7. `prompts/09-personalhub-timer-places-alerts.md`
8. `prompts/10-personalhub-dark-theme.md`

Nota sul task 03: l'engine di auto-export è già implementato e corretto; il prompt è stato ristretto alla sola parità residua con MultiTimer per indicatore `✅/❌` e dettaglio stato/ultimo export. I task successivi devono preservare le garanzie già verificate e non riesplorare/reimplementare queste feature salvo dipendenza strettamente necessaria.