# Codex Roadmap

[[README|README]] · [[spiegazioni|Spiegazioni]]

Ordine consigliato di esecuzione, riesaminato end-to-end sullo stato corrente di `PersonalHub/main`, sul dump Codex del 2026-09-05 e sull'audit statico dello stesso giorno. Eseguire **un solo task Codex alla volta** sullo stesso progetto secondo il workflow del README, salvo i blocchi esplicitamente marcati come continuous campaign.

Stato già acquisito e da NON reimplementare nei task futuri: database PH unificato; Settings/Database & Backup integrati; sync Datasette local-first; Places API key/address suggestions; shortcut pinnabili e percorso diretto ai moduli; protezione dell'app reale dai benchmark/test distruttivi; auto-export SAF generation-based con WorkManager/recovery/error state; hardening del Database Vault con import marker atomico/fail-safe e rollback SAF verificato; Soldi integrato con account, saldi, prodotto canonico e Git exchange; policy delete/FK Places↔Soldi corretta; Timer Alerts passati su `PersonalHub/main` a prompt in-app centrati e immediati con link/deep link cliccabili; capsulizzazione dei moduli completata; Hub Context Graph generico disponibile per People, Timer, Places, Soldi, Substances, WordPulse e Resources, con navigazione all'entità esatta, risoluzione batch, ricerca Timer/Places bounded e Context Type di sistema bloccati; widget configurabile Timer `Events` implementato e archiviato; manutenzione Timer rimanente completata con picker Events scrollabile/cercabile, Quick Session a risultato reale, tag sessione a chip/creazione esatta e cleanup runtime/backup.

Finding tecnici/funzionali ancora pendenti: Places non espone ancora il flusso manuale completo di check-in immediato + retroattivo; UI Composer v29 embedded/nested in Timer giudicata inutilizzabile e da sostituire con una sezione top-level dedicata; People call-overlay deep-link/race/PII. Dettagli storici: `audits/2026-09-05-personalhub-main-audit.md`.

## Ordine pendente

La roadmap è stata consolidata da **15 a 6 goal sostanziali**. L'accorpamento è basato sul costo Codex reale: stesso modulo/modello, file e dominio condivisi, possibilità di riusare esplorazione e test, un solo incremento versione e soprattutto una sola build/installazione/QA finale per goal. I task rimasti separati lo sono perché unirli trascinerebbe contesto non pertinente o un rischio/modello più costoso senza sufficiente riuso.

1. [[prompts/personalhub-places-history-map-geofencing|personalhub-places-history-map-geofencing]] — **GPT-5.5 / medium / STANDARD** · alternativa 5.6: **GPT-5.6 Sol / medium**
2. [[prompts/personalhub-context-composer-redesign|personalhub-context-composer-redesign]] — **GPT-5.6 Sol / medium / STRICT**
3. [[prompts/personalhub-database-schema-upgrade-safety|personalhub-database-schema-upgrade-safety]] — **GPT-5.6 Sol / medium / STRICT**
4. [[prompts/personalhub-people-call-overlay-hardening|personalhub-people-call-overlay-hardening]] — **GPT-5.5 / medium / FAST** · alternativa 5.6: **GPT-5.6 Sol / medium**
5. [[prompts/personalhub-global-ui-theme-version-backup-status|personalhub-global-ui-theme-version-backup-status]] — **GPT-5.5 / medium / STANDARD** · alternativa 5.6: **GPT-5.6 Terra / medium**
6. [[prompts/personalhub-global-activity-register-safe-undo|personalhub-global-activity-register-safe-undo]] — **GPT-5.6 Sol / medium / STRICT**

## Cosa è stato accorpato e perché

- **Places: 3 → 1.** visite/check-in/`Dov'ero?`, sorting+mappa e geofence condividono `PlaceRepository`, location, Place detail, metriche e navigazione. La fase visite definisce la semantica canonica riusata dalle altre fasi; il geofencing resta opzionale e battery-efficient tramite Android `GeofencingClient`, mai GPS continuo. Per ogni Place può operare come sola notifica oppure, se esplicitamente configurato, tradurre ENTER/EXIT nel medesimo check-in/check-out canonico, con protezioni contro duplicati e ambiguità; **ogni check-in/out automatico riuscito genera sempre anche una notifica utente deduplicata**. L'intera capability dipendente da background location deve restare isolata e degradare senza rompere Places quando il permesso manca o una futura variante Play non la include. Un solo passaggio finale verifica l'intero modulo.
- **Timer: goal completato.** Il widget `Events` e la manutenzione Timer rimanente sono stati archiviati; i task ancora pendenti partono da Places.
- **UI globale: 3 → 1.** indicatore auto-export, footer versione e dark theme richiedevano tutti di percorrere shell e moduli. Il goal costruisce una sola inventory delle schermate e la riusa per footer e tema, verificando anche il nuovo indicatore nello stesso passaggio.
- **Registro attività: 2 → 1.** backend audit/undo e UI erano due metà della stessa feature. Il read model viene ora progettato una volta per paging, filtri, grouping e undo, evitando che una seconda sessione debba riscoprire l'API appena creata.

## Perché i tre restanti non sono stati accorpati ulteriormente

- `personalhub-context-composer-redesign.md` è già un goal molto grande e cross-module. Fonderlo con altro trascinerebbe un contesto enorme nelle fasi successive.
- `personalhub-database-schema-upgrade-safety.md` è infrastruttura DB ad alto rischio e richiede test di migrazione storica dedicati. Unirlo a una feature UI renderebbe diagnosi/rollback più difficili e costringerebbe quella feature a pagare il costo STRICT del lavoro DB.
- `personalhub-people-call-overlay-hardening.md` è un fix telephony/overlay/race/PII molto localizzato: non condivide abbastanza file o QA con i goal globali per giustificare il contesto aggiuntivo.

## Dipendenze / motivazione dell'ordine

- Il goal Places viene subito dopo. Include anche l'eventuale schema necessario alla configurazione geofence/automazione, così il successivo framework di sicurezza delle migrazioni può validare lo schema risultante invece di essere immediatamente seguito da un'altra modifica DB non ancora coperta. La parte background-location resta opzionale e separabile dalla funzionalità core di Places.
- `personalhub-context-composer-redesign.md` resta separato e prima della sicurezza schema perché può introdurre/assestare gli ultimi contratti Hub Context da consolidare.
- `personalhub-database-schema-upgrade-safety.md` viene quindi eseguito sullo schema risultante da Timer/Places/Composer e rende obbligatoria una catena di migrazione completa per i bump futuri.
- People call-overlay resta un fix indipendente e localizzato.
- Il goal UI globale viene dopo le principali modifiche funzionali, così footer/tema/status vengono applicati alle schermate definitive una sola volta.
- Il Registro attività resta ultimo: è il goal più cross-module e può appoggiarsi sia al framework definitivo di migrazione DB sia alle superfici/moduli ormai stabilizzati.

## Disciplina globale

Ogni prompt deve restare self-contained e verificare esplicitamente eventuali prerequisiti; fuori da un blocco continuo non deve assumere una chat precedente. Per i task PersonalHub, il bootstrap specializzato autorevole è `MegaVault/ai/personalhubdoc.md`; il protocollo globale va letto solo nei casi di fallback esplicitamente previsti da quel file. Nei blocchi continui esplicitamente marcati, le fasi successive possono riusare esclusivamente il contesto verificato nelle fasi precedenti della stessa sessione, senza rilanciare bootstrap/esplorazione equivalenti.

Quando un prompt modifica PersonalHub, deve catturare la versione iniziale una sola volta e fissare per quel goal `target = base + 1`. Nei prompt consolidati le fasi interne condividono lo stesso target: retry, rebuild, test o fasi successive dello stesso goal non possono incrementarlo di nuovo.

**Cleanup app-clone su Pixel:** se durante il testing Codex installa sul Pixel un'app clone/QA separata dall'app PersonalHub reale, quell'app temporanea deve essere disinstallata dal Pixel prima di chiudere il task con `PASS`. La verifica del cleanup fa parte dell'acceptance finale; non lasciare package clone di test installati sul dispositivo.

**Ordine solo numerico in roadmap:** l'ordine canonico è esclusivamente la posizione `1.`, `2.`, `3.`, ... in questa lista. I filename/titoli dei prompt devono essere semantici e non devono contenere prefissi o suffissi numerici/alfanumerici d'ordine. Inserire, rimuovere o riordinare un task richiede solo di rinumerare consecutivamente la lista; non si rinominano i file per la posizione. `PROMPT_ID` resta consentito perché è un identificatore casuale, non un indicatore d'ordine.

**Pre-localizzazione obbligatoria:** ogni prompt pendente deve indicare un set iniziale di file/classi reali verificati sullo stato corrente del repository target, sufficiente a iniziare il task senza scansione generale. Nei prompt consolidati è preferibile una pre-localizzazione per fase: Codex legge i file della fase solo quando vi entra, invece di caricare subito l'intera unione. Se un task precedente ha rinominato/spostato un file indicato, il prompt può autorizzare una singola ricerca mirata per il simbolo/classe noto. La disciplina operativa dettagliata su esplorazione, batching, tool call, retry, device QA, test, Git e stop resta definita dal bootstrap MegaVault governante e non va duplicata nei prompt.

Le fasi interne e i task successivi non devono riaprire l'architettura già verificata salvo che un acceptance check dimostri una regressione o un prerequisito mancante.
