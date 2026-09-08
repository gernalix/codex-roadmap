# Codex Roadmap

[[README|README]] · [[spiegazioni|Spiegazioni]]

Eseguire **un solo task Codex alla volta** sullo stesso progetto. Per PersonalHub, MegaVault e codex-roadmap si consultano soltanto dalle rispettive sorgenti remote correnti secondo `MegaVault/ai/personalhubdoc.md`.

La readiness e la consegna Telegram dell'APK finale **non sono più un goal della roadmap**: preflight riutilizzabile, destinazione, invio documento e gestione dei blocker sono regole permanenti del bootstrap PersonalHub remoto. Il vecchio prompt Telegram è stato eliminato.

## Audit codice remoto corrente

Il riesame mostra 8 goal PersonalHub pendenti e 1 fix infrastrutturale Fedora prioritario. Le parti già implementate restano incorporate nei prompt per evitare riesplorazione:

- **Codex usage publisher — runtime isolation/finalizzazione:** i fix precedenti hanno ridotto il costo Codex e corretto single-pass, status e gran parte del guard, ma il service systemd esegue ancora direttamente il Python dal worktree modificabile. Durante l'ultimo hardening questo ha permesso al timer live di eseguire patch intermedie e `codex-usage` ha prodotto due republish da 502 cicli. Restano inoltre il return code di `git status`, la distinzione robusta fra upstream assente/errore e i falsi allarmi su repo usati solo come workdir. Il nuovo prompt ferma il timer prima degli edit, introduce release runtime atomiche per commit, migrazione fingerprint versionata senza backfill e write-evidence separata dai semplici workdir.
- **Places history mutations — regressione prioritaria:** il commit Places `45edd082fe8323478cf7826cabe845129be57ad3` ha reso globale il controllo overlap. `PlaceRepository.validateNewEvents(...)` e `validateEventReplacement(...)` possono rifiutare una nuova modifica valida quando `HistorySessionCalculator.hasAnyOverlap(...)` trova una sovrapposizione preesistente e non correlata in qualunque punto dello storico. Questo spiega il blocco di check-in/out, visite retroattive e modifica orari sul DB reale. Il precedente test Robolectric ricreava un DB pulito per ogni test; il precedente smoke fisico usava TCL-6102H ma verificava solo sort, `Where was I?` e assenza crash, senza eseguire mutazioni. Il nuovo prompt riproduce uno storico già sovrapposto, corregge la validazione incrementale e richiede uno smoke di mutazione su Pixel con dati QA isolati.
- **Timer Events:** ancora pendente. Il ViewModel in-app usa feedback generico (`showEntryRecorded` / `showMacroRecorded`) e il widget usa ancora `quick_event_recorded` o il conteggio macro. Il prompt parte direttamente da questi call-site; niente nuovo audit Timer.
- **Substances Prescriptions:** il default a oggi per entrambe le date di una nuova prescrizione è **già implementato**. Restano i campi tecnici `Order epoch day` / `Prescription epoch day` nell'editor: il prompt modifica soltanto la UI calendario e preserva la persistenza epoch-day esistente.
- **Composer:** il motore, `HubComposerState`, ricerca adapter-backed, template/resource creation e test base create-save-reopen esistono già, ma l'UI resta un dialogo embedded e `SessionEditDialog` contiene ancora Context; la home non ha Composer top-level. Il prompt riusa/refactorizza queste basi invece di ricostruirle.
- **Database upgrade safety:** Room/`SCHEMA_VERSION` è già **10**, gli snapshot **1..10** esistono e la produzione registra migrazioni fino a 10. Restano un vero migration-graph check, un gate fail-safe al primo avvio dopo update e test automatici di tutte le versioni storiche. `DatabaseVault` validation/rollback esistente va riusato.
- **People call overlay:** tutti e tre i difetti risultano ancora presenti: intent contatto implicito, lookup asincrono non invalidato da dismiss/nuova chiamata, numero completo nel log INFO.
- **UI globale:** la home mostra già il `versionName` host e `DatabaseVault.autoExportStatus()` espone già tutti i dati del badge. People, Places, Substances e WordPulse seguono già il dark mode di sistema; Timer ha già palette light/dark ma default light, Soldi usa ancora un `MaterialTheme` generico e il tema host è light-only. Restano badge UI, versione host sui moduli/rimozione versioni feature e i soli boundary dark-mode realmente mancanti.
- **Registro attività:** esistono audit locali di Timer e Places, ma non un journal globale né una destinazione `Registro attività` nella home. Il prompt deve riusare/collegare questi meccanismi ed evitare doppio logging.

## Ordine pendente

1. [[prompts/fedora-codex-usage-runtime-isolation-finalization|fedora-codex-usage-runtime-isolation-finalization]] — **GPT-5.5 / low / FAST**
2. [[prompts/personalhub-places-history-mutation-overlap-regression|personalhub-places-history-mutation-overlap-regression]] — **GPT-5.5 / low / FAST**
3. [[prompts/personalhub-timer-event-title-success-toast|personalhub-timer-event-title-success-toast]] — **GPT-5.5 / low / FAST**
4. [[prompts/personalhub-substances-prescription-date-pickers|personalhub-substances-prescription-date-pickers]] — **GPT-5.5 / low / FAST**
5. [[prompts/personalhub-context-composer-redesign|personalhub-context-composer-redesign]] — **GPT-5.6 Sol / medium / STRICT**
6. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]] — **GPT-5.6 Sol / medium / STRICT**
7. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]] — **GPT-5.5 / medium / FAST**
8. [[prompts/personalhub-global-ui-theme-version-backup-status|personalhub-global-ui-theme-version-backup-status]] — **GPT-5.5 / medium / STANDARD**
9. [[prompts/personalhub-global-activity-register-safe-undo|personalhub-global-activity-register-safe-undo]] — **GPT-5.6 Sol / medium / STRICT**

## Accorpamento e costo Codex

L'accorpamento utile resta al limite corretto:

- **Codex usage runtime isolation/finalizzazione** resta autonomo e primo: lavora solo sul publisher/systemd appena modificato e impedisce che ulteriori task eseguano codice intermedio live o generino churn storico; i call-site sono già pre-localizzati.
- **Places regression** resta autonoma e prima degli altri goal PersonalHub: è un malfunzionamento dei write-path fondamentali già pre-localizzato, da correggere senza trascinare altro lavoro Places già completato.
- **Timer** e **Substances** restano separati: sono fix FAST in moduli diversi, senza esplorazione/test condivisibili.
- **Composer** resta separato: è già un goal cross-module grande e architetturale.
- **Database safety** resta separato: è infrastruttura dati ad alto rischio e richiede migration/rollback QA dedicato.
- **People overlay** resta separato: è un fix telephony/window/race/PII pre-localizzato.
- **UI globale** è già l'accorpamento ottimale di badge auto-export + versione canonica + light/dark perché condividono la stessa inventory e un solo QA finale.
- **Registro attività** è già accorpato end-to-end (capture + read model + undo + UI); dividerlo imporrebbe di riscoprire API e schema.

Non creare ulteriori mega-task contenenti obiettivi indipendenti. Ottimizzare dentro i prompt: partire dai call-site verificati, preservare ciò che esiste, usare test mirati, una sola build/installazione finale e stop immediato al PASS.

## Dipendenze / ordine

- Il fix Fedora viene **prima di tutto** perché separa il runtime live dal worktree e chiude i difetti del guard/fingerprint prima delle sessioni successive; è un task FAST pre-localizzato.
- Places viene subito dopo perché il modulo non riesce attualmente a eseguire normali mutazioni di storico sui dati reali; la causa è già localizzata ed è un fix FAST.
- Timer e Substances seguono perché sono fix localizzati e chiudibili con GPT-5.5/low.
- Composer viene prima della sicurezza schema perché può introdurre gli ultimi contratti/identità Hub Context da consolidare.
- Database safety segue sullo schema risultante e diventa il guardrail per i bump successivi.
- People resta indipendente.
- UI globale viene dopo le principali modifiche funzionali, così inventaria e rifinisce schermate definitive una volta sola.
- Registro attività resta ultimo: è il goal più cross-module e può appoggiarsi al framework migrazioni definitivo e alle superfici ormai stabilizzate.

## Disciplina permanente della roadmap

- Ogni prompt è self-contained e non dipende da chat precedenti; riusa invece i fatti verificati incorporati nel prompt.
- Per PersonalHub il bootstrap autorevole è il **corrente `MegaVault/ai/personalhubdoc.md` remoto**; non consultare checkout locali di MegaVault/codex-roadmap.
- Un goal che modifica PersonalHub legge la versione iniziale una volta e usa `target = base + 1` una sola volta; retry/rebuild/test non incrementano di nuovo.
- Se viene installato sul Pixel un clone/QA temporaneo, va disinstallato prima del PASS.
- Ordine canonico = sola posizione numerica in questo file; i filename restano semantici, senza prefissi/suffissi d'ordine.
- Ogni prompt deve partire da file/simboli pre-localizzati e ampliare l'indagine solo se una dipendenza concreta lo richiede.
- Dopo acceptance PASS: nessuna esplorazione/audit facoltativo; eseguire solo le operazioni terminali obbligatorie del bootstrap.
