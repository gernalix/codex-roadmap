# Codex Roadmap

Ordine consigliato di esecuzione, ricalcolato sullo stato corrente di PersonalHub. Un task Codex alla volta sullo stesso progetto.

Stato già acquisito e quindi NON da duplicare nei task futuri: database PH unificato e migrazione verificata; settings/database-backup integrati; sync Datasette local-first; Places API key/address suggestions fix; shortcut pinnabili e percorso diretto ottimizzato; protezione app reale dai benchmark distruttivi; auto-export SAF generation-based durevole con recovery/error state e fix del loop idle; Soldi migrato come modulo PH con schema finance iniziale nel commit `a20e9171a2a48775980d673f2e418ca847b0121c`.

1. `prompts/04-personalhub-cross-module-shared-entities.md`
2. `prompts/06-personalhub-places-overlap-disambiguation.md`
3. `prompts/07-personalhub-places-manual-checkin.md`
4. `prompts/08-personalhub-places-where-was-i.md`
5. `prompts/09-personalhub-timer-places-alerts.md`
6. `prompts/10-personalhub-dark-theme.md`

Il correttivo Soldi 05b precede l'architettura cross-module: completa account/balance, identità prodotto e interscambio Git prima che il task 04 definisca le relazioni condivise sullo schema finance definitivo.

L'indicatore home `✅/❌` con dettaglio stato/ultimo export è intenzionalmente accorpato al task UI/theme 10: non merita bootstrap, esplorazione, build e test di una sessione Codex autonoma. I task devono preservare le garanzie auto-export già verificate e non riesplorare/reimplementare tali feature salvo dipendenza strettamente necessaria.
