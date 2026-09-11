[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=672541 | project_id=31 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT`

# Goal
Portare Uptime Kuma a uno stato operativo e sicuro in un solo task: (A) popolare l'indice MegaVault dal DB live di Uptime Kuma; (B) trovare e correggere la causa dei monitor `Fedora Host` e `Fedora Storage` rossi; (C) aggiungere copertura Kuma ai progetti attivi che hanno servizi Fedora associati quando il monitor produce un segnale stabile e utile; (D) mettere l'interfaccia e le API push di Uptime Kuma dietro HTTPS con Caddy, rimuovendo l'esposizione pubblica diretta della porta `3001` con backup e rollback verificati.

# Starting point verificato
- progetto primario MegaVault: `project_id=31` (`oracle-uptime-kuma`, runtime Oracle VM); progetto Fedora correlato già noto: `project_id=15` (`fedora-system-monitor`). Risolvi eventuali altri `project_id` solo da MegaVault;
- MegaVault possiede già l'indice operativo Kuma e i comandi `kuma-sync-sqlite`, `kuma-map`, `kuma-describe`, `kuma-finalize`, `kuma-index`;
- l'inventario Kuma non va dichiarato completo finché non è sincronizzato da un DB live/backup recente della vera istanza;
- evidenza utente del 2026-09-11: `Fedora Host` e `Fedora Storage` risultano rossi/0%; `Fedora Network` e `Fedora Services` risultano verdi e `Fedora Software` mostra attività prevalentemente verde. È solo un indizio iniziale: verifica lo stato live e non dedurre la causa dallo screenshot;
- l'UI è attualmente raggiunta via HTTP diretto sulla porta pubblica `3001`. L'obiettivo finale è accesso HTTPS con certificato pubblicamente trusted tramite Caddy, Kuma non esposto direttamente su Internet e push esistenti ancora funzionanti.

# A — Inventario Kuma live → MegaVault
Parti da MegaVault e dal progetto `31`; non fare discovery generale dei repository.

1. Individua sul runtime Oracle la vera istanza Uptime Kuma e il suo SQLite corrente usando i fatti/path già presenti in MegaVault e nel repo proprietario. Ottieni una snapshot consistente e recente in sola lettura per l'import; non copiare un DB in scrittura in modo non sicuro.
2. Esegui il percorso già implementato in MegaVault (`kuma-sync-sqlite`) sulla snapshot. Non salvare token push, credenziali, query segrete o URL completi sensibili.
3. Per ogni monitor corrente, associa uno o più `project_id` solo con evidenza concreta e scrivi una spiegazione breve di cosa controlla. Non indovinare associazioni mancanti.
4. Esegui `kuma-finalize` solo quando tutti i monitor correnti sono mappati e descritti. Se manca evidenza per un monitor, lascia l'inventario incompleto e riporta precisamente il blocker invece di forzare `COMPLETE`.

# B — Fedora Host / Fedora Storage rossi
Dopo avere identificato i monitor reali dal DB live, traccia il percorso end-to-end solo per `Fedora Host` e `Fedora Storage`: monitor Kuma → endpoint/push sanitizzato → script/probe Fedora → eventuale unit/timer systemd → check effettivo.

Per ciascuno determina la root cause verificando almeno: unit/timer attivo, ultimo run e exit code, journal pertinente, cadenza attesa vs ultimo heartbeat, eventuale errore del probe, mapping/configurazione del monitor e raggiungibilità del push. Non stampare secret o URL push completi.

Applica il fix minimo alla causa reale. Non cambiare soglie o disabilitare controlli solo per far diventare verde il monitor. Se il problema è nel probe, correggi il probe; se è scheduling/configurazione, correggi quello. Verifica il nuovo heartbeat/stato live per almeno due intervalli attesi quando pratico. Le barre storiche possono restare rosse: l'acceptance riguarda lo stato corrente e la ripresa dei heartbeat.

# C — Copertura dei progetti attivi con servizi Fedora
Usa MegaVault (`projects` + `services` + host Fedora) come inventario iniziale. Apri soltanto i repo dei candidati effettivi che richiedono verifica o modifica.

Per ogni progetto attivo con almeno un servizio/timer Fedora associato, aggiungi un monitor dedicato solo se tutte queste condizioni sono vere:
- il servizio rappresenta una funzione persistente o schedulata importante del progetto, non un processo dev/test/transient;
- esiste un segnale di salute/liveness stabile e poco costoso;
- il fallimento è azionabile e la cadenza attesa è definibile;
- non esiste già copertura Kuma equivalente che identifichi chiaramente quel progetto/failure domain.

Preferisci **un monitor per progetto o failure domain indipendente**, non un monitor per ogni unit. Per servizi Fedora non raggiungibili dall'Oracle VM, preferisci push/heartbeat locale; non aprire nuove porte di rete solo per Kuma. Riusa helper/pattern esistenti quando compatibili, senza creare un framework nuovo.

Per ogni monitor creato usa un nome riconoscibile e una descrizione che permettano di capire subito progetto e funzione. Dopo le creazioni, sincronizza di nuovo il DB live di Kuma in MegaVault, mappa i monitor ai `project_id`, aggiungi le spiegazioni e finalizza nuovamente l'inventario.

# D — HTTPS con Caddy + chiusura pubblica 3001
Questa fase è infrastruttura critica: lavora in `STRICT`, verifica live prima di ogni mutazione e mantieni una via di rollback funzionante fino alla verifica finale.

## Backup/preflight obbligatorio
Prima di installare o modificare Caddy, firewall, bind address o endpoint push:
- identifica il runtime reale di Kuma, il metodo di avvio e le regole firewall/network correnti;
- crea backup timestampati e verificabili almeno del DB/config Kuma, unit/container/config runtime pertinenti, configurazione firewall e qualunque configurazione reverse-proxy già presente;
- registra hash/path dei backup senza copiare segreti nei report;
- verifica che il DB backup sia leggibile e che i file di configurazione possano essere ripristinati;
- prepara una procedura/script di rollback idempotente che ripristini listener/config precedenti e accesso amministrativo se il cutover HTTPS fallisce.

## Caddy/TLS
- usa **Caddy** come reverse proxy autorevole verso Kuma su loopback/local network, mantenendo supporto WebSocket;
- usa un certificato **pubblicamente trusted** con rinnovo automatico. Riusa un hostname/DNS già disponibile se esiste; se l'ambiente corrente supporta in modo affidabile certificati pubblici per IP con Caddy/CA, è accettabile. Non usare certificati self-signed come soluzione finale;
- se serve una modifica DNS che Codex non può eseguire con accesso già autorizzato, fermati con blocker preciso indicando esclusivamente il record da creare; non indebolire TLS per aggirarlo;
- verifica configurazione con gli strumenti nativi di Caddy prima del reload/restart e non sostituire un reverse proxy già utile senza prima comprenderne lo scope;
- configura redirect HTTP→HTTPS se compatibile con il challenge/certificato scelto.

## Cutover sicuro dei push
Non chiudere `3001` finché i producer esistenti dipendono ancora da URL `http://...:3001/api/push/...`.

1. Porta HTTPS online e verifica UI/login, WebSocket e un endpoint `/api/push/` usando un monitor/test non distruttivo senza esporre token nei log.
2. Individua dai monitor live e dai repo/servizi già in scope tutti i producer che inviano push alla vecchia porta pubblica `3001`.
3. Migra gli endpoint dei producer al nuovo URL HTTPS canonico, preservando token e semantica del monitor; modifica solo i producer effettivamente necessari.
4. Verifica heartbeat reali sul nuovo endpoint per i monitor push coinvolti.
5. Solo dopo il PASS dei push, fai ascoltare Kuma soltanto sull'interfaccia necessaria al reverse proxy (preferibilmente loopback) e blocca l'accesso pubblico inbound alla `3001` sia nel firewall host sia, se applicabile e già gestibile con accesso autorizzato, nelle regole cloud Oracle. Non toccare SSH o altre porte non pertinenti.
6. Verifica dall'esterno che `443` funzioni con certificato valido e che `3001` non sia più raggiungibile pubblicamente; verifica localmente che Caddy continui a raggiungere Kuma.

## Rollback test
Prima di dichiarare PASS:
- prova realmente il rollback in modo controllato quando può essere fatto senza rischio/downtime significativo: ripristina la configurazione precedente, verifica che il percorso amministrativo precedente torni disponibile, quindi riapplica il nuovo stato HTTPS e ripeti i check finali;
- se un rollback reale completo produrrebbe un rischio ingiustificato, esegui almeno un rehearsal verificabile: restore dei backup in percorso temporaneo, validazione sintattica/semantica delle config ripristinate, verifica dei comandi firewall inversi e prova del ripristino del servizio in modalità isolata. Spiega perché il rollback live non è stato eseguito;
- il rollback non deve dipendere da memoria/chat: deve essere documentato in una fonte autorevole del progetto o in tooling operativo minimo, senza segreti.

Non modificare direttamente il SQLite live di Uptime Kuma se esiste un percorso amministrativo/tooling già supportato. Se l'unico modo praticabile richiede una mutazione raw del DB live o un'operazione distruttiva, crea prima un backup verificabile e procedi solo con una strategia transazionale/ripristinabile; altrimenti fermati con blocker.

# Verifiche / acceptance
- `python3 megavault.py operational-index-migrate` PASS;
- `python3 megavault.py operational-index-validate` PASS, non `PASS_WITH_WARNINGS` per inventario non sincronizzato;
- `python3 megavault.py kuma-index` mostra inventario live `COMPLETE`, almeno un monitor corrente, zero monitor correnti non mappati e zero spiegazioni mancanti;
- `Fedora Host` e `Fedora Storage`: root cause identificata, fix mirato applicato se risolvibile in scope, heartbeat recente e stato corrente UP verificati; se uno resta DOWN, il motivo deve essere reale e documentato, non mascherato;
- per ogni progetto attivo con servizi Fedora: monitor presente se utile secondo i criteri sopra, oppure esclusione motivata nel report finale; nessun duplicato inutile;
- per ogni nuovo monitor: mapping MegaVault a `project_id` + spiegazione presenti dopo il resync finale;
- HTTPS: browser/client standard valida il certificato senza eccezioni manuali; UI e WebSocket funzionano via `https://...`; HTTP viene rediretto o gestito solo quanto necessario per ACME;
- tutti i producer push migrati funzionano sul nuovo endpoint HTTPS prima della chiusura della vecchia esposizione;
- `3001` non è raggiungibile pubblicamente, ma Kuma resta raggiungibile da Caddy internamente;
- backup pre-cutover verificati e rollback procedure/rehearsal PASS; nessun segreto nei log/report;
- `python3 megavault.py validate` PASS dopo le modifiche MegaVault;
- test mirati dei repo modificati PASS; niente audit generale, refactor, cleanup o modifiche fuori scope.

# Discipline / stop
Riusa i fatti già presenti in MegaVault e nei repo proprietari; non riesplorare tutta l'organizzazione. Raggruppa query/check indipendenti, niente retry identici senza nuova evidenza. Non mostrare segreti. Commit/push separati solo per i repo realmente modificati e verifica una volta lo stato finale. Non chiudere `3001` prima di avere HTTPS e i push migrati/verificati. Quando acceptance è soddisfatta, aggiorna/archivia questo task secondo il README della roadmap e STOP.

Output finale conciso: `PROMPT_ID`, `RESULT`, stato inventario Kuma e numero monitor, root cause+fix di `Fedora Host`, root cause+fix di `Fedora Storage`, progetti Fedora candidati con esito `MONITORED`/`EXCLUDED` e motivo, nuovi monitor+project_id, URL HTTPS canonico (senza token), stato TLS/Caddy, stato esposizione `3001`, backup+rollback test, test, commit SHA per repo, blocker residui.
