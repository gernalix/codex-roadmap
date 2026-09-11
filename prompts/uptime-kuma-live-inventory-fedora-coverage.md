[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=672541 | project_id=31 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Portare Uptime Kuma a uno stato operativo coerente in un solo task: (A) popolare l'indice MegaVault dal DB live di Uptime Kuma; (B) trovare e correggere la causa dei monitor `Fedora Host` e `Fedora Storage` rossi; (C) aggiungere copertura Kuma ai progetti attivi che hanno servizi Fedora associati quando il monitor produce un segnale stabile e utile.

# Starting point verificato
- progetto primario MegaVault: `project_id=31` (`oracle-uptime-kuma`, runtime Oracle VM); progetto Fedora correlato già noto: `project_id=15` (`fedora-system-monitor`). Risolvi eventuali altri `project_id` solo da MegaVault;
- MegaVault possiede già l'indice operativo Kuma e i comandi `kuma-sync-sqlite`, `kuma-map`, `kuma-describe`, `kuma-finalize`, `kuma-index`;
- l'inventario Kuma non va dichiarato completo finché non è sincronizzato da un DB live/backup recente della vera istanza;
- evidenza utente del 2026-09-11: `Fedora Host` e `Fedora Storage` risultano rossi/0%; `Fedora Network` e `Fedora Services` risultano verdi e `Fedora Software` mostra attività prevalentemente verde. È solo un indizio iniziale: verifica lo stato live e non dedurre la causa dallo screenshot.

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

Non modificare direttamente il SQLite live di Uptime Kuma se esiste un percorso amministrativo/tooling già supportato. Se l'unico modo praticabile richiede una mutazione raw del DB live o un'operazione distruttiva, promuovi MegaVault a `STRICT`, crea prima un backup verificabile e procedi solo con una strategia transazionale/ripristinabile; altrimenti fermati con blocker.

# Verifiche / acceptance
- `python3 megavault.py operational-index-migrate` PASS;
- `python3 megavault.py operational-index-validate` PASS, non `PASS_WITH_WARNINGS` per inventario non sincronizzato;
- `python3 megavault.py kuma-index` mostra inventario live `COMPLETE`, almeno un monitor corrente, zero monitor correnti non mappati e zero spiegazioni mancanti;
- `Fedora Host` e `Fedora Storage`: root cause identificata, fix mirato applicato se risolvibile in scope, heartbeat recente e stato corrente UP verificati; se uno resta DOWN, il motivo deve essere reale e documentato, non mascherato;
- per ogni progetto attivo con servizi Fedora: monitor presente se utile secondo i criteri sopra, oppure esclusione motivata nel report finale; nessun duplicato inutile;
- per ogni nuovo monitor: mapping MegaVault a `project_id` + spiegazione presenti dopo il resync finale;
- `python3 megavault.py validate` PASS dopo le modifiche MegaVault;
- test mirati dei repo modificati PASS; niente audit generale, refactor, cleanup o modifiche fuori scope.

# Discipline / stop
Riusa i fatti già presenti in MegaVault e nei repo proprietari; non riesplorare tutta l'organizzazione. Raggruppa query/check indipendenti, niente retry identici senza nuova evidenza. Non mostrare segreti. Commit/push separati solo per i repo realmente modificati e verifica una volta lo stato finale. Quando acceptance è soddisfatta, aggiorna/archivia questo task secondo il README della roadmap e STOP.

Output finale conciso: `PROMPT_ID`, `RESULT`, stato inventario Kuma e numero monitor, root cause+fix di `Fedora Host`, root cause+fix di `Fedora Storage`, progetti Fedora candidati con esito `MONITORED`/`EXCLUDED` e motivo, nuovi monitor+project_id, test, commit SHA per repo, blocker residui.
