# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Questo file spiega in parole semplici a cosa serve ciascun prompt ancora presente in `roadmap.md`. È pensato per essere comprensibile anche senza conoscenze di programmazione.

**L'ordine e la numerazione qui sotto devono corrispondere esattamente a `roadmap.md`.** I valori `Recommended model`/`Reasoning` originali restano dentro i singoli prompt; in `roadmap.md` trovi accanto a ogni voce anche la nuova alternativa sperimentale GPT-5.6, così puoi scegliere di volta in volta quale configurazione usare.

## 1. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]]

Rende sicuri gli aggiornamenti dell'app rispetto ai dati già presenti, consolidando anche lo schema risultante dal nuovo blocco Hub Context. Al primo avvio di una nuova versione, PersonalHub controlla il database ereditato: se è già compatibile lo valida, se usa uno schema più vecchio lo migra senza perdere dati e ricontrolla il risultato, mentre se è troppo nuovo o manca una migrazione rifiuta di sovrascriverlo. Aggiunge inoltre test automatici che obbligano ogni futura modifica dello schema ad avere una catena completa di migrazioni dalle versioni precedenti supportate.

## 2. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]]

Rende più affidabile il riquadro che People mostra durante una telefonata: deve aprire la persona corretta, non comparire in ritardo dopo la fine della chiamata, non riutilizzare dati di chiamate precedenti e non scrivere numeri di telefono nei registri tecnici.

## 3. [[prompts/personalhub-timer-widget-write-result|personalhub-timer-widget-write-result]]

Fa dire al widget rapido di Timer “sessione avviata” soltanto dopo che la sessione è stata davvero salvata. Se il salvataggio fallisce, niente falso messaggio di successo, falso evento o apertura dell'app come se tutto fosse riuscito.

## 4. [[prompts/personalhub-timer-session-tag-picker-ux|personalhub-timer-session-tag-picker-ux]]

Sistema la scelta dei tag quando crei una nuova sessione Timer. I tag già selezionati restano visibili come chip/card distinti e ben riconoscibili, invece di diventare una debole stringa grigia. Inoltre, se scrivi per esempio `shop`, puoi creare proprio il tag `shop` anche quando tra i risultati esiste già `shopping`; la creazione viene nascosta solo se esiste già esattamente quel nome.

## 5. [[prompts/personalhub-timer-legacy-runtime-cleanup|personalhub-timer-legacy-runtime-cleanup]]

Riunisce la pulizia dei principali residui del vecchio MultiTimeTracker dentro Timer. Timer deve usare la vera versione di PersonalHub, riprovare correttamente le riparazioni automatiche fallite e smettere di chiedere una propria cartella/database di backup. Backup e ripristino del database passano dal sistema globale di PersonalHub.

## 6. [[prompts/personalhub-places-visit-history-checkin|personalhub-places-visit-history-checkin]]

Riunisce tre lavori che usano lo stesso storico Places, ormai costruito sopra la semantica definitiva delle visite. Se sei dentro più luoghi sovrapposti l'app deve chiedere quale scegliere; puoi aggiungere manualmente una visita passata; e con “Dov'ero?” puoi scegliere data/ora e vedere quale luogo risulta dallo storico o, se sei tra due visite, tra quali luoghi stavi presumibilmente spostandoti senza inventare una posizione.

## 7. [[prompts/personalhub-places-sorting-map-navigation|personalhub-places-sorting-map-navigation]]

Migliora lista e mappa Places: ordinamento per distanza, ultima visita, tempo totale o numero visite con ASC/DESC; mappa centrata sulla posizione attuale; tap su un marker che apre la scheda del luogo.

## 8. [[prompts/personalhub-places-geofence-alerts|personalhub-places-geofence-alerts]]

Aggiunge notifiche quando entri o esci da determinati Places. Devono sopravvivere a riavvii/aggiornamenti, rispettare i permessi Android e non produrre notifiche duplicate.

## 9. [[prompts/personalhub-autoexport-status-indicator|personalhub-autoexport-status-indicator]]

Aggiunge nella home un indicatore semplice dello stato del backup automatico: aggiornato/sano oppure non configurato, arretrato o in errore, con dettagli utili accessibili al tocco.

## 10. [[prompts/personalhub-global-screen-version-footer|personalhub-global-screen-version-footer]]

Uniforma il numero di versione in tutta PersonalHub. Ogni schermata completa di People, Timer, Places, Substances, Soldi e WordPulse mostra in piccolo, in basso a destra, la versione reale di PersonalHub. Se una vecchia app da cui deriva il modulo mostrava già una propria versione, quella scritta viene sostituita invece di lasciare due numeri diversi.

## 11. [[prompts/personalhub-dark-theme|personalhub-dark-theme]]

Aggiunge un vero tema scuro coerente a tutta PersonalHub, seguendo il tema Android e mantenendo leggibili schermate, dialog, campi, errori e barre di sistema di tutti i moduli.

## 12. [[prompts/personalhub-global-audit-foundation-safe-undo|personalhub-global-audit-foundation-safe-undo]]

Costruisce insieme il backend del Registro attività e l'annullamento sicuro. PersonalHub registra semanticamente le modifiche importanti a dati e impostazioni in modo comprensibile, senza segreti, e conserva abbastanza informazioni per tentare un annullamento. L'annullamento non cancella la storia: crea una modifica compensativa e viene rifiutato se nel frattempo lo stato è cambiato o ci sono conflitti. Operazioni multiple devono essere annullate tutte insieme oppure per niente.

## 13. [[prompts/personalhub-global-audit-register-ui|personalhub-global-audit-register-ui]]

Crea la parte visibile del Registro attività: card nella home, cronologia leggibile, filtri per modulo e pulsante di annullamento quando il backend stabilisce che l'operazione può essere invertita in sicurezza.
