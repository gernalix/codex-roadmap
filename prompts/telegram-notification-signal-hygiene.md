[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=417826 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Migliorare utilità, testo e deduplica delle notifiche Telegram osservate il 2026-09-11 senza ridurre due segnali che l'utente vuole mantenere esattamente come prima: notifiche sulle oscillazioni dello spazio libero Fedora e notifiche per ogni variazione della quota Codex.

Inoltre, OGNI messaggio Telegram generato da qualunque progetto coinvolto deve iniziare con il `project_id` MegaVault del progetto sorgente.

# Regola globale project_id — obbligatoria
Prima di modificare i produttori, risolvi i relativi `project_id` dall'attuale `megavault.sqlite` autorevole (`projects`/`project_aliases`/`repositories`); non indovinare e non riusare ID per nome simile.

Formato obbligatorio all'inizio di ogni messaggio/caption Telegram:

`project_id=<INTEGER> | ...`

Regole:
- il prefisso deve essere letteralmente il primo contenuto testuale visibile;
- vale per alert, warning, successi, recovery, digest, test, file/document caption e qualunque altra notifica prodotta dai progetti interessati;
- per componenti condivisi come `telegram_notify`, usa il `project_id` del PROGETTO CHE HA ORIGINATO il messaggio, non quello dell'helper condiviso;
- se il produttore non sa quale progetto ha originato la notifica, correggi il call-site/API affinché lo sappia esplicitamente: niente fallback silenzioso e niente `project_id=UNKNOWN`;
- non stampare chat_id, token o altri segreti;
- aggiorna i test affinché falliscano se una notifica non comincia col prefisso corretto.

# Evidenza del 2026-09-11 — non riscoprire
Nell'export Telegram di oggi risultano 35 messaggi dal bot: 14 `Codex usage` (11 con `senza PROMPT_ID`), 7 `Fedora System Monitor`, 4 T7, 4 variazioni quota Codex, 3 FB-Scraper/CSV, 2 test Telegram PersonalHub e 1 APK finale.

Esempi osservati:
- Fedora: `/ libero 749.14 GiB; variazione -1.85 GiB` e altre oscillazioni dello spazio libero;
- FB-Scraper: `193` amici, `Aggiunti: 0`, `Rimossi: 0`, più snapshot CSV e diff CSV separati;
- Codex: molti `Pushato prompt senza PROMPT_ID:<hash> di chat 178` e alcuni normali `Pushato prompt <id> di chat <id>`;
- quota Codex: notifiche 89%→88%→87%→86%;
- T7: `Backup T7 fallito` con `T7 montato: no`, poi successo, poi altro fallimento; successivamente un promemoria scollegamento;
- PH: due artefatti `PersonalHub Telegram delivery test` consecutivi.

# Scope
Risolvi i produttori reali tramite MegaVault/systemd/repo remoti, con lookup mirati per titolo/codice notificatore. Non fare una scansione generica di tutti i repo. Riusa il package condiviso `telegram_notify`; non creare un nuovo bot/daemon e non cambiare destinazione Telegram.

Applica deduplica/state transition SOLO dove non contraddice le due eccezioni esplicite sotto. Per gli altri problemi: stesso problema invariato => silenzio; problema nuovo/cambiato => un alert; problema risolto => una sola notifica di risoluzione quando utile. Persisti lo stato necessario e sopravvivi ai restart.

## Fedora System Monitor — PRESERVA trigger esistente
La precedente versione di questo prompt era sbagliata nel voler eliminare le notifiche per oscillazioni ordinarie dello spazio libero.

- individua nel codice/config corrente la soglia/cadenza GIA' ESISTENTE che fa scattare le notifiche quando lo spazio libero cambia di circa `N` GiB;
- NON scegliere una nuova soglia, NON convertirla in percentuale, NON alzarla e NON abbassarla;
- preserva esattamente la semantica corrente: direzione/i considerate, baseline, isteresi/eventuale accumulo e reset della baseline;
- se il valore attuale è configurabile, lascialo configurabile e invariato;
- conserva quindi le notifiche sulle oscillazioni dello spazio libero con la stessa frequenza di prima;
- puoi migliorare il testo rendendolo più leggibile, ma deve continuare a mostrare almeno spazio libero corrente e variazione che ha causato il trigger;
- aggiungi obbligatoriamente il prefisso `project_id=<id Fedora System Monitor> |`;
- eventuali altri alert Fedora possono essere deduplicati, ma NON deduplicare/sopprimere una nuova oscillazione che secondo la logica preesistente avrebbe generato una nuova notifica.

## FB-Scraper
- se `Aggiunti=0` e `Rimossi=0`: nessun messaggio Telegram e nessun CSV allegato; continua a salvare gli artefatti dove già previsto;
- se ci sono cambiamenti: UN solo messaggio con totale/+/- e, se utile, nomi sintetici; allega al massimo il diff CSV, non anche lo snapshot completo;
- errori reali restano notificati e deduplicati;
- ogni messaggio/caption comincia col `project_id` del progetto FB-Scraper.

## Backup T7
- `T7 non montato/non disponibile` non deve essere presentato come generico `Backup fallito` quando il backup non è realmente partito: usa `Backup T7 non eseguito` + causa + azione richiesta;
- un vero errore deve dire in ordine: cosa è fallito, causa umana se determinabile, cosa deve fare Daniele; exit code/log solo come dettaglio secondario;
- stesso errore invariato non si ripete; un successivo successo chiude lo stato precedente;
- mantieni un solo successo conciso con durata/dati scritti/stato smontaggio; usa MiB/GiB invece di byte grezzi quando possibile;
- promemoria scollegamento al massimo una volta e solo se il disco risulta ancora fisicamente collegato ma già smontato dopo un intervallo ragionevole;
- ogni messaggio comincia col `project_id` del progetto T7/backup risolto da MegaVault.

## Codex usage / quota — PRESERVA ogni variazione quota
### Push/pubblicazione prompt
- elimina Telegram per i normali `Pushato prompt ...`: il push riuscito resta telemetria interna;
- `senza PROMPT_ID` resta una anomalia utile: un solo alert stateful per chat/problema con conteggio e primo/ultimo rilevamento; una sola risoluzione quando torna normale;
- ogni relativo messaggio comincia col `project_id` del progetto `codex-usage-monitor`/produttore effettivo risolto da MegaVault.

### Weekly quota
La precedente versione di questo prompt era sbagliata nel voler sostituire le notifiche a ogni variazione con soglie 75/50/25/10/5.

- conserva ESATTAMENTE il comportamento corrente che notifica ogni variazione osservata della weekly quota, anche minima (per esempio 89%→88%→87%→86% devono continuare a produrre quattro notifiche);
- non introdurre soglie sostitutive, batching, digest sostitutivo, debounce o deduplica che nascondano una variazione reale;
- conserva anche le notifiche correnti relative a reset/cambio finestra e disponibilità dei reset se già previste;
- migliora il testo, se utile, mostrando chiaramente `precedente → nuovo`, differenza in punti percentuali, momento reset e reset disponibili, senza perdere informazioni oggi presenti;
- ogni notifica quota comincia col `project_id` del progetto che monitora/pubblica la quota Codex;
- un eventuale digest giornaliero è ammesso SOLO come informazione aggiuntiva e non può sostituire nessuna notifica di variazione; crealo solo se porta valore netto e usa dati già raccolti;
- un eventuale alert per sessione anomala è anch'esso aggiuntivo e deve evitare falsa attribuzione quando sessioni si sovrappongono.

## PersonalHub Telegram
- preserva la consegna dell'APK finale;
- non ripetere test di readiness se esiste una prova valida e notifier/config non è cambiato;
- quando un nuovo test è davvero necessario, preferisci una sola prova document-delivery invece della coppia testo+file;
- il nuovo requisito globale `project_id` prevale sul precedente `caption=none`: APK finale, test document e qualunque altro invio PH devono avere una caption che INIZIA con `project_id=<project_id PersonalHub> |`; evita altro testo di status/progresso non necessario.

# Verification
Aggiungi test mirati per ogni produttore modificato e una fixture/tabella di casi equivalente ai messaggi sopra. Dimostra almeno:
1. una variazione spazio disco che secondo la configurazione preesistente supera il trigger continua a notificare; una che non lo supera continua a non notificare; il valore/algoritmo della soglia non cambia;
2. quattro variazioni quota 89→88→87→86 producono ancora QUATTRO notifiche, ora col project_id e testo corretto;
3. FB 0/0 => 0 Telegram/0 allegati; cambi reali => 1 messaggio + max 1 diff;
4. T7 assente vs vero fallimento hanno testo e severità diversi, dedup + recovery funzionano;
5. push Codex riuscito => 0 Telegram; 10 cicli senza PROMPT_ID nella stessa chat => 1 alert stateful, non 10;
6. preflight PH valido => 0 test; preflight necessario => una sola prova document;
7. OGNI messaggio/caption prodotto nei test comincia col `project_id` corretto del progetto sorgente;
8. un call-site senza project_id valido fallisce chiaramente invece di inviare una notifica senza identità;
9. Telegram failure non viene dichiarato PASS e non fa avanzare lo stato di deduplica.

Non mandare una raffica di notifiche reali durante i test: mock/fake per la matrice; al massimo UNA prova reale finale del notifier condiviso se indispensabile. Non modificare feature PersonalHub, non cambiare chat_id/token, non introdurre nuovi servizi periodici.

# PASS / stop
PASS quando le frequenze storiche delle notifiche spazio-disco e quota Codex sono preservate, le altre notifiche risultano più informative/meno ridondanti, e il 100% dei messaggi Telegram porta come primo contenuto il `project_id` corretto del progetto sorgente. Commit/push separati per ogni repo realmente modificato, aggiorna MegaVault autorevole solo se necessario, poi operazioni terminali roadmap e STOP.

Output conciso: `PROMPT_ID`, `RESULT`, project_id risolti per produttore, trigger disco prima/dopo, trigger quota prima/dopo, notifiche eliminate/cambiate/aggiunte, test, repo+commit, blocker.