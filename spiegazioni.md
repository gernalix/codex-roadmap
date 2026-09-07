# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Questo file spiega in parole semplici a cosa serve ciascun prompt ancora presente in `roadmap.md`. L'ordine deve corrispondere esattamente alla roadmap.

**Regola comune:** se Codex installa sul Pixel una copia clone/QA temporanea, deve rimuoverla prima del PASS. La verifica e consegna Telegram dell'APK finale non sono più un prompt: sono regole permanenti del bootstrap PersonalHub remoto in MegaVault.

## 1. [[prompts/personalhub-timer-event-title-success-toast|personalhub-timer-event-title-success-toast]]

Il codice è stato ricontrollato e questo bug è ancora presente. Dentro Timer, dopo un successo, il ViewModel usa ancora un messaggio generico; dal widget Android il codice mostra ancora `Event recorded` oppure il numero di elementi creati dalla macro. Il prompt cambia solo questo feedback: toccando `Coffee` deve apparire `Coffee added`, sia nell'app sia dal widget; una macro deve mostrare il proprio titolo e non un conteggio. Il resto di Events non viene riaperto.

## 2. [[prompts/personalhub-substances-prescription-date-pickers|personalhub-substances-prescription-date-pickers]]

Una parte richiesta esiste già: quando crei una prescrizione nuova, entrambe le date vengono già salvate con la data odierna. Il problema rimanente è la UI: nella modifica compaiono ancora `Order epoch day` e `Prescription epoch day` come numeri tecnici. Il prompt è stato ristretto a sostituire quei campi con normali calendari e a mostrare date leggibili, senza cambiare database o logica già corretta.

## 3. [[prompts/personalhub-context-composer-redesign|personalhub-context-composer-redesign]]

È ancora necessario. Il motore Hub Context e i relativi adapter esistono già, ma la home PersonalHub non ha una sezione Composer e l'editor sessione Timer contiene ancora `SessionContextEditor` e `HubContextLinks`. Il prompt riusa il motore esistente, toglie l'interfaccia Context dal dialogo Timer e crea una schermata principale dedicata con tempo/luogo suggeriti, poche proposte pertinenti, ricerca, rilevazione dei dati avvenuti nell'intervallo scelto e Context retroattivi.

## 4. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]]

PersonalHub è già più avanti di quanto descriveva la vecchia versione del prompt: il database è alla versione 10, esistono gli snapshot 1–10 e sono registrate migrazioni fino alla 10. Mancano però due protezioni importanti: una verifica reale che la catena di migrazioni sia completa (oggi `canMigrateFrom` presume semplicemente che tutte le versioni da 1 a 10 vadano bene) e un vero gate al primo avvio dopo l'aggiornamento, prima che i moduli inizino a scrivere. Il prompt ora lavora solo su queste parti mancanti e sui test automatici di tutte le versioni storiche.

## 5. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]]

Il controllo del codice conferma che i tre difetti sono ancora presenti: il pulsante del riquadro chiamata usa ancora un intent implicito, una ricerca contatto lenta può ancora terminare dopo `dismiss()` e mostrare un overlay vecchio, e il log di successo contiene ancora il numero di telefono completo. Il prompt resta quindi separato e molto localizzato.

## 6. [[prompts/personalhub-global-ui-theme-version-backup-status|personalhub-global-ui-theme-version-backup-status]]

Anche qui alcune basi esistono già. La home mostra già correttamente la versione PersonalHub e `DatabaseVault` espone già tutti i dati necessari per sapere se l'auto-export è sano; non serve modificare il sistema di backup. Restano da aggiungere il piccolo indicatore ✅/❌ sulla home, la versione PersonalHub su tutte le vere schermate dei moduli e il dark mode. Il tema host è infatti ancora solo chiaro e Substances mostra ancora una propria versione `BuildConfig`, che va sostituita con quella dell'app principale. I tre lavori restano accorpati perché usano la stessa lista di schermate e lo stesso giro finale di QA.

## 7. [[prompts/personalhub-global-activity-register-safe-undo|personalhub-global-activity-register-safe-undo]]

Esistono già registri parziali specifici, per esempio l'audit di Timer e lo storico/audit di Places, ma non esiste ancora un registro globale né una card `Registro attività` nella home. Il prompt riusa o collega ciò che è già disponibile invece di creare doppioni, poi costruisce un'unica cronologia leggibile e paginata, filtri, gruppi di modifiche e annullamento sicuro che rifiuta conflitti e registra a sua volta l'operazione di ripristino.
