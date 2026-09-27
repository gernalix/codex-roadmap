PROMPT_ID=853479

Esegui SOLO Phase A dell'umbrella P0 MegaVault.

Obiettivo:
- riconcilia /home/daniele/MegaVault e /home/daniele/projects/MegaVault preservando dati e storia utili;
- scegli UN checkout + megavault.sqlite canonici;
- aggiorna tutti i consumer/path/protocolli/AGENTS/docs/script/servizi/C2/PersonalHub che puntano a copie obsolete;
- rendi bootstrap e update MegaVault automatici, minimi e non bypassabili per dirty state;
- audita i debris MegaVault-correlati sotto /home/daniele, migra ciò che serve e rimuovi/archivia il superfluo solo con recovery verificabile;
- lascia il canonico pulito, sincronizzato e AI-facing ultracompatto.

Vincoli:
- usa solo evidenza reale da filesystem/Git/DB e file pertinenti; niente esplorazione generale non necessaria;
- preserva lavoro locale e storia; prima di operazioni distruttive crea backup/checkpoint recuperabile e verifica il contenuto;
- preferisci merge/migrazione conservativa, wrapper/guard/CI automatici e riferimenti a una sola authority invece di duplicare protocolli;
- non avviare Phase B/database_inventory salvo ciò che è strettamente necessario per eliminare inventari duplicati della Phase A;
- non fare refactor estranei;
- Git è memoria operativa: checkpoint ricostruibili con commit+push; niente stash/local-only come stato canonico;
- discovery incidentale: cattura solo la descrizione in C2 Inbox e continua, salvo blocker reale.

Acceptance Phase A:
1. Un solo checkout e megavault.sqlite sono dichiarati e verificati canonici; copie divergenti fuse o archiviate in sicurezza senza perdita di dati/storia utile.
2. Tutti i consumer attivi puntano al canonico; nessun path stale attivo rimane.
3. Bootstrap executor minimo legge i vincoli pertinenti e gli update canonici hanno enforcement automatico semplice; dirty state non autorizza bypass.
4. Debris MegaVault-correlati sotto /home/daniele sono classificati e bonificati con recovery verificabile.
5. Documentazione AI-facing è ultracompressa/non ridondante; repo canonico pulito, sincronizzato e recuperabile.

Termina appena questi criteri sono verificati. Report finale conciso con evidenze/test/commit/PR e remaining reale.
