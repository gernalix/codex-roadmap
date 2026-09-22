PROMPT_ID=815274
PARENT_PROMPT_ID=463817
ROADMAP_PROJECT=Fedora
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=STRICT

# Goal
Chiudi SOLO il residuo reale di 463817: completa la riconciliazione live dei monitor Uptime Kuma per i servizi Fedora usando i path canonici ora esposti da fedora-system-monitor. Non rifare inventario, hardening systemd o modifiche già concluse da 463817.

# Evidenza già verificata
- 463817 ha terminato il lavoro con FAIL solo perché il tooling non esponeva in modo autorevole DB/backup Kuma.
- Root cause corretta su gernalix/fedora-system-monitor/main.
- Baseline minima da avere localmente: daef956d1b0e353629b581d00da115dbf3848dcd.
- CI di quella baseline: PASS.
- Nuovo comando canonico: fedora-system-monitor kuma-runtime --json.
- Descriptor atteso, non segreto:
  - ssh_helper=/home/daniele/projects/vm_oracle/scripts/oracle_ssh.sh
  - compose_directory=/opt/uptime-kuma
  - database_path=/opt/uptime-kuma/data/kuma.db
  - backup_path_template=/opt/uptime-kuma/data/kuma.db.backup-<UTC_TIMESTAMP>
- Riusa l'inventario e le evidenze già raccolte da 463817. Non ripetere discovery equivalente.

# Scope
1. Claim canonico di 815274 e usa solo il worktree restituito.
2. Porta ~/projects/fedora-system-monitor al main canonico contenente almeno daef956d..., senza distruggere modifiche locali.
3. Deploy SOLO del runtime già verificato:
   sudo scripts/deploy-runtime.sh
4. Verifica una volta:
   fedora-system-monitor kuma-runtime --json
   I quattro path devono coincidere col descriptor sopra.
5. Riprendi dallo stato lasciato da 463817: identifica soltanto i monitor per-servizio mancanti/incoerenti e le relative unit già inventariate. Niente nuovo audit generale dei servizi.
6. Per qualunque operazione Kuma usa ESCLUSIVAMENTE il canonical Oracle SSH helper indicato dal descriptor.
7. Fai prima un solo readback mirato del DB Kuma. Se tutto è già corretto, non scrivere nulla.
8. Se serve davvero una modifica DB:
   - crea prima un backup SQLite timestampato e verificabile usando il path canonico;
   - non stampare token/URL push o altri segreti;
   - ferma Kuma solo se necessario per garantire una scrittura coerente;
   - applica UNA transazione minima ai soli monitor pertinenti;
   - riavvia il runtime Kuma se era stato fermato;
   - esegui un solo readback autorevole post-write.
9. Riconcilia il file credenziali locale solo se un monitor nuovo/cambiato richiede il relativo push token; non stampare mai il valore.
10. Per ogni monitor aggiunto/corretto invia un solo heartbeat reale tramite il producer Fedora e verifica nel DB Kuma monitor/timestamp attesi. Non ripetere probe identici senza nuova evidenza.
11. Verifica che:
   - nessun monitor per-servizio sia duplicato;
   - i daemon always-on pertinenti siano UP o segnalino correttamente DOWN;
   - timer/oneshot mantengano la semantica corretta;
   - il monitor aggregato Fedora Services resti coerente;
   - il backup pre-write esista solo se una write è stata realmente necessaria.
12. Aggiorna MegaVault solo per i record di servizio/monitor realmente mancanti o cambiati, senza duplicare la tabella services già canonica.

# Non-goal
Niente refactor, cleanup, nuovo inventario repo-wide, modifiche a soglie Kuma, migrazioni infrastrutturali, nuovi sistemi di autenticazione o audit dopo il PASS.

# Acceptance
PASS solo quando il residuo di 463817 è chiuso end-to-end: runtime FSM aggiornato, path Kuma canonici verificati, monitor per-servizio live coerenti, eventuale DB write coperta da backup+readback, heartbeat verificati, nessun segreto esposto.

# Stop
Al PASS usa roadmap_result/roadmap_finish per 815274 e STOP immediato.

# Report
Massimo 8 righe:
PROMPT_ID
RESULT
FSM_REVISION
KUMA_RUNTIME
MONITORS
BACKUP
READBACK
BLOCKER
