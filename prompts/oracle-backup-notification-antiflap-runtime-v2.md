PROMPT_ID=781352 | PARENT_PROMPT_ID=219473 | project_id=43 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST
Codex Desktop project: vm_oracle


# Autonomia operativa
Goal + acceptance criteria definiscono lo scope; i passi sono il piano iniziale, non una whitelist.
Per qualunque failure nello stesso dominio puoi fare discovery mirata e modificare codice, test, adapter, config, unit/script e documentazione tecnica necessari al goal, anche se non nominati esplicitamente. Puoi usare comandi/helper equivalenti più corretti se quelli indicati sono obsoleti, correggere più blocker dello stesso dominio in batch, commit/pushare fix in-scope e continuare automaticamente.
Non terminare BLOCKED/FAIL per test/compile failure, mismatch di file/helper, warning, remote advance riconciliabile, lock transitorio o necessità di toccare un file adiacente. BLOCKED solo per credenziale/permesso/decisione umana indispensabile, runtime esterno indisponibile senza alternativa, rischio dati/distruzione non autorizzata o conflitto semantico materialmente fuori goal. FAIL solo dopo recovery in-scope ragionevole realmente esaurito.

# Goal
Distribuisci sulla VM Oracle il fix anti-flapping già versionato in `gernalix/vm_oracle`, così gli stati transitori del backup non generano più coppie Telegram ALERT/RECOVERY inutili.

# Starting point autoritativo
- checkout canonico Fedora: `/home/daniele/projects/vm_oracle`, branch `main`, origin `https://github.com/gernalix/vm_oracle.git`;
- baseline minima già pushata: commit `f66770c42cad31a6eddc7229c90f9680db6eabb1`;
- helper pronto: `scripts/oracle_backup_alert_gate.py`;
- test pronto: `tests/test_oracle_backup_alert_gate.py`;
- accesso VM canonico: `scripts/oracle_ssh.sh`;
- runtime coinvolto: `oracle-backup-monitor.service` / `oracle-backup-monitor.timer`;
- esempi reali del bug: ALERT con `status=OK`, `last_any_success_age=3511..5313s <= 5400`, `running_age=missing`, seguito ~5 min dopo da RECOVERY;
- policy vincolante: con `status=OK` e `last_any_success_age <= 5400`, active/running marker mancante o heartbeat transitorio NON deve da solo produrre Telegram ALERT; soft-failure persistono almeno 600 s prima di ALERT; hard-failure reali restano immediate; RECOVERY solo dopo un ALERT realmente inviato.
- NON leggere roadmap/spiegazioni/MEMORY/MegaVault o fare audit generale: questo starting point sostituisce la discovery documentale.

# Esecuzione
1. In `/home/daniele/projects/vm_oracle`: verifica `main` + origin e sincronizza in modo non distruttivo. Se ci sono dirty path o divergenza, identifica l'overlap e preserva il lavoro utente; usa worktree/branch o riconciliazione Git sicura se basta allo stesso goal. Blocca solo se il conflitto semantico è fuori scope o c'è rischio di perdita dati.
2. Esegui una sola volta:
   `python3 -m unittest tests.test_oracle_backup_alert_gate -v`
   Se FAIL, correggi SOLO helper/test e rilancia solo il test fallito.
3. Con una sola raccolta SSH mirata acquisisci:
   - `systemctl cat oracle-backup-monitor.service oracle-backup-monitor.timer`;
   - `systemctl show oracle-backup-monitor.service -p ExecStart -p User -p Group -p ActiveState -p SubState`;
   - il solo file/script referenziato da ExecStart e, se necessario, massimo 100 righe recenti di journal del monitor.
   Niente journal globale/inventory della VM.
4. Integra il gate nel monitor reale con il minimo diff:
   - stato persistente in un path runtime owner-only; preferisci `/var/lib/oracle-backup-monitor/notification-gate.json` se compatibile con l'utente del servizio;
   - stato healthy quando `status=OK` e `last_any_success_age <= 5400`, anche se `running_age`/active marker manca;
   - condizioni solo transitorie di marker/heartbeat/soglia diventano `soft-failure` e devono restare tali >=600 s prima di notificare;
   - failure esplicite già realmente critiche restano `hard-failure`;
   - invia Telegram solo su output `ALERT`; invia recovery solo su `RECOVERY`; `SILENT` non invia nulla;
   - non cambiare schedule, backup payload, retention, Restic, soglia 5400 o destinatario Telegram.
5. Se la sorgente runtime modificata non è già versionata nel repo, aggiungi SOLO quella sorgente/unit/drop-in necessaria a `vm_oracle` senza segreti, in un path coerente `scripts/` o `systemd/`; il repo deve restare sufficiente per ridistribuire il fix.
6. Installa/copia solo i file necessari sulla VM con backup locale del file runtime precedente. `daemon-reload` solo se tocchi unit/drop-in. Mantieni timer/servizio attivi.
7. Verifica senza inviare Telegram di prova:
   - test sintetico del gate con state file temporaneo: soft <600 s => sempre SILENT e ritorno healthy => SILENT; soft >=600 s => un solo ALERT, poi SILENT, poi un solo RECOVERY; hard => ALERT immediato;
   - `systemctl is-active oracle-backup-monitor.timer`;
   - `systemctl status oracle-backup-monitor.service --no-pager -n 30` oppure equivalente bounded;
   - nessun nuovo failure del monitor nel journal mirato.
   Non aspettare un'ora e non creare falsi incidenti reali solo per testare Telegram.
8. Se hai modificato il repo oltre la baseline: un solo commit/push finale dopo i gate. Prima del push fai un solo refresh di origin; se origin è avanzato, integra autonomamente il nuovo stato con la strategia Git non distruttiva più semplice e rilancia solo i gate invalidati. Blocca solo per conflitto sostanziale fuori goal o rischio dati.
9. PASS solo se runtime + repo sono coerenti e i gate sopra sono verdi. Poi finalizza una sola volta:
   `python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 781352 --confirm-executed`

# Non-goal / stop
Niente aggiornamenti generali VM, niente modifiche al backup stesso, niente test Telegram artificiali, niente audit Uptime Kuma/Datasette/rete, niente refactor o cleanup fuori scope, niente ulteriori controlli dopo PASS.

Output finale massimo 5 righe:
`RESULT=PASS|BLOCKED|FAIL`
`RUNTIME=<deployed|unchanged|blocked>`
`ANTI_FLAP=<PASS|FAIL|NOT_RUN>`
`REPO_COMMIT=<sha|none>`
`BLOCKER=<none|testo minimo>`
