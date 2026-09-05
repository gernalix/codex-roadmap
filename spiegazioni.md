# Spiegazioni della roadmap

Questo file spiega in parole semplici a cosa serve ciascun prompt ancora presente in `roadmap.md`. È pensato per essere comprensibile anche senza conoscenze di programmazione.

**L'ordine e la numerazione qui sotto devono corrispondere esattamente a `roadmap.md`.**

## 1. `personalhub-soldi-account-filter-lifecycle.md`

Serve a correggere due problemi del modulo Soldi.

Primo: se escludi un conto dal totale del denaro posseduto, le transazioni di quel conto devono comunque restare visibili nello storico. L'esclusione deve cambiare solo il totale mostrato.

Secondo: se stai compilando una transazione o modificando qualcosa e Android ricrea la schermata, per esempio dopo una rotazione o un'altra normale interruzione, quello che avevi già scritto non deve sparire.

## 2. `personalhub-people-call-overlay-hardening.md`

Serve a rendere più affidabile il riquadro che People mostra durante una telefonata.

Il pulsante per aprire il contatto deve portare davvero alla persona corretta senza rischiare un errore. Inoltre il riquadro non deve apparire in ritardo quando la chiamata è già terminata, né mostrare per errore dati di una telefonata precedente. Infine i numeri di telefono non devono essere scritti nei registri tecnici dell'app.

## 3. `personalhub-timer-widget-write-result.md`

Serve a fare in modo che il widget rapido di Timer dica “sessione avviata” soltanto quando la sessione è stata davvero salvata.

Oggi può succedere che l'app mostri vibrazione o messaggio di successo anche se il salvataggio fallisce. Dopo questo task, in caso di errore verrà mostrato un errore reale e non verranno creati falsi eventi nello storico.

## 4. `personalhub-timer-version-autoconsistency.md`

Serve a correggere il modo in cui Timer capisce quale versione di PersonalHub è installata e quando deve eseguire alcune correzioni automatiche interne.

In pratica Timer non deve confondere la vecchia versione del progetto da cui deriva con la versione reale di PersonalHub. Inoltre, se una correzione automatica fallisce, l'app deve poter riprovare in seguito invece di considerarla erroneamente completata.

## 5. `personalhub-timer-remove-legacy-first-run-backup.md`

Serve a eliminare una vecchia procedura di backup rimasta dentro Timer.

PersonalHub ormai usa un unico database e un unico sistema generale di backup. Timer non deve quindi chiedere una propria cartella di backup o fingere di poter ripristinare un database separato. Tutte le funzioni di backup del database devono portare al sistema generale di PersonalHub.

## 6. `personalhub-timer-alerts.md`

Serve a rendere realmente utilizzabili e affidabili gli avvisi di Timer.

Dovrai poter creare, modificare, attivare, disattivare e cancellare gli avvisi. Gli avvisi già programmati dovranno inoltre continuare a funzionare dopo il riavvio del telefono o dopo un aggiornamento dell'app, senza duplicarsi.

## 7. `personalhub-remove-idle-polling.md`

Serve a evitare che PersonalHub controlli il database continuamente ogni 2 secondi anche quando non sta succedendo nulla.

L'obiettivo è ridurre lavoro inutile, consumo di CPU e batteria, mantenendo però invariata l'affidabilità del backup automatico e della sincronizzazione. L'app dovrà reagire quando avviene davvero una modifica, mantenendo comunque un sistema di recupero nel caso qualcosa venga interrotto.

## 8. `personalhub-complete-module-capsulization.md`

Serve a mettere ordine nella struttura interna di PersonalHub senza cambiare ciò che vede l'utente.

L'idea è che ogni modulo — People, Timer, Places, Substances, WordPulse e Soldi — abbia responsabilità ben separate e non dipenda direttamente dai dettagli interni degli altri moduli. PersonalHub continuerà comunque a usare un unico database. Questo rende l'app più facile da modificare in futuro e riduce il rischio che una modifica in un modulo rompa gli altri.

## 9. `personalhub-cross-module-shared-entities.md`

Serve a creare il collegamento corretto tra People, Timer e Places.

Esempio: una sessione Timer “16:00–18:00 passeggiata con Giovanni al Cafe Oscar” dovrà poter essere collegata alla vera scheda di Giovanni e alla vera scheda del Cafe Oscar, invece di salvare copie separate dei loro nomi.

Inoltre quella stessa sessione Timer potrà contare come visita al Cafe Oscar nello storico di Places, senza creare due visite uguali e quindi senza raddoppiare tempo o numero di visite.

## 10. `personalhub-cross-module-linked-entities-ui.md`

Serve a rendere utilizzabili dall'interfaccia i collegamenti creati dal task precedente.

Quando crei o modifichi una sessione Timer potrai scegliere una Persona e un Luogo già esistenti. Potrai anche creare direttamente una nuova persona o un nuovo luogo senza uscire dal flusso. Un nuovo luogo creato così avrà automaticamente un raggio di 75 metri.

Le attività collegate saranno poi visibili anche dalla scheda della persona e del luogo, e toccandole si potrà passare da una sezione all'altra. Se cambi il nome di una persona o di un luogo, il nuovo nome apparirà automaticamente ovunque.

## 11. `personalhub-places-overlap-disambiguation.md`

Serve a evitare check-in automatici sbagliati quando ti trovi contemporaneamente dentro il raggio di più luoghi salvati.

Se sei dentro un solo luogo, PersonalHub può sceglierlo automaticamente. Se invece sei dentro due o più luoghi sovrapposti, deve sempre chiederti quale intendi selezionare, invece di scegliere da solo quello apparentemente più vicino.

## 12. `personalhub-places-manual-checkin.md`

Serve ad aggiungere manualmente visite passate a un luogo.

Potrai aprire un Place e indicare, per esempio, “sono stato qui ieri dalle 15:00 alle 17:30”. La visita manuale finirà nello stesso storico delle visite rilevate automaticamente e verrà usata anche nelle statistiche, senza creare un secondo tipo di storico separato.

## 13. `personalhub-places-where-was-i.md`

Serve ad aggiungere la funzione “Dov'ero?”.

Scegliendo una data e un'ora, PersonalHub cercherà nello storico dei luoghi e ti dirà dove risultavi essere in quel momento. Se quell'istante cade tra due visite, potrà dire che eri presumibilmente in spostamento dal luogo precedente a quello successivo, senza inventare percorsi o posizioni non registrate.

## 14. `personalhub-places-sorting-map-navigation.md`

Serve a migliorare lista e mappa di Places.

Potrai ordinare i luoghi per distanza dalla posizione attuale, ultima visita, tempo totale trascorso o numero di visite, scegliendo ogni volta ordine crescente o decrescente.

La mappa si aprirà centrata sulla tua posizione attuale quando disponibile. Inoltre, toccando il simbolo di un singolo luogo sulla mappa si aprirà direttamente la scheda di quel luogo.

## 15. `personalhub-places-geofence-alerts.md`

Serve a ricevere notifiche quando entri o esci da determinati luoghi.

Per ogni Place potrai attivare un avviso all'ingresso, all'uscita o in entrambi i casi. Gli avvisi continueranno a funzionare anche dopo riavvii o aggiornamenti dell'app, compatibilmente con i permessi concessi ad Android, e non dovranno produrre notifiche duplicate.

## 16. `personalhub-substances-core-integrity-command-stock-archive.md`

È la prima grande fase di sistemazione del modulo Substances.

Serve soprattutto a rendere sicuri i dati: modificare una sostanza non deve cancellare accidentalmente il suo storico; tutte le operazioni devono seguire le stesse regole; il conteggio delle scorte deve essere matematicamente corretto; annullare un consumo deve restituire esattamente la quantità tolta.

Aggiunge inoltre un vero sistema di archiviazione e ripristino delle sostanze, conservando lo storico, ed elimina eventuali dati dimostrativi che non devono apparire nei dati reali.

## 17. `personalhub-substances-scheduling-intake-interactions-macros.md`

È la seconda fase di Substances e serve a rendere corretti orari, assunzioni, interazioni e macro.

L'app dovrà capire correttamente terapie con orari precisi, giorni specifici, data di inizio/fine, terapia continua o al bisogno. Non dovrà inventare dosi mancate nel futuro o gestire male la mezzanotte.

Ogni assunzione, anche se parte da una macro, dovrà rispettare le stesse regole: orario, quantità, scorte e possibili interazioni con altre sostanze. Le interazioni che bloccano davvero un'assunzione non potranno essere aggirate da altri pulsanti o percorsi dell'app.

## 18. `personalhub-substances-prescriptions-notifications.md`

È la terza fase di Substances e riguarda prescrizioni, rifornimenti e notifiche.

Potrai gestire prescrizioni e rifornimenti ricorrenti in modo più completo, compresi quantità, date e modifiche.

Le notifiche per dose, dose mancata, fine di un'interazione e prossimo rifornimento verranno ricostruite in modo affidabile dopo riavvio, aggiornamento dell'app o cambio di ora/fuso, evitando notifiche vecchie o duplicate.

## 19. `personalhub-substances-history-performance.md`

È la quarta fase di Substances e serve a rendere lo storico corretto e veloce anche dopo anni di utilizzo.

Lo storico dovrà continuare a riconoscere una sostanza anche se la rinomini, permettere ricerca e filtri e mostrare correttamente dosi e orari.

Inoltre l'app non dovrà caricare inutilmente migliaia di eventi tutti insieme né creare enormi quantità di righe artificiali per ogni dose teoricamente mancata. In pratica lo storico deve restare fluido anche con molti dati.

## 20. `personalhub-substances-global-import-export-cleanup.md`

È la quinta fase di Substances e serve a eliminare i vecchi sistemi di backup separati del modulo.

Substances deve usare lo stesso unico database e lo stesso sistema sicuro di importazione, esportazione e backup del resto di PersonalHub. Quando scegli un file da importare, deve essere eseguito un vero import controllato; non basta semplicemente aprire la schermata dei backup e dichiarare successo.

## 21. `personalhub-substances-ui-navigation-final-qa.md`

È l'ultima fase di Substances e riguarda soprattutto ciò che vedi e usi.

La schermata principale verrà organizzata in modo chiaro per distinguere, per esempio, sostanze da prendere, da prendere più tardi, bloccate, già assunte e al bisogno.

La scheda di ogni sostanza renderà facilmente accessibili assunzione, scorte, storico, prescrizione, interazioni, modifica e archiviazione. Verranno corretti anche diversi problemi di usabilità, come pulsanti ambigui, schermate troppo dense o stato perso tornando nel modulo.

Alla fine il modulo verrà provato direttamente sia su Pixel sia su TCL.

## 22. `personalhub-autoexport-status-indicator.md`

Serve ad aggiungere nella home di PersonalHub un piccolo indicatore che ti dica immediatamente se il backup automatico sta funzionando.

Un simbolo positivo indicherà che il backup è aggiornato e sano; uno negativo che manca la configurazione, il backup è rimasto indietro o si è verificato un errore. Toccandolo potrai vedere informazioni come ultimo backup riuscito, cartella usata e ultimo errore.

## 23. `personalhub-dark-theme.md`

Serve ad aggiungere un vero tema scuro a tutta PersonalHub.

L'app seguirà automaticamente il tema chiaro/scuro di Android e tutte le sezioni principali dovranno rimanere leggibili e coerenti: home, People, Timer, Places, Substances, WordPulse e Soldi, compresi finestre, campi di testo, messaggi di errore e barre di sistema.

## 24. `personalhub-global-audit-foundation.md`

È la prima fase del Registro attività globale.

Serve a far registrare automaticamente a PersonalHub le modifiche importanti ai dati e alle impostazioni in un linguaggio che possa poi essere mostrato chiaramente all'utente.

Per esempio: creazione di una persona, modifica di un luogo, cancellazione di una transazione, modifica di un'impostazione, aggiornamento dell'app. Il registro dovrà conservare abbastanza informazioni da capire cosa è cambiato, ma senza salvare password, token o altri segreti.

Questa fase costruisce il sistema che raccoglie gli eventi, ma non ancora la schermata finale del registro.

## 25. `personalhub-global-audit-safe-undo.md`

È la seconda fase del Registro attività e serve a permettere di annullare in sicurezza le modifiche registrate.

Esempio: se modifichi una voce e poi tocchi “annulla”, PersonalHub proverà a riportarla allo stato precedente. Ma se nel frattempo quella voce è stata modificata ancora, l'app non deve cancellare alla cieca le modifiche più recenti: deve rifiutare l'annullamento e spiegare perché.

Anche le operazioni che coinvolgono più modifiche devono essere annullate tutte insieme oppure per niente. Alcuni eventi, come un aggiornamento dell'app, verranno invece indicati chiaramente come non annullabili.

## 26. `personalhub-global-audit-register-ui.md`

È la terza e ultima fase del Registro attività e crea la parte visibile all'utente.

Nella home comparirà una card `Registro attività`. Aprendola vedrai la cronologia delle modifiche con data, modulo interessato e descrizione comprensibile, senza codici incomprensibili.

Potrai filtrare gli eventi per People, Timer, Places, Substances, WordPulse, Soldi, Impostazioni e Sistema. Quando un evento può essere annullato in sicurezza, verrà mostrato un apposito pulsante di annullamento; se non può più essere annullato, l'app ne mostrerà il motivo.
