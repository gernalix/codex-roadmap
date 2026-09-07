# Codex Roadmap

[[README|README]] · [[spiegazioni|Spiegazioni]]

Ordine consigliato di esecuzione, riesaminato end-to-end sullo stato corrente di `PersonalHub/main`, sul dump Codex del 2026-09-05 e sull'audit statico dello stesso giorno. Eseguire **un solo task Codex alla volta** sullo stesso progetto secondo il workflow del README, salvo i blocchi esplicitamente marcati come continuous campaign.

Stato già acquisito e da NON reimplementare nei task futuri: database PH unificato; Settings/Database & Backup integrati; sync Datasette local-first; Places API key/address suggestions; Places storico/check-in manuale e retroattivo, `Dov'ero?`, sort metriche/mappa e geofence Android opzionale con notifiche/dedupe; shortcut pinnabili e percorso diretto ai moduli; protezione dell'app reale dai benchmark/test distruttivi; auto-export SAF generation-based con WorkManager/recovery/error state; hardening del Database Vault con import marker atomico/fail-safe e rollback SAF verificato; Soldi integrato con account, saldi, prodotto canonico e Git exchange; policy delete/FK Places↔Soldi corretta; Timer Alerts passati su `PersonalHub/main` a prompt in-app centrati e immediati con link/deep link cliccabili; capsulizzazione dei moduli completata; Hub Context Graph generico disponibile per People, Timer, Places, Soldi, Substances, WordPulse e Resources, con navigazione all'entità esatta, risoluzione batch, ricerca Timer/Places bounded e Context Type di sistema bloccati; widget configurabile Timer `Events` implementato e archiviato; manutenzione Timer rimanente completata con picker Events scrollabile/cercabile, Quick Session a risultato reale, tag sessione a chip/creazione esatta e cleanup runtime/backup.

Finding tecnici/funzionali ancora pendenti: il toast di successo dopo un tap sui pulsanti Timer `Events` usa wording generico come `Event recorded` invece di `<titolo pulsante> added`, e deve essere coerente tra tap in-app e widget; Substances → Prescriptions espone ancora i campi `orderEpochDay` e `prescriptionEpochDay` come valori tecnici epoch-day invece di normali date selezionabili da calendario; UI Composer v29 embedded/nested in Timer giudicata inutilizzabile e da sostituire con una sezione top-level dedicata; People call-overlay deep-link/race/PII. Dettagli storici: `audits/2026-09-05-personalhub-main-audit.md`.

La readiness Telegram per la consegna dell'APK finale **non è più un goal separato della roadmap**: è una regola operativa permanente del corrente `MegaVault/ai/personalhubdoc.md` remoto. Il bootstrap governa sia il preflight una tantum del notifier condiviso sia la consegna finale dell'APK; i prompt applicativi non devono duplicare quel lavoro.

## Ordine pendente

La roadmap contiene ora **7 goal sostanziali**. I fix Timer e Substances vengono prima perché sono interventi FAST molto localizzati e non conviene trascinarli nei goal cross-module successivi. L'accorpamento del resto resta basato sul costo Codex reale: stesso modulo/modello, file e dominio condivisi, possibilità di riusare esplorazione e test, un solo incremento versione e soprattutto una sola build/installazione/QA finale per goal.

1. [[prompts/personalhub-timer-event-title-success-toast|personalhub-timer-event-title-success-toast]] — **GPT-5.5 / low / FAST**
2. [[prompts/personalhub-substances-prescription-date-pickers|personalhub-substances-prescription-date-pickers]] — **GPT-5.5 / low / FAST**
3. [[prompts/personalhub-context-composer-redesign|personalhub-context-composer-redesign]] — **GPT-5.6 Sol / medium / STRICT**
4. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]] — **GPT-5.6 Sol / medium / STRICT**
5. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]] — **GPT-5.5 / medium / FAST** · alternativa 5.6: **GPT-5.6 Sol / medium**
6. [[prompts/personalhub-global-ui-theme-version-backup-status|personalhub-global-ui-theme-version-backup-status]] — **GPT-5.5 / medium / STANDARD** · alternativa 5.6: **GPT-5.6 Terra / medium**
7. [[prompts/personalhub-global-activity-register-safe-undo|personalhub-global-activity-register-safe-undo]] — **GPT-5.6 Sol / medium / STRICT**

## Cosa è stato accorpato e perché

- **Timer: goal principale completato; nuovo fix puntuale separato.** Il widget `Events` e la manutenzione Timer precedente sono già archiviati. La nuova richiesta riguarda solo il feedback dopo il tap: un successo deve mostrare `<titolo del pulsante tappato> added` sia dentro l'app sia dal widget, invece di `Event recorded` o conteggi generici. Poiché il goal Timer precedente è già PASS, non viene riaperto né duplicato; il fix ha un prompt autonomo, stretto e FAST.
- **Substances Prescriptions: date picker separato e localizzato.** I due valori data esistono già nel modello; il difetto è l'input tecnico epoch-day nella UI. Il goal mantiene la rappresentazione persistita compatibile e sostituisce solo l'interazione con selettori calendario, default odierno e conversione locale testata.
- **UI globale: 3 → 1.** indicatore auto-export, footer versione e dark theme richiedevano tutti di percorrere shell e moduli. Il goal costruisce una sola inventory delle schermate e la riusa per footer e tema, verificando anche il nuovo indicatore nello stesso passaggio.
- **Registro attività: 2 → 1.** backend audit/undo e UI erano due metà della stessa feature. Il read model viene ora progettato una volta per paging, filtri, grouping e undo, evitando che una seconda sessione debba riscoprire l'API appena creata.

## Perché i tre restanti non sono stati accorpati ulteriormente

- `personalhub-context-composer-redesign.md` è già un goal molto grande e cross-module. Fonderlo con altro trascinerebbe un contesto enorme nelle fasi successive.
- `personalhub-database-schema-upgrade-safety.md` è infrastruttura DB ad alto rischio e richiede test di migrazione storica dedicati. Unirlo a una feature UI renderebbe diagnosi/rollback più difficili e costringerebbe quella feature a pagare il costo STRICT del lavoro DB.
- `personalhub-people-call-overlay-hardening.md` è un fix telephony/overlay/race/PII molto localizzato: non condivide abbastanza file o QA con i goal globali per giustificare il contesto aggiuntivo.

## Dipendenze / motivazione dell'ordine

- Il fix Timer `Events` viene per primo perché è un bug UX molto localizzato, con starting files già pre-localizzati e costo GPT-5.5/low/FAST; chiuderlo subito evita di trascinarlo dentro i goal più ampi successivi.
- Il fix Substances Prescriptions segue perché è anch'esso localizzato: elimina l'input epoch-day e prova una volta la conversione calendario locale senza trascinarla nei goal cross-module.
- `personalhub-context-composer-redesign.md` resta separato e prima della sicurezza schema perché può introdurre/assestare gli ultimi contratti Hub Context da consolidare.
- `personalhub-database-schema-upgrade-safety.md` viene quindi eseguito sullo schema risultante dai goal funzionali precedenti e rende obbligatoria una catena di migrazione completa per i bump futuri.
- People call-overlay resta un fix indipendente e localizzato.
- Il goal UI globale viene dopo le principali modifiche funzionali, così footer/tema/status vengono applicati alle schermate definitive una sola volta.
- Il Registro attività resta ultimo: è il goal più cross-module e può appoggiarsi sia al framework definitivo di migrazione DB sia alle superfici/moduli ormai stabilizzati.

## Disciplina globale

Ogni prompt deve restare self-contained e verificare esplicitamente eventuali prerequisiti; fuori da un blocco continuo non deve assumere una chat precedente. Per i task PersonalHub, il bootstrap specializzato autorevole è il **corrente `MegaVault/ai/personalhubdoc.md` remoto**; MegaVault e codex-roadmap devono essere consultati dalle rispettive sorgenti remote correnti e non da checkout locali. Il protocollo globale va letto solo nei casi di fallback esplicitamente previsti da quel file. Nei blocchi continui esplicitamente marcati, le fasi successive possono riusare esclusivamente il contesto verificato nelle fasi precedenti della stessa sessione, senza rilanciare bootstrap/esplorazione equivalenti.

Quando un prompt modifica PersonalHub, deve catturare la versione iniziale una sola volta e fissare per quel goal `target = base + 1`. Nei prompt consolidati le fasi interne condividono lo stesso target: retry, rebuild, test o fasi successive dello stesso goal non possono incrementarlo di nuovo.

**Cleanup app-clone su Pixel:** se durante il testing Codex installa sul Pixel un'app clone/QA separata dall'app PersonalHub reale, quell'app temporanea deve essere disinstallata dal Pixel prima di chiudere il task con `PASS`. La verifica del cleanup fa parte dell'acceptance finale; non lasciare package clone di test installati sul dispositivo.

**Ordine solo numerico in roadmap:** l'ordine canonico è esclusivamente la posizione `1.`, `2.`, `3.`, ... in questa lista. I filename/titoli dei prompt devono essere semantici e non devono contenere prefissi o suffissi numerici/alfanumerici d'ordine. Inserire, rimuovere o riordinare un task richiede solo di rinumerare consecutivamente la lista; non si rinominano i file per la posizione. `PROMPT_ID` resta consentito perché è un identificatore casuale, non un indicatore d'ordine.

**Pre-localizzazione obbligatoria:** ogni prompt pendente deve indicare un set iniziale di file/classi reali verificati sullo stato corrente del repository target, sufficiente a iniziare il task senza scansione generale. Nei prompt consolidati è preferibile una pre-localizzazione per fase: Codex legge i file della fase solo quando vi entra, invece di caricare subito l'intera unione. Se un task precedente ha rinominato/spostato un file indicato, il prompt può autorizzare una singola ricerca mirata per il simbolo/classe noto. La disciplina operativa dettagliata su esplorazione, batching, tool call, retry, device QA, test, Git e stop resta definita dal bootstrap MegaVault governante e non va duplicata nei prompt.

Le fasi interne e i task successivi non devono riaprire l'architettura già verificata salvo che un acceptance check dimostri una regressione o un prerequisito mancante.
