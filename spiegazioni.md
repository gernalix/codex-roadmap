# Spiegazioni della roadmap

[[README]] · [[roadmap]]

Questo file serve a capire **cosa farà Codex e perché**, senza dover conoscere programmazione, Android o Linux.

I dettagli tecnici sono volutamente lasciati nei singoli prompt. Qui trovi solo il risultato pratico di ogni lavoro.

## In che ordine vanno fatti

### Prima di tutto

Il primo lavoro, **Registro degli ID dei prompt**, va eseguito per primo e da solo. Mette in funzione il sistema che impedisce di assegnare per errore lo stesso numero a due prompt diversi.

### PersonalHub

I lavori di PersonalHub vanno fatti uno dopo l'altro, mai due contemporaneamente:

**Profili → Date e ore → Salute: dati → Salute: schermate → Obsidian: base → Obsidian: aggiornamenti automatici → Obsidian: tutti i moduli → Cronologia e ripristino → Esploratore dati offline → Controllo finale Google Play**

Il lavoro **Datasette PersonalHub online** è separato e può essere fatto mentre avanzano i primi lavori di PersonalHub, ma deve essere concluso prima di **Esploratore dati offline**.

### Altri lavori

- **Velocizzare il salvataggio dei dati Codex**: è indipendente, ma conviene eseguirlo da solo perché deve misurare con precisione la velocità prima e dopo.
- **Backup ActivityWatch su GitHub**: è indipendente da PersonalHub.
- **Controllo monitor Fedora**: è indipendente da PersonalHub, ma richiede che tu abbia già effettuato il login a Uptime Kuma.
- **Backup ActivityWatch su GitHub** e **Controllo monitor Fedora** non vanno eseguiti contemporaneamente, perché entrambi lavorano sul sistema di monitoraggio.
- **Aggiornamento automatico Logseq** va eseguito per ultimo e da solo, perché comprende anche una delicata pulizia della vecchia cronologia del progetto.

## I lavori in parole semplici

| # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/megavault-prompt-id-registry-activation]] | **Registro degli ID dei prompt.** Mette in funzione il registro che impedisce il riuso degli ID. Recupera gli ID storici dalle fonti durevoli (roadmap/history e archivio `codex-usage`) e usa eventuali vecchi archivi locali solo se ancora presenti, quindi un path legacy sparito non blocca più l'attivazione. Serve Codex solo per migrare e verificare il `megavault.sqlite` reale sul Fedora. | medium | Prompt |
| 2 | [[prompts/codex-usage-publisher-noop-fastpath-deploy]] | **Velocizzare il salvataggio dei dati Codex.** Installa sul tuo PC la modifica che evita di ricontrollare centinaia di vecchie conversazioni quando non è cambiato nulla. Poi esegue due prove consecutive per verificare che la seconda finisca molto più rapidamente. Serve Codex perché la modifica deve essere installata e misurata sul tuo Fedora reale. | low | Prompt |
| 3 | [[prompts/activity-watch-uploader-runtime-deploy]] | **Backup automatico di ActivityWatch.** Fa sì che tutta la cronologia raccolta da ActivityWatch venga salvata automaticamente in un archivio privato su GitHub, in un formato che ChatGPT possa leggere facilmente. Configura anche un controllo che ti avvisi se questo salvataggio smette di funzionare. Serve Codex perché deve configurare sia il tuo PC Fedora sia il tuo sistema di monitoraggio remoto. | medium | Prompt |
| 4 | [[prompts/personalhub-global-profiles-timer-demotion]] | **Profili separati in PersonalHub.** Completa la possibilità di avere più profili, per esempio uno personale e uno di prova, senza che i dati di uno finiscano nell'altro. Controlla anche che notifiche, Timer, Places e altre funzioni seguano sempre il profilo giusto. Infine elimina dal Timer alcune funzioni duplicate che ormai appartengono a PersonalHub nel suo insieme. Serve Codex perché deve costruire e provare realmente l'app Android. | medium | Prompt |
| 5 | [[prompts/personalhub-epoch-timestamps-migration]] | **Date e ore coerenti ovunque.** Controlla tutti i dati di PersonalHub e lascia intatti quelli già corretti. Corregge solo eventuali vecchie date salvate in un formato diverso e fa mostrare le date nello stesso modo in tutta l'app, per esempio “ven 18/9/26 14:30”. Serve Codex perché deve verificare i dati reali dell'app e assicurarsi che nessuna data venga persa o cambiata per errore. | medium | Prompt |
| 6 | [[prompts/personalhub-salute-canonical-integration]] | **Portare Salute dentro PersonalHub.** Sposta la base del modulo Salute nell'archivio dati principale di PersonalHub, invece di tenerla separata. Prepara anche il modo sicuro con cui ChatGPT potrà aggiungere o aggiornare informazioni sanitarie in futuro. In questa fase non cambia ancora ciò che vedi sullo schermo. Serve Codex perché è una modifica delicata ai dati dell'app. | medium | Prompt |
| 7 | [[prompts/personalhub-salute-ui-hub-obsidian]] | **Rendere Salute visibile e collegata al resto dell'app.** Dopo il lavoro precedente, fa usare davvero a PersonalHub i dati Salute interni. Aggiunge una schermata semplice per consultarli e li rende trovabili insieme agli altri moduli nelle funzioni generali di ricerca, cronologia e consultazione. La schermata Salute resta di sola lettura. Serve Codex perché deve collegare e provare diverse parti dell'app Android. | medium | Prompt |
| 8 | [[prompts/personalhub-obsidian-archive-foundation]] | **Prima versione dell'archivio Obsidian.** Aggiunge una funzione opzionale che crea da PersonalHub una cartella leggibile con Obsidian. PersonalHub continua a essere la fonte principale dei dati: Obsidian serve solo per consultarli comodamente. La funzione parte disattivata e inizialmente permette di ricreare manualmente tutto l'archivio. Serve Codex perché deve integrare questa funzione nell'app e provarla con i file reali di Android. | medium | Prompt |
| 9 | [[prompts/personalhub-obsidian-archive-incremental]] | **Aggiornare Obsidian automaticamente.** Dopo aver creato l'archivio Obsidian, fa sì che PersonalHub aggiorni soltanto ciò che è cambiato invece di ricreare tutto ogni volta. Deve continuare a funzionare anche se il telefono o l'app si interrompono a metà. Serve Codex perché deve provare questi aggiornamenti e i casi di interruzione sul sistema Android reale. | medium | Prompt |
| 10 | [[prompts/personalhub-obsidian-archive-projections]] | **Completare Obsidian per tutti i moduli.** Estende l'archivio Obsidian a People, Places, Timer, Soldi, Salute e agli altri moduli mantenuti. L'obiettivo è ottenere note leggibili, collegate tra loro e senza creare una quantità ingestibile di file. Serve Codex perché deve verificare il risultato nell'app e su un dispositivo Android di prova. | medium | Prompt |
| 11 | [[prompts/datasette5-personalhub-explorer-security-deploy]] | **Versione online dell'esploratore dati di PersonalHub.** Mette in funzione sul tuo computer remoto una pagina privata con cui puoi consultare i dati PersonalHub e passare facilmente da un elemento collegato a un altro. Deve essere possibile leggere e cercare, ma non modificare i dati. Serve Codex perché deve installare e provare questo sistema sul computer remoto reale. | medium | Prompt |
| 12 | [[prompts/personalhub-git-history-data-sync-validation]] | **Cronologia, backup e ripristino dei dati PersonalHub.** Controlla con particolare attenzione il sistema che permette di vedere come i dati sono cambiati nel tempo e di tornare a una situazione precedente, per un singolo elemento o per tutto l'archivio. Deve dimostrare che un ripristino non può danneggiare o perdere i dati attuali. Serve Codex perché sono necessarie prove reali e controllate su copie dei dati dell'app. | medium | Prompt |
| 13 | [[prompts/personalhub-datasette-lite-offline-runtime]] | **Esploratore dati direttamente dentro PersonalHub, anche senza Internet.** Completa la schermata che permette di consultare tutti i dati e i collegamenti fra moduli direttamente sul telefono. Deve funzionare offline, essere leggibile su uno schermo piccolo e offrire gli stessi collegamenti utili della versione online. Alla fine prepara anche la versione 51 di PersonalHub. Serve Codex perché deve costruire l'app e provarla su Android. | medium | Prompt |
| 14 | [[prompts/personalhub-play-release-local-validation]] | **Controllo finale prima di Google Play.** Non pubblica nulla. Crea il pacchetto finale dell'app una sola volta e controlla firma, versione, permessi richiesti e compatibilità. Poi installa una copia derivata dallo stesso pacchetto su un telefono Android virtuale e verifica che le schermate principali si aprano senza problemi. Serve Codex perché richiede gli strumenti Android installati sul tuo PC. | low | Prompt |
| 15 | [[prompts/fedora-runtime-validation]] | **Ultimo controllo del monitoraggio Fedora.** Dopo che hai effettuato il login a Uptime Kuma, verifica soltanto che i due controlli Fedora abbiano le impostazioni corrette, compreso il comportamento speciale del controllo dello spazio su disco. Non reinstalla nulla e non ripete lavori già conclusi. Serve Codex perché deve usare la sessione e la configurazione presenti sul tuo PC. | low | Prompt |
| 16 | [[prompts/logseq-updates-pat-safety-closure]] | **Pulizia di sicurezza e aggiornamenti automatici di Logseq.** Elimina dalla vecchia cronologia del progetto una chiave di accesso GitHub che non deve più essere presente. Poi sostituisce il vecchio aggiornamento pensato per Windows con uno adatto a Fedora: trova automaticamente la nuova versione di Logseq, la installa in sicurezza e ti manda un messaggio Telegram quando riesce o quando qualcosa va storto. Serve Codex perché deve lavorare sulla cronologia reale del progetto, sul tuo Logseq installato e sui servizi del tuo PC. | medium | Prompt |

## Cosa non trovi qui

Non vengono elencati lavori che ChatGPT può già completare direttamente senza Codex. Questa roadmap deve contenere soltanto attività che hanno davvero bisogno del tuo PC, di Android, del computer remoto o di altre risorse locali.

I singoli prompt contengono intenzionalmente tutti i dettagli tecnici necessari a Codex. **Non è necessario capirli per usare questa pagina.**
