# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, nello stesso ordine della roadmap, una spiegazione semplice di ciò che farà ogni prompt.

## 1. [[prompts/fedora-codex-usage-runtime-isolation-finalization|fedora-codex-usage-runtime-isolation-finalization]]

Rende più sicuro il sistema che registra quanto Codex viene usato. Impedisce che parta mentre Codex lo sta ancora modificando, evita di ripubblicare per errore centinaia di vecchi risultati e riduce i falsi allarmi. Non cambia PersonalHub.

## 2. [[prompts/personalhub-timer-event-title-success-toast|personalhub-timer-event-title-success-toast]]

Quando tocchi un pulsante nella sezione Events di Timer, il messaggio di conferma dirà chiaramente che cosa è stato aggiunto. Per esempio, toccando “Coffee” comparirà “Coffee added”. Funzionerà allo stesso modo sia dentro l’app sia dal widget.

## 3. [[prompts/personalhub-substances-prescription-date-pickers|personalhub-substances-prescription-date-pickers]]

Nelle prescrizioni di Substances non dovrai più inserire le date come numeri incomprensibili. Potrai sceglierle da un normale calendario e le vedrai scritte in modo leggibile. Quando crei una prescrizione, le date continueranno a partire da oggi.

## 4. [[prompts/personalhub-context-composer-redesign|personalhub-context-composer-redesign]]

Aggiunge alla schermata principale un Composer per collegare facilmente ciò che stavi facendo, il luogo, le persone e altri dati di PersonalHub. L’app proporrà automaticamente gli elementi più probabili, ma potrai sempre cambiarli. La creazione e modifica delle sessioni di Timer tornerà più semplice perché questi collegamenti non saranno più inseriti direttamente lì.

## 5. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]]

Protegge i tuoi dati quando installi una nuova versione di PersonalHub. Prima di usare il vecchio archivio, l’app controllerà che possa essere aggiornato senza rischi. Se trova un problema, si fermerà senza cancellare o sostituire i dati.

## 6. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]]

Corregge tre problemi del riquadro che appare durante le chiamate: il pulsante per aprire un contatto, la possibile ricomparsa di un riquadro appartenente a una chiamata già finita e la presenza del numero di telefono nei registri tecnici. Il funzionamento generale delle chiamate non verrà ridisegnato.

## 7. [[prompts/personalhub-global-ui-theme-version-backup-status|personalhub-global-ui-theme-version-backup-status]]

Rende l’aspetto di PersonalHub più coerente. La schermata principale mostrerà subito se il salvataggio automatico dei dati funziona, tutte le sezioni mostreranno la stessa versione dell’app e il tema chiaro o scuro seguirà correttamente quello del telefono.

## 8. [[prompts/personalhub-global-activity-register-safe-undo|personalhub-global-activity-register-safe-undo]]

Aggiunge un unico Registro attività in cui vedere le modifiche fatte nelle varie sezioni di PersonalHub. Potrai cercarle e filtrarle e, quando è sicuro, annullare un’azione. Se nel frattempo i dati sono cambiati e l’annullamento potrebbe creare problemi, l’app lo impedirà.
