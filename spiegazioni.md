# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Questo file spiega in parole semplici a cosa serve ciascun prompt ancora presente in `roadmap.md`. È pensato per essere comprensibile anche senza conoscenze di programmazione.

**L'ordine e la numerazione qui sotto devono corrispondere esattamente a `roadmap.md`.** La roadmap è stata accorpata per ridurre sessioni Codex, esplorazioni ripetute, build/installazioni e passaggi di test duplicati: i task strettamente correlati sono ora fasi dello stesso goal.

**Regola di test comune:** se Codex installa sul Pixel una copia clone/QA di PersonalHub solo per fare test senza rischiare i dati dell'app reale, deve disinstallare quella copia temporanea prima di dichiarare il task completato.

## 1. [[prompts/personalhub-telegram-apk-channel-delivery-readiness|personalhub-telegram-apk-channel-delivery-readiness]]

Verifica prima di tutto che il sistema Telegram condiviso usato da Codex possa davvero inviare l'APK alla **stessa destinazione predefinita che in passato veniva usata per le notifiche Codex di progresso/stato**, senza usare né inventare un altro chat ID. Le notifiche Telegram di progresso, test e installazione di PersonalHub restano disabilitate: quella destinazione viene riusata soltanto per consegnare l'APK finale. Deve usare il notifier comune a tutti i progetti, non quello specifico di `amici_fb`. Oltre a un normale messaggio di prova, controlla anche ciò che servirà davvero a PersonalHub: inviare un file come documento, scegliendone il nome e senza aggiungere caption o altro testo. Se qualcosa non funziona, Codex prova a correggere soltanto il notifier condiviso o la sua configurazione; se invece manca un permesso che puoi concedere solo tu, si ferma spiegando esattamente cosa serve. Questo test evita di scoprire il problema solo alla fine di un futuro task, quando l'APK sarebbe già pronto.

## 2. [[prompts/personalhub-timer-event-title-success-toast|personalhub-timer-event-title-success-toast]]

Corregge il messaggio che compare quando tocchi un pulsante `Events` di Timer. Invece del generico `Event recorded`, dopo un inserimento riuscito deve comparire `<titolo del pulsante> added`: per esempio, toccando `Coffee` deve apparire `Coffee added`. La regola deve essere identica sia quando tocchi il pulsante dentro PersonalHub sia quando usi il relativo widget sulla home Android. Anche i pulsanti-macro devono mostrare il proprio titolo, non un conteggio generico. Il messaggio di successo deve apparire solo se il salvataggio è realmente riuscito.

## 3. [[prompts/personalhub-context-composer-redesign|personalhub-context-composer-redesign]]

Sostituisce l'attuale interfaccia Context incastrata dentro “Nuova sessione” di Timer con una sezione principale di PersonalHub chiamata per ora `Composer`. Il normale editor Timer torna semplice. Composer prova invece a precompilare tempo/sessione e luogo, propone poche persone o altre entità plausibili in base allo storico e rileva automaticamente transazioni, assunzioni e WordSession avvenute nel periodo scelto. Tempo e luogo restano modificabili per creare Context retroattivi, mentre ricerca, template ed Explorer rimangono disponibili senza riempire la schermata principale di liste e dettagli tecnici.

## 4. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]]

Rende sicuri gli aggiornamenti dell'app rispetto ai dati già presenti. Al primo avvio di una nuova versione, PersonalHub controlla il database ereditato: se è compatibile lo valida, se è più vecchio lo migra senza perdere dati e ricontrolla il risultato, mentre se è troppo nuovo, manca una migrazione o la migrazione fallisce rifiuta di sovrascrivere i dati. Aggiunge anche test automatici che obbligano ogni futura modifica dello schema ad avere una catena completa di migrazioni dalle versioni storiche supportate.

## 5. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]]

Rende affidabile il riquadro che People mostra durante una telefonata: il pulsante deve aprire esplicitamente la persona corretta dentro PersonalHub, una ricerca lenta non deve far apparire il riquadro dopo che la chiamata è già finita né sovrascrivere una chiamata più recente, e i log tecnici non devono contenere il numero di telefono completo.

## 6. [[prompts/personalhub-global-ui-theme-version-backup-status|personalhub-global-ui-theme-version-backup-status]]

Riunisce tre lavori che richiedevano tutti di attraversare le schermate di PersonalHub. Aggiunge nella home l'indicatore ✅/❌ dello stato del backup automatico con dettagli al tocco; mostra in basso a destra su ogni vera schermata di People, Timer, Places, Substances, Soldi e WordPulse una sola versione, quella reale di PersonalHub, eliminando le vecchie versioni delle app originarie; infine applica un tema scuro coerente seguendo il tema Android. Codex costruisce una sola lista delle schermate e la riusa per versione e dark mode, facendo un'unica navigazione finale invece di tre audit UI separati.

## 7. [[prompts/personalhub-global-activity-register-safe-undo|personalhub-global-activity-register-safe-undo]]

Costruisce il Registro attività completo in un solo goal, dal database alla schermata finale. PersonalHub registra in modo comprensibile le modifiche importanti fatte nei vari moduli e nelle impostazioni, senza salvare segreti; conserva abbastanza informazioni per annullare in sicurezza le operazioni reversibili senza cancellare la storia e rifiuta l'annullamento se nel frattempo i dati sono cambiati o ci sono conflitti. La stessa infrastruttura alimenta direttamente la card `Registro attività`, la cronologia paginata, i gruppi di modifiche, i filtri per modulo e il pulsante di annullamento con spiegazioni leggibili quando non è più possibile tornare indietro.
