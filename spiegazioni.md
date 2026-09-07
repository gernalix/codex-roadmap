# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Questo file spiega in parole semplici a cosa serve ciascun prompt ancora presente in `roadmap.md`. L'ordine deve corrispondere esattamente alla roadmap.

**Regola comune:** se Codex installa sul Pixel una copia clone/QA temporanea, deve rimuoverla prima del PASS. La verifica e consegna Telegram dell'APK finale non sono più un prompt: sono regole permanenti del bootstrap PersonalHub remoto in MegaVault.

## 1. [[prompts/fedora-github-autosync-completion-guard-hardening|fedora-github-autosync-completion-guard-hardening]]

Corregge quattro difetti rimasti nel sistema Git automatico appena installato. Oggi il controllo che parte quando Codex finisce guarda soprattutto la cartella da cui è stata aperta la sessione: se Codex lavora su più repository, può quindi non accorgersi che uno di essi è rimasto con modifiche non salvate o commit non pubblicati. Inoltre il publisher ripassa inutilmente tutte le vecchie sessioni ogni minuto, il ramo che registra nuovi repository in MegaVault non è ancora abbastanza fail-safe se ghorg fallisce, e un report che dice chiaramente `RESULT=PASS` può finire nello storico come `UNKNOWN`. Il fix userà i repository realmente toccati dai comandi della sessione, controllerà soltanto le nuove completion, renderà la registrazione MegaVault fail-fast e sistemerà PASS/BLOCKED/FAIL. I test useranno solo repository e database temporanei, senza toccare `megavault.sqlite` reale.

## 2. [[prompts/personalhub-places-history-mutation-overlap-regression|personalhub-places-history-mutation-overlap-regression]]

Corregge una regressione introdotta dall'ultimo lavoro su Places. Oggi, se nello storico esiste già anche una sola visita sovrapposta a un'altra, il codice può considerare “in conflitto” l'intero archivio e rifiutare anche operazioni nuove completamente valide: check-in, check-out, visita retroattiva o modifica di un orario. Il fix non cancellerà né correggerà automaticamente i vecchi dati: farà in modo che una modifica venga rifiutata soltanto quando è quella modifica a creare o peggiorare un conflitto. Il bug non era emerso nei test perché i test automatici partivano ogni volta da un database vuoto e lo smoke fisico sul TCL controllava soltanto schermate di lettura, senza eseguire nessuna vera modifica. Questa volta Codex deve anche riprodurre lo storico già “sporco” e provare le operazioni reali su Pixel usando dati QA isolati.

## 3. [[prompts/personalhub-timer-event-title-success-toast|personalhub-timer-event-title-success-toast]]

Il codice è stato ricontrollato e questo bug è ancora presente. Dentro Timer, dopo un successo, il ViewModel usa ancora un messaggio generico; dal widget Android il codice mostra ancora `Event recorded` oppure il numero di elementi creati dalla macro. Il prompt cambia solo questo feedback: toccando `Coffee` deve apparire `Coffee added`, sia nell'app sia dal widget; una macro deve mostrare il proprio titolo e non un conteggio. Il resto di Events non viene riaperto.

## 4. [[prompts/personalhub-substances-prescription-date-pickers|personalhub-substances-prescription-date-pickers]]

Una parte richiesta esiste già: quando crei una prescrizione nuova, entrambe le date vengono già salvate con la data odierna. Il problema rimanente è la UI: nella modifica compaiono ancora `Order epoch day` e `Prescription epoch day` come numeri tecnici. Il prompt è stato ristretto a sostituire quei campi con normali calendari e a mostrare date leggibili, senza cambiare database o logica già corretta.

## 5. [[prompts/personalhub-context-composer-redesign|personalhub-context-composer-redesign]]

È ancora necessario, ma una parte sostanziale del motore esiste già: lo stato Composer sa già salvare e ripristinare membri e ricerca, cercare tramite gli adapter, creare entità/risorse, salvare Context e gestire template; esiste anche un test che prova crea → salva → riapri → aggiungi un'altra entità. Il problema è soprattutto come tutto questo viene presentato: oggi è ancora un dialogo tecnico incastrato nel flusso Timer, con tipi interni poco leggibili, e la home non ha una vera schermata Composer. Il prompt ora riusa e rifattorizza queste basi invece di ricostruirle, aggiungendo inferenza di tempo/luogo, suggerimenti limitati e rilevazione dei dati già registrati nell'intervallo scelto.

## 6. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]]

PersonalHub è già più avanti di quanto descriveva la vecchia versione del prompt: il database è alla versione 10, esistono gli snapshot 1–10 e sono registrate migrazioni fino alla 10. Mancano però due protezioni importanti: una verifica reale che la catena di migrazioni sia completa (oggi `canMigrateFrom` presume semplicemente che tutte le versioni da 1 a 10 vadano bene) e un vero gate al primo avvio dopo l'aggiornamento, prima che i moduli inizino a scrivere. Il prompt ora lavora solo su queste parti mancanti e sui test automatici di tutte le versioni storiche.

## 7. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]]

Il controllo del codice conferma che i tre difetti sono ancora presenti: il pulsante del riquadro chiamata usa ancora un intent implicito, una ricerca contatto lenta può ancora terminare dopo `dismiss()` e mostrare un overlay vecchio, e il log di successo contiene ancora il numero di telefono completo. Il prompt resta quindi separato e molto localizzato.

## 8. [[prompts/personalhub-global-ui-theme-version-backup-status|personalhub-global-ui-theme-version-backup-status]]

Anche qui molte basi esistono già. La home mostra già correttamente la versione PersonalHub e `DatabaseVault` espone già tutti i dati necessari per sapere se l'auto-export è sano; non serve modificare il sistema di backup. Inoltre People, Places, Substances e WordPulse seguono già il tema scuro di sistema. Restano il piccolo indicatore ✅/❌ sulla home, la versione PersonalHub su tutte le vere schermate dei moduli e i soli buchi di dark mode ancora reali: il tema principale di PersonalHub è light-only, Timer possiede già colori scuri ma non li seleziona automaticamente e Soldi usa ancora un tema generico. Substances e Timer mostrano inoltre ancora versioni proprie da sostituire con quella dell'app principale. I tre lavori restano accorpati perché usano la stessa lista di schermate e lo stesso giro finale di QA.

## 9. [[prompts/personalhub-global-activity-register-safe-undo|personalhub-global-activity-register-safe-undo]]

Esistono già registri parziali specifici, per esempio l'audit di Timer e lo storico/audit di Places, ma non esiste ancora un registro globale né una card `Registro attività` nella home. Il prompt riusa o collega ciò che è già disponibile invece di creare doppioni, poi costruisce un'unica cronologia leggibile e paginata, filtri, gruppi di modifiche e annullamento sicuro che rifiuta conflitti e registra a sua volta l'operazione di ripristino.
