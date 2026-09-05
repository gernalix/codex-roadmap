# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Questo file spiega in parole semplici a cosa serve ciascun prompt ancora presente in `roadmap.md`. È pensato per essere comprensibile anche senza conoscenze di programmazione.

**L'ordine e la numerazione qui sotto devono corrispondere esattamente a `roadmap.md`.**

## 1. [[prompts/personalhub-substances-core-integrity-command-stock-archive|personalhub-substances-core-integrity-command-stock-archive]]

Prima fase Substances: mette in sicurezza i dati di base. Modificare una sostanza non deve cancellarne lo storico; le scorte e gli annullamenti devono tornare sempre; archiviazione e ripristino devono essere reversibili; non si possono creare due pulsanti/sostanze con lo stesso nome.

## 2. [[prompts/personalhub-substances-therapy-intake-interactions-notifications|personalhub-substances-therapy-intake-interactions-notifications]]

Sistema assunzioni, orari, interazioni e notifiche. Dopo un'assunzione il pulsante della sostanza resta disponibile e il sistema sa qual è il prossimo orario consigliato. Le interazioni non fanno sparire o disabilitare pulsanti: se una combinazione è bloccata, il blocco viene spiegato al tap. Le finestre di attesa mostrano dati per un conto alla rovescia e producono una notifica alla scadenza. Corregge anche il bug per cui modificare un'interazione continuava a conservare il primo valore inserito.

## 3. [[prompts/personalhub-substances-prescriptions-stock-crossmodule|personalhub-substances-prescriptions-stock-crossmodule]]

Rifà completamente Prescriptions. Ogni riga rappresenta una singola prescrizione, ma lo stesso farmaco può avere più prescrizioni senza creare più pulsanti in Home. Gestisce dosi residue, dose in mg, frequenza giornaliera/settimanale, date e data stimata di esaurimento. Il medico viene scelto da People e il costo da una delle cinque voci Soldi più recenti con lo stesso nome. Una nuova prescrizione con un nome mai usato crea automaticamente la sostanza; con un nome già esistente riusa quella esistente.

## 4. [[prompts/personalhub-substances-history-data-integration|personalhub-substances-history-data-integration]]

Rende History corretto e veloce anche con molti dati. Ogni voce ha matita per modificarla e cestino per eliminarla, mantenendo coerenti scorte e dosi residue delle prescrizioni. Nello stesso task vengono eliminati i vecchi percorsi che trattano Substances come se avesse un proprio database/backup: importazione e backup autorevoli usano l'unico `personalhub.db`.

## 5. [[prompts/personalhub-substances-ui-navigation-final-qa|personalhub-substances-ui-navigation-final-qa]]

Fase finale Substances: sistema schermate e navigazione sopra il backend definitivo. I pulsanti restano visibili dopo il tap e mostrano in piccolo il prossimo orario; le interazioni mostrano countdown con il nome della sostanza; il `+` cambia funzione in modo logico in base alla tab senza creare duplicati. Verifica inoltre Prescriptions, History e tutti i flussi principali su Pixel e TCL.

## 6. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]]

Rende più affidabile il riquadro che People mostra durante una telefonata: deve aprire la persona corretta, non comparire in ritardo dopo la fine della chiamata, non riutilizzare dati di chiamate precedenti e non scrivere numeri di telefono nei registri tecnici.

## 7. [[prompts/personalhub-timer-widget-write-result|personalhub-timer-widget-write-result]]

Fa dire al widget rapido di Timer “sessione avviata” soltanto dopo che la sessione è stata davvero salvata. Se il salvataggio fallisce, niente falso messaggio di successo, falso evento o apertura dell'app come se tutto fosse riuscito.

## 8. [[prompts/personalhub-timer-legacy-runtime-cleanup|personalhub-timer-legacy-runtime-cleanup]]

Riunisce la pulizia dei principali residui del vecchio MultiTimeTracker dentro Timer. Timer deve usare la vera versione di PersonalHub, riprovare correttamente le riparazioni automatiche fallite e smettere di chiedere una propria cartella/database di backup. Backup e ripristino del database passano dal sistema globale di PersonalHub.

## 9. [[prompts/personalhub-timer-alerts|personalhub-timer-alerts]]

Rende realmente utilizzabili gli avvisi di Timer: creazione, modifica, attivazione, disattivazione e cancellazione. Gli avvisi programmati devono inoltre essere ricostruiti dopo riavvio o aggiornamento dell'app senza duplicarsi.

## 10. [[prompts/personalhub-remove-idle-polling|personalhub-remove-idle-polling]]

Elimina il controllo continuo del database ogni 2 secondi quando non succede nulla, riducendo lavoro inutile e consumo di batteria senza rendere meno affidabili backup automatico e sincronizzazione.

## 11. [[prompts/personalhub-complete-module-capsulization|personalhub-complete-module-capsulization]]

Mette ordine nell'architettura interna: ogni modulo deve possedere meglio i propri dettagli e comunicare attraverso interfacce chiare, pur continuando a usare l'unico database PersonalHub. È un refactor tecnico importante ma non dovrebbe cambiare il comportamento visibile.

## 12. [[prompts/personalhub-cross-module-entity-linking|personalhub-cross-module-entity-linking]]

Crea in un solo task il collegamento completo People ↔ Timer ↔ Places. Una sessione Timer può riferirsi alla vera persona e al vero luogo, senza copiarne nomi e dati. Se il Timer è collegato a un Place, quello stesso intervallo conta come visita Places una sola volta. Nell'editor Timer puoi scegliere o creare una persona/un luogo; un nuovo luogo creato lì parte con raggio 75 m. Le attività collegate diventano visibili e navigabili anche dalle relative schede.

## 13. [[prompts/personalhub-places-visit-history-checkin|personalhub-places-visit-history-checkin]]

Riunisce tre lavori che usano lo stesso storico Places. Se sei dentro più luoghi sovrapposti l'app deve chiedere quale scegliere; puoi aggiungere manualmente una visita passata; e con “Dov'ero?” puoi scegliere data/ora e vedere quale luogo risulta dallo storico o, se sei tra due visite, tra quali luoghi stavi presumibilmente spostandoti senza inventare una posizione.

## 14. [[prompts/personalhub-places-sorting-map-navigation|personalhub-places-sorting-map-navigation]]

Migliora lista e mappa Places: ordinamento per distanza, ultima visita, tempo totale o numero visite con ASC/DESC; mappa centrata sulla posizione attuale; tap su un marker che apre la scheda del luogo.

## 15. [[prompts/personalhub-places-geofence-alerts|personalhub-places-geofence-alerts]]

Aggiunge notifiche quando entri o esci da determinati Places. Devono sopravvivere a riavvii/aggiornamenti, rispettare i permessi Android e non produrre notifiche duplicate.

## 16. [[prompts/personalhub-autoexport-status-indicator|personalhub-autoexport-status-indicator]]

Aggiunge nella home un indicatore semplice dello stato del backup automatico: aggiornato/sano oppure non configurato, arretrato o in errore, con dettagli utili accessibili al tocco.

## 17. [[prompts/personalhub-dark-theme|personalhub-dark-theme]]

Aggiunge un vero tema scuro coerente a tutta PersonalHub, seguendo il tema Android e mantenendo leggibili schermate, dialog, campi, errori e barre di sistema di tutti i moduli.

## 18. [[prompts/personalhub-global-audit-foundation-safe-undo|personalhub-global-audit-foundation-safe-undo]]

Costruisce insieme il backend del Registro attività e l'annullamento sicuro. PersonalHub registra semanticamente le modifiche importanti a dati e impostazioni in modo comprensibile, senza segreti, e conserva abbastanza informazioni per tentare un annullamento. L'annullamento non cancella la storia: crea una modifica compensativa e viene rifiutato se nel frattempo lo stato è cambiato o ci sono conflitti. Operazioni multiple devono essere annullate tutte insieme oppure per niente.

## 19. [[prompts/personalhub-global-audit-register-ui|personalhub-global-audit-register-ui]]

Crea la parte visibile del Registro attività: card nella home, cronologia leggibile, filtri per modulo e pulsante di annullamento quando il backend stabilisce che l'operazione può essere invertita in sicurezza.
