# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Questo file spiega in parole semplici a cosa serve ciascun prompt ancora presente in `roadmap.md`. È pensato per essere comprensibile anche senza conoscenze di programmazione.

**L'ordine e la numerazione qui sotto devono corrispondere esattamente a `roadmap.md`.** I valori `Recommended model`/`Reasoning` originali restano dentro i singoli prompt; in `roadmap.md` trovi accanto a ogni voce anche la nuova alternativa sperimentale GPT-5.6, così puoi scegliere di volta in volta quale configurazione usare.

## 1. [[prompts/personalhub-timer-quick-event-widget|personalhub-timer-quick-event-widget]]

Crea un nuovo widget Android per i pulsanti `Events` di Timer. Quando aggiungi il widget alla home scegli quale pulsante di Events deve rappresentare; da quel momento un tap sul widget esegue la stessa azione di quel pulsante senza dover aprire e cercare Timer. Puoi avere più widget, ciascuno collegato a un pulsante diverso. Se quel pulsante richiede informazioni aggiuntive, il tap apre direttamente il relativo flusso già preselezionato invece di inventare dati. Se il pulsante viene rinominato, archiviato o eliminato, il widget deve aggiornarsi o smettere di registrare eventi finché non viene riconfigurato.

## 2. [[prompts/personalhub-places-visit-history-checkin|personalhub-places-visit-history-checkin]]

Riunisce sullo stesso storico Places il check-in manuale immediato e quello retroattivo. Puoi quindi indicare esplicitamente “sono qui adesso” anche senza aspettare il GPS, oppure registrare dopo che eri stato in un luogo a una data/ora passata, eventualmente indicando anche quando te ne sei andato. Lo stesso lavoro gestisce i luoghi sovrapposti senza scegliere arbitrariamente, evita visite duplicate o incompatibili e aggiunge “Dov'ero?” per interrogare lo storico a una data e ora precise.

## 3. [[prompts/personalhub-context-composer-redesign|personalhub-context-composer-redesign]]

Butta via l'attuale interfaccia Context incastrata dentro “Nuova sessione” di Timer e ripristina il normale editor Timer. Crea invece una sezione principale di PersonalHub chiamata per ora `Composer`, costruita apposta per mettere insieme un Context in pochi tap. Appena la apri prova a capire automaticamente dove sei e quale intervallo/sessione stai vivendo; il luogo e il tempo restano sempre modificabili per creare anche Context retroattivi. Un'unica ricerca e poche chip leggibili mostrano solo 3–5 suggerimenti utili: le persone vengono ordinate in base a quanto sono state associate in passato al luogo e agli altri elementi già scelti, i Places vicini vengono privilegiati, e ogni nuovo pezzo selezionato rende più precise le proposte successive. Transazioni, assunzioni di sostanze e WordSession già registrate vengono rilevate automaticamente dal periodo scelto invece di costringerti a sfogliare liste infinite. Tutti i tipi restano comunque raggiungibili da un comando manuale secondario. Template ed Explorer restano disponibili ma non affollano più il flusso principale.

## 4. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]]

Rende sicuri gli aggiornamenti dell'app rispetto ai dati già presenti, consolidando anche lo schema risultante dai lavori Hub Context. Al primo avvio di una nuova versione, PersonalHub controlla il database ereditato: se è già compatibile lo valida, se usa uno schema più vecchio lo migra senza perdere dati e ricontrolla il risultato, mentre se è troppo nuovo o manca una migrazione rifiuta di sovrascriverlo. Aggiunge inoltre test automatici che obbligano ogni futura modifica dello schema ad avere una catena completa di migrazioni dalle versioni precedenti supportate.

## 5. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]]

Rende più affidabile il riquadro che People mostra durante una telefonata: deve aprire la persona corretta, non comparire in ritardo dopo la fine della chiamata, non riutilizzare dati di chiamate precedenti e non scrivere numeri di telefono nei registri tecnici.

## 6. [[prompts/personalhub-timer-widget-write-result|personalhub-timer-widget-write-result]]

Fa dire al widget rapido di Timer “sessione avviata” soltanto dopo che la sessione è stata davvero salvata. Se il salvataggio fallisce, niente falso messaggio di successo, falso evento o apertura dell'app come se tutto fosse riuscito.

## 7. [[prompts/personalhub-timer-session-tag-picker-ux|personalhub-timer-session-tag-picker-ux]]

Sistema la scelta dei tag quando crei una nuova sessione Timer. I tag già selezionati restano visibili come chip/card distinti e ben riconoscibili, invece di diventare una debole stringa grigia. Inoltre, se scrivi per esempio `shop`, puoi creare proprio il tag `shop` anche quando tra i risultati esiste già `shopping`; la creazione viene nascosta solo se esiste già esattamente quel nome.

## 8. [[prompts/personalhub-timer-legacy-runtime-cleanup|personalhub-timer-legacy-runtime-cleanup]]

Riunisce la pulizia dei principali residui del vecchio MultiTimeTracker dentro Timer. Timer deve usare la vera versione di PersonalHub, riprovare correttamente le riparazioni automatiche fallite e smettere di chiedere una propria cartella/database di backup. Backup e ripristino del database passano dal sistema globale di PersonalHub.

## 9. [[prompts/personalhub-places-sorting-map-navigation|personalhub-places-sorting-map-navigation]]

Migliora lista e mappa Places: ordinamento per distanza, ultima visita, tempo totale o numero visite con ASC/DESC; mappa centrata sulla posizione attuale; tap su un marker che apre la scheda del luogo.

## 10. [[prompts/personalhub-places-geofence-alerts|personalhub-places-geofence-alerts]]

Aggiunge notifiche quando entri o esci da determinati Places. Devono sopravvivere a riavvii/aggiornamenti, rispettare i permessi Android e non produrre notifiche duplicate.

## 11. [[prompts/personalhub-autoexport-status-indicator|personalhub-autoexport-status-indicator]]

Aggiunge nella home un indicatore semplice dello stato del backup automatico: aggiornato/sano oppure non configurato, arretrato o in errore, con dettagli utili accessibili al tocco.

## 12. [[prompts/personalhub-global-screen-version-footer|personalhub-global-screen-version-footer]]

Uniforma il numero di versione in tutta PersonalHub. Ogni schermata completa di People, Timer, Places, Substances, Soldi e WordPulse mostra in piccolo, in basso a destra, la versione reale di PersonalHub. Se una vecchia app da cui deriva il modulo mostrava già una propria versione, quella scritta viene sostituita invece di lasciare due numeri diversi.

## 13. [[prompts/personalhub-dark-theme|personalhub-dark-theme]]

Aggiunge un vero tema scuro coerente a tutta PersonalHub, seguendo il tema Android e mantenendo leggibili schermate, dialog, campi, errori e barre di sistema di tutti i moduli.

## 14. [[prompts/personalhub-global-audit-foundation-safe-undo|personalhub-global-audit-foundation-safe-undo]]

Costruisce insieme il backend del Registro attività e l'annullamento sicuro. PersonalHub registra semanticamente le modifiche importanti a dati e impostazioni in modo comprensibile, senza segreti, e conserva abbastanza informazioni per tentare un annullamento. L'annullamento non cancella la storia: crea una modifica compensativa e viene rifiutato se nel frattempo lo stato è cambiato o ci sono conflitti. Operazioni multiple devono essere annullate tutte insieme oppure per niente.

## 15. [[prompts/personalhub-global-audit-register-ui|personalhub-global-audit-register-ui]]

Crea la parte visibile del Registro attività: card nella home, cronologia leggibile, filtri per modulo e pulsante di annullamento quando il backend stabilisce che l'operazione può essere invertita in sicurezza.
