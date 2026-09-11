# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, nello stesso ordine della roadmap, una spiegazione semplice di ciò che farà ogni prompt.

## 1. [[prompts/github-autosync-fedora-migration|github-autosync-fedora-migration]]

Sposta definitivamente sul Fedora l'autosync dei repository nel nuovo repo dedicato `github-autosync`. Codex clonerà o sincronizzerà il nuovo repo locale, spegnerà il vecchio timer che partiva da `codex-usage-monitor`, installerà il nuovo service/timer ogni 5 minuti e verificherà che non possano esistere due autosync concorrenti. La prima esecuzione controllerà anche che il nuovo repo sia registrato una sola volta in MegaVault.

## 2. [[prompts/codex-roadmap-worktree-sync-hardening|codex-roadmap-worktree-sync-hardening]]

Rende più sicuro e veloce il modo in cui Codex apre e chiude i task. Una modifica locale non dovrà più costringerlo a creare stash solo per leggere la roadmap, un prompt ad-hoc non potrà più essere scambiato per un diverso prompt pendente, e un commit non dovrà inglobare automaticamente modifiche che erano già presenti prima del task.

## 3. [[prompts/megavault-event-cli-scoped-validation|megavault-event-cli-scoped-validation]]

Aggiunge a MegaVault un modo stabile per registrare gli eventi senza far riscoprire ogni volta a Codex colonne SQLite, esempi e INSERT manuali. Introduce anche una verifica limitata al progetto o evento appena modificato, così errori globali preesistenti e non collegati non bloccheranno inutilmente un task valido.

## 4. [[prompts/personalhub-telegram-file-delivery-cli|personalhub-telegram-file-delivery-cli]]

Semplifica l’ultimo passo dei task PersonalHub: Codex potrà inviare l’APK su Telegram con un solo comando file-only, senza provare argomenti vuoti, leggere il codice interno del notifier o usare Python inline. Il comportamento Telegram già esistente resterà compatibile.

## 5. [[prompts/personalhub-widget-qa-harness|personalhub-widget-qa-harness]]

Rende molto più semplice testare i widget di PersonalHub. Invece di far perdere tempo a Codex ogni volta con comandi ADB, dati di prova creati a mano e tentativi poco affidabili per leggere i toast, crea un percorso di test unico e riutilizzabile che prepara i dati, simula i tap e verifica successo o errore in modo stabile.

## 6. [[prompts/personalhub-adb-device-preflight|personalhub-adb-device-preflight]]

Aggiunge un controllo iniziale unico per capire subito quali dispositivi Android sono disponibili. Codex saprà se può usare Pixel, TCL o emulatore, tenterà solo recuperi ADB sicuri e limitati e non perderà più tempo a riscoprire ogni volta quale device è collegato o se deve avviare l’emulatore.

## 7. [[prompts/personalhub-substances-prescription-date-pickers|personalhub-substances-prescription-date-pickers]]

Nelle prescrizioni di Substances non dovrai più inserire le date come numeri incomprensibili. Potrai sceglierle da un normale calendario e le vedrai scritte in modo leggibile. Quando crei una prescrizione, le date continueranno a partire da oggi. Inoltre, quando tocchi un pulsante configurato in Substances, l’azione verrà registrata anche se lo stock della sostanza è pari a zero.

## 8. [[prompts/personalhub-context-composer-redesign|personalhub-context-composer-redesign]]

Aggiunge alla schermata principale un Composer per collegare facilmente ciò che stavi facendo, il luogo, le persone e altri dati di PersonalHub. L’app proporrà automaticamente gli elementi più probabili, ma potrai sempre cambiarli. La creazione e modifica delle sessioni di Timer tornerà più semplice perché questi collegamenti non saranno più inseriti direttamente lì.

## 9. [[prompts/personalhub-temporal-context-search|personalhub-temporal-context-search]]

Aggiunge alla Home una funzione Cerca basata sul tempo. Scegli una data e ora di inizio e una di fine e PersonalHub raccoglie in un’unica schermata tutto ciò che è successo in quell’intervallo nei vari moduli, ordinandolo nel tempo. È come ricostruire automaticamente il contesto di quel periodo, ma senza creare collegamenti permanenti tra i dati.

## 10. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]]

Protegge i tuoi dati quando installi una nuova versione di PersonalHub. Prima di usare il vecchio archivio, l’app controllerà che possa essere aggiornato senza rischi. Se trova un problema, si fermerà senza cancellare o sostituire i dati.

## 11. [[prompts/personalhub-random-timer-time-perception|personalhub-random-timer-time-perception]]

Aggiunge alla Home Random timer. Premi Avvia e parte un timer di durata casuale che non puoi vedere. Quando finisce ricevi una notifica che ti chiede quanto tempo pensi sia passato. Solo dopo aver inserito la tua risposta PersonalHub mostra il tempo reale, confronta tempo percepito e tempo reale e salva entrambi per poter misurare nel tempo la tua percezione del passare dei minuti.

## 12. [[prompts/personalhub-timer-substances-random-alerts|personalhub-timer-substances-random-alerts]]

Ogni pulsante Events di Timer e ogni pulsante configurato di Substances potrà avere i propri Random alerts. Per ogni pulsante scegli se attivarli e quanti riceverne ogni ora o ogni giorno; gli orari vengono scelti casualmente. Un unico interruttore generale può sospendere tutti i Random alerts senza perdere le impostazioni dei singoli pulsanti, che tornano come prima quando li riattivi.

## 13. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]]

Corregge tre problemi del riquadro che appare durante le chiamate: il pulsante per aprire un contatto, la possibile ricomparsa di un riquadro appartenente a una chiamata già finita e la presenza del numero di telefono nei registri tecnici. Il funzionamento generale delle chiamate non verrà ridisegnato.

## 14. [[prompts/personalhub-global-ui-theme-version-backup-status|personalhub-global-ui-theme-version-backup-status]]

Rende l’aspetto di PersonalHub più coerente. La schermata principale mostrerà subito se il salvataggio automatico dei dati funziona, tutte le sezioni mostreranno la stessa versione dell’app e il tema chiaro o scuro seguirà correttamente quello del telefono.

## 15. [[prompts/personalhub-global-activity-register-safe-undo|personalhub-global-activity-register-safe-undo]]

Aggiunge un unico Registro attività in cui vedere le modifiche fatte nelle varie sezioni di PersonalHub. Potrai cercarle e filtrarle e, quando è sicuro, annullare un’azione. Se nel frattempo i dati sono cambiati e l’annullamento potrebbe creare problemi, l’app lo impedirà.
