# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Questo file spiega in parole semplici a cosa serve ciascun prompt ancora presente in `roadmap.md`. È pensato per essere comprensibile anche senza conoscenze di programmazione.

**L'ordine e la numerazione qui sotto devono corrispondere esattamente a `roadmap.md`.** La roadmap è stata accorpata per ridurre sessioni Codex, esplorazioni ripetute, build/installazioni e passaggi di test duplicati: i task strettamente correlati sono ora fasi dello stesso goal.

**Regola di test comune:** se Codex installa sul Pixel una copia clone/QA di PersonalHub solo per fare test senza rischiare i dati dell'app reale, deve disinstallare quella copia temporanea prima di dichiarare il task completato.

La verifica e la consegna Telegram dell'APK finale non sono più un prompt della roadmap: sono regole permanenti del bootstrap PersonalHub in MegaVault.

## 1. [[prompts/personalhub-timer-event-title-success-toast|personalhub-timer-event-title-success-toast]]

Corregge il messaggio che compare quando tocchi un pulsante `Events` di Timer. Invece del generico `Event recorded`, dopo un inserimento riuscito deve comparire `<titolo del pulsante> added`: per esempio, toccando `Coffee` deve apparire `Coffee added`. La regola deve essere identica sia quando tocchi il pulsante dentro PersonalHub sia quando usi il relativo widget sulla home Android. Anche i pulsanti-macro devono mostrare il proprio titolo, non un conteggio generico. Il messaggio di successo deve apparire solo se il salvataggio è realmente riuscito.

## 2. [[prompts/personalhub-substances-prescription-date-pickers|personalhub-substances-prescription-date-pickers]]

Sostituisce i due campi data tecnici delle prescrizioni di Substances con normali selettori calendario. Quando crei una nuova prescrizione, sia la data dell'ordine sia la data della prescrizione partono da oggi; quando ne modifichi una esistente, mostrano invece le date già salvate. Non devi più vedere né digitare numeri `epoch-day`, e il salvataggio deve mantenere la stessa data scelta senza slittamenti dovuti al fuso orario.

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
