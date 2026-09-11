[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=417826 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Ridurre drasticamente il rumore Telegram dei servizi Fedora/Codex senza perdere gli alert davvero utili. Le notifiche devono rappresentare azioni richieste, soglie significative o cambi di stato; successi ordinari e polling invariato devono restare silenziosi.

# Evidenza del 2026-09-11 — non riscoprire
Nell'export Telegram di oggi risultano 35 messaggi dal bot: 14 `Codex usage` (11 con `senza PROMPT_ID`), 7 `Fedora System Monitor`, 4 T7, 4 variazioni quota Codex, 3 FB-Scraper/CSV, 2 test Telegram PersonalHub e 1 APK finale.

Esempi di rumore osservato:
- Fedora: `/ libero 749.14 GiB; variazione -1.85 GiB` e altre oscillazioni ~1-2 GiB;
- FB-Scraper: `193` amici, `Aggiunti: 0`, `Rimossi: 0`, più snapshot CSV e diff CSV separati;
- Codex: molti `Pushato prompt senza PROMPT_ID:<hash> di chat 178` e alcuni normali `Pushato prompt <id> di chat <id>`;
- quota Codex: quattro messaggi consecutivi 89%→88%→87%→86%;
- T7: `Backup T7 fallito` con `T7 montato: no`, poi successo, poi altro fallimento; successivamente un promemoria scollegamento;
- PH: due artefatti `PersonalHub Telegram delivery test` consecutivi.

# Scope
Risolvi i produttori reali tramite MegaVault/systemd/repo remoti, con lookup mirati per titolo/codice notificatore. Non fare una scansione generica di tutti i repo. Riusa il package condiviso `telegram_notify`; non creare un nuovo bot/daemon e non cambiare destinazione Telegram.

Applica una policy comune minima: stesso problema invariato => silenzio; problema nuovo/cambiato => un alert; problema risolto => una sola notifica di risoluzione quando utile. Persisti lo stato necessario e sopravvivi ai restart. Nessun flood ogni ciclo timer.

## Fedora System Monitor
- elimina le notifiche basate sulla sola variazione ordinaria dello spazio libero;
- notifica spazio disco solo quando attraversa soglie warning/critical/recovery già configurate o, se mancanti, introduci soglie percentuali conservative configurabili con isteresi;
- un grande consumo improvviso può essere notificato solo se realmente anomalo e non spiegato da un backup T7 noto;
- una condizione invariata non deve ripetersi a ogni polling.

## FB-Scraper
- se `Aggiunti=0` e `Rimossi=0`: nessun messaggio Telegram e nessun CSV allegato; continua a salvare gli artefatti dove già previsto;
- se ci sono cambiamenti: UN solo messaggio con totale/+/- e, se utile, nomi sintetici; allega al massimo il diff CSV, non anche lo snapshot completo;
- errori reali restano notificati e deduplicati.

## Backup T7
- `T7 non montato/non disponibile` non deve essere presentato come generico `Backup fallito` quando il backup non è realmente partito: usa `Backup T7 non eseguito` + causa + azione richiesta;
- un vero errore deve dire in ordine: cosa è fallito, causa umana se determinabile, cosa deve fare Daniele; exit code/log solo come dettaglio secondario;
- stesso errore invariato non si ripete; un successivo successo chiude lo stato precedente;
- mantieni un solo successo conciso con durata/dati scritti/stato smontaggio; niente byte grezzi se possono essere mostrati in MiB/GiB;
- promemoria scollegamento al massimo una volta e solo se il disco risulta ancora fisicamente collegato ma già smontato dopo un intervallo ragionevole; non inviarlo se scollegato.

## Codex usage / quota
- elimina completamente Telegram per i normali `Pushato prompt ...`: il push riuscito è telemetria interna, non una notifica utente;
- `senza PROMPT_ID` diventa una anomalia stateful: un solo alert per chat/problema con conteggio e primo/ultimo rilevamento; niente hash sintetico nel testo utente salvo dettaglio diagnostico richiesto; una sola risoluzione quando torna normale;
- elimina notifiche a ogni variazione dell'1% della weekly quota;
- notifica solo attraversamenti di soglie utili `75%, 50%, 25%, 10%, 5%`, cambio/reset effettivo della finestra e recupero quota;
- aggiungi un solo digest giornaliero, solo nei giorni con uso Codex: quota restante, consumo osservato nelle 24h, reset e i prompt più costosi disponibili dai dati già raccolti;
- aggiungi un alert immediato per una singola sessione chiaramente anomala se l'osservazione mostra almeno 2 punti percentuali di quota persi nella sessione; non attribuire causalità esclusiva quando ci sono sessioni sovrapposte.

## PersonalHub Telegram preflight
- preserva l'APK finale come documento file-only senza testo aggiuntivo;
- non ripetere test di readiness se esiste una prova valida e il notifier/config non è cambiato;
- quando un nuovo test è davvero necessario per la consegna APK, preferisci una sola prova document-delivery invece della coppia testo+file, poi registra la readiness; non inviare progress/status generici.

# Verification
Aggiungi test mirati per ogni produttore modificato e una fixture/tabella di casi equivalente ai messaggi sopra. Dimostra almeno:
1. oscillazioni disco ~1-2 GiB => 0 Telegram;
2. FB 0/0 => 0 Telegram/0 allegati; cambi reali => 1 messaggio + max 1 diff;
3. T7 assente vs vero fallimento hanno testo e severità diversi, dedup + recovery funzionano;
4. push Codex riuscito => 0 Telegram; 10 cicli senza PROMPT_ID nella stessa chat => 1 alert stateful, non 10;
5. quota 89→88→87→86 => 0 alert; attraversamento 75/50/25/10/5 => 1 alert per soglia;
6. preflight PH valido => 0 test; preflight necessario => una sola prova document;
7. Telegram failure non viene dichiarato PASS e non fa avanzare lo stato di deduplica.

Non mandare una raffica di notifiche reali durante i test: mock/fake per la matrice, al massimo UNA prova reale finale del notifier condiviso se indispensabile. Non modificare PersonalHub feature code, non cambiare chat_id/token, non introdurre nuovi servizi periodici.

# PASS / stop
PASS quando la matrice odierna produrrebbe solo messaggi azionabili/significativi, tutti i produttori interessati hanno deduplica/state transition coerente e i test mirati passano. Commit/push separati per ogni repo realmente modificato, aggiorna eventuale MegaVault autorevole solo se necessario, poi operazioni terminali roadmap e STOP.

Output conciso: `PROMPT_ID`, `RESULT`, produttori modificati, notifiche eliminate/cambiate/aggiunte, policy soglie/dedup, test, repo+commit, blocker.