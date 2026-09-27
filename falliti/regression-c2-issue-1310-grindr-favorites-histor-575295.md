PROMPT_ID=575295

Correggi SOLO la regressione: quando un favorito Grindr viene bloccato e scompare dalla lista Favorites, deve arrivare la notifica Telegram prevista.

Vincoli:
- parti dal codice e dai test del monitor corrente; non rifare l'architettura;
- identifica il punto preciso in cui la transizione block/removal perde l'evento/notifica;
- preserva deduplica, storico append-only, callback e altri eventi già funzionanti;
- aggiungi una regressione test mirata per il caso block→sparizione→Telegram;
- nessun refactor estraneo.

Acceptance:
- caso riprodotto prima/fallisce e passa dopo il fix;
- suite pertinente PASS;
- commit+push del fix verificato; report finale conciso con evidenze.
