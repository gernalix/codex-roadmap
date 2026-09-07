# Codex Roadmap

[[README|README]] · [[spiegazioni|Spiegazioni]]

Eseguire **un solo task Codex alla volta** sullo stesso progetto. Per PersonalHub, MegaVault e codex-roadmap si consultano soltanto dalle rispettive sorgenti remote correnti secondo `MegaVault/ai/personalhubdoc.md`.

La readiness e la consegna Telegram dell'APK finale **non sono più un goal della roadmap**: preflight riutilizzabile, destinazione, invio documento e gestione dei blocker sono regole permanenti del bootstrap PersonalHub remoto. Il vecchio prompt Telegram è stato eliminato.

## Audit codice remoto corrente

Il riesame di `PersonalHub/main` mostra che nessuno dei 7 goal rimasti è già interamente completato, ma diverse parti sono già presenti e i prompt sono stati ristretti per non rifarle:

- **Timer Events:** ancora pendente. Il ViewModel in-app usa ancora feedback generico (`showEntryRecorded` / `showMacroRecorded`) e il widget usa ancora `quick_event_recorded` o il conteggio macro. Il prompt parte direttamente da questi call-site; niente nuovo audit Timer.
- **Substances Prescriptions:** il default a oggi per entrambe le date di una nuova prescrizione è **già implementato**. Restano i campi tecnici `Order epoch day` / `Prescription epoch day` nell'editor: il prompt ora modifica soltanto la UI calendario e preserva la persistenza epoch-day esistente.
- **Composer:** il motore, `HubComposerState`, ricerca adapter-backed, template/resource creation e test base create-save-reopen esistono già, ma l'UI resta un dialogo embedded e `SessionEditDialog` contiene ancora Context; la home non ha Composer top-level. Il prompt riusa/refactorizza queste basi invece di ricostruirle.
- **Database upgrade safety:** Room/`SCHEMA_VERSION` è già **10**, gli snapshot **1..10** esistono e la produzione registra migrazioni fino a 10. Restano un vero migration-graph check, un gate fail-safe al primo avvio dopo update e test automatici di tutte le versioni storiche. `DatabaseVault` validation/rollback esistente va riusato.
- **People call overlay:** tutti e tre i difetti risultano ancora presenti: intent contatto implicito, lookup asincrono non invalidato da dismiss/nuova chiamata, numero completo nel log INFO.
- **UI globale:** la home mostra già il `versionName` host e `DatabaseVault.autoExportStatus()` espone già tutti i dati del badge. People, Places, Substances e WordPulse seguono già il dark mode di sistema; Timer ha già palette light/dark ma default light, Soldi usa ancora un `MaterialTheme` generico e il tema host è light-only. Restano quindi badge UI, versione host su tutti i moduli/rimozione versioni feature, e solo i boundary dark-mode realmente mancanti.
- **Registro attività:** esistono audit locali di Timer e Places, ma non un journal globale né una destinazione `Registro attività` nella home. Il prompt deve riusare/collegare questi meccanismi ed evitare doppio logging.

## Ordine pendente

1. [[prompts/personalhub-timer-event-title-success-toast|personalhub-timer-event-title-success-toast]] — **GPT-5.5 / low / FAST**
2. [[prompts/personalhub-substances-prescription-date-pickers|personalhub-substances-prescription-date-pickers]] — **GPT-5.5 / low / FAST**
3. [[prompts/personalhub-context-composer-redesign|personalhub-context-composer-redesign]] — **GPT-5.6 Sol / medium / STRICT**
4. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]] — **GPT-5.6 Sol / medium / STRICT**
5. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]] — **GPT-5.5 / medium / FAST**
6. [[prompts/personalhub-global-ui-theme-version-backup-status|personalhub-global-ui-theme-version-backup-status]] — **GPT-5.5 / medium / STANDARD**
7. [[prompts/personalhub-global-activity-register-safe-undo|personalhub-global-activity-register-safe-undo]] — **GPT-5.6 Sol / medium / STRICT**

## Accorpamento e costo Codex

L'accorpamento utile è già al limite corretto:

- **Timer** e **Substances** restano separati: sono due fix FAST in moduli diversi, senza esplorazione/test condivisibili; unirli trascinerebbe contesto inutile.
- **Composer** resta separato: è già un goal cross-module grande e architetturale. Aggiungere altro aumenterebbe reasoning, tool-call e rischio.
- **Database safety** resta separato: è infrastruttura dati ad alto rischio e deve avere migration/rollback QA dedicato.
- **People overlay** resta separato: è un fix telephony/window/race/PII pre-localizzato e non condivide superfici con gli altri task.
- **UI globale** è già l'accorpamento ottimale di badge auto-export + versione canonica + light/dark: condividono la stessa inventory di schermate e un solo giro finale di QA.
- **Registro attività** è già accorpato end-to-end (capture + read model + undo + UI) perché sono parti della stessa feature e devono condividere lo stesso modello; dividerlo obbligherebbe a riscoprire API e schema.

Non creare ulteriori mega-task contenenti obiettivi indipendenti. L'ottimizzazione successiva deve avvenire **dentro i prompt**: partire dai call-site/file verificati qui, preservare ciò che è già implementato, test mirati, una sola build/installazione finale e stop immediato al PASS.

## Dipendenze / ordine

- Timer e Substances vengono prima perché sono fix localizzati e chiudibili con GPT-5.5/low.
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
