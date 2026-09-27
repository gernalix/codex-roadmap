PROMPT_ID=545953

Implementa SOLO la regressione telegram_insert_bot sul diff storico Grindr.

Obiettivo:
- eliminare il flood «Profilo …: aggiornamento profilo» causato da baseline/storico perso o incompatibile dopo l'enrichment;
- bootstrap/migrazione/rehydration non devono essere notificati come modifiche reali;
- non inviare snapshot completi JSON salvo debug esplicito;
- preserva tutte le notifiche Grindr realmente utili e le altre funzioni del bot.

Riproduci con fixture o DB/storico preesistente, quindi copri almeno: bootstrap da storico esistente senza falso update, prima scansione, seconda scansione invariata, una modifica reale che produce il diff corretto, nessuna regressione alle altre notifiche. Minimo cambiamento; niente refactor estranei.

Commit+push del checkpoint verificato. Usa il percorso repo single-writer già assegnato; non modificare roadmap.sqlite direttamente. Alla fine integra tramite il percorso canonico del repo e terminalizza PROMPT_ID con roadmap_finish.py. Incidenti collaterali: cattura solo la descrizione in C2 Inbox e continua.
