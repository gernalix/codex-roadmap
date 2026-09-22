PROMPT_ID=918643

Correzione diretta del FAIL di PROMPT_ID=463817. Continua dallo stato già verificato in questa sessione e RIUSA tutti i risultati già ottenuti. Non ripetere inventory, audit o test già conclusi se non necessari per verificare una modifica.

OBIETTIVO
Portare a PASS l'hardening dei servizi custom e l'integrazione Uptime Kuma/MegaVault che 463817 ha lasciato incompleti.

STATO GIÀ VERIFICATO

* 36 servizi custom totali.
* 10 always-on.
* 26 timer/oneshot/event/lifecycle: NON devono essere trasformati artificialmente in daemon persistenti.
* `service_health` già PASS.
* FSM config-check già PASS.
* almeno il servizio ADB attivo usa ancora `Restart=on-failure`.
* altri daemon always-on presentano drift rispetto allo standard.
* Kuma ha aggregate monitor + un solo monitor individuale.
* MegaVault usa già la tabella `services`, ma l'indice Kuma è incompleto/stale.
* le sei vecchie PR sono chiuse/unmerged ma i tree canonici equivalenti sono già stati verificati: NON riaprire, ricreare o riauditare quelle PR.
* blocker precedente: il tooling FSM canonico non espone il path autorevole del DB/backup di Uptime Kuma.

REGOLE

1. Modifica direttamente le fonti canoniche; niente PR.
2. Scope stretto: sistema solo quanto necessario a soddisfare questa acceptance.
3. Non fare refactor/cleanup/modernizzazioni collaterali.
4. Non fare esplorazione generale dei repo.
5. Parti da AGENTS.md/MegaVault e dai file/tool già identificati nella sessione.
6. Non ripetere comandi equivalenti senza nuova evidenza.
7. Non considerare più “DB path non esposto dal tooling” un motivo sufficiente per fermarti: correggi il tooling canonico affinché possa determinare/esporre in modo affidabile il path reale.
8. Non indovinare mai path di database o backup.
9. Nessuna modifica diretta al DB Kuma finché non hai determinato autorevolmente:

   * runtime/istanza Kuma corretta;
   * DB realmente in uso;
   * directory/file di backup corretti.
10. Prima di modificare SQLite: crea backup verificabile. Esegui modifica transazionale e successivo readback.
11. Se Kuma deve essere temporaneamente fermato per garantire consistenza SQLite, fallo usando il meccanismo canonico e riavvialo subito dopo con verifica runtime.
12. Preserva integralmente monitor/config esistenti non coinvolti.

TASK A — HARDENING SYSTEMD
Individua SOLO i 10 servizi classificati already-on/daemon.

Per ciascuno applica lo standard always-on già definito nel progetto/MegaVault. In particolare elimina il drift come `Restart=on-failure` dove lo standard prescrive restart continuo.

Non modificare semanticamente i 26 timer/oneshot/event/lifecycle.

Assicurati che:

* i daemon always-on si autoripristinino dopo terminazione/crash secondo lo standard;
* unit file e relativi generator/template rimangano coerenti;
* eventuali file installati siano aggiornati dal source canonico, non patchati soltanto nel runtime.

Esegui daemon-reload/restart solo dove necessario e verifica lo stato runtime dei daemon interessati.

TASK B — RENDERE AUTOREVOLE IL TOOLING KUMA/FSM
Individua il meccanismo realmente usato per eseguire Uptime Kuma, partendo dalle informazioni già disponibili nella sessione.

Estendi il tooling FSM canonico con il MINIMO necessario perché possa risolvere e restituire programmaticamente almeno:

* Kuma runtime/instance;
* authoritative DB path;
* authoritative backup destination/path.

La risoluzione deve derivare dalla configurazione/runtime reale, non da path hardcoded fragili se evitabile.

Aggiungi test mirati per questo comportamento.

TASK C — MONITOR KUMA INDIVIDUALI
Usando esclusivamente il DB autorevole risolto dal tooling:

* crea/aggiorna in modo idempotente i monitor richiesti per TUTTI i servizi custom per cui lo standard MegaVault prevede monitoraggio individuale;
* mantieni anche il monitor aggregate esistente;
* evita duplicati;
* preserva monitor estranei;
* usa naming/tag/metadata coerenti e deterministici;
* collega correttamente ogni monitor all'identità canonica del servizio.

Prima della write:

* backup verificato.

Write:

* transazione atomica.

Dopo la write:

* readback SQLite;
* verifica conteggi e mapping;
* verifica che Kuma riparta/continui a funzionare;
* verifica almeno un percorso runtime rappresentativo del monitoraggio.

TASK D — MEGAVAULT
Aggiorna la tabella `services` e/o l'indice Kuma canonico già esistente affinché rappresentino lo stato reale appena implementato.

Non creare una nuova tabella parallela se `services` è già la fonte corretta.

Per ogni servizio devono essere sincronizzati almeno i riferimenti necessari a capire:

* lifecycle/type;
* always-on sì/no;
* hardening/restart policy pertinente;
* presenza/identità del relativo monitor Kuma quando applicabile.

Elimina dati stale solo quando puoi dimostrare che non rappresentano più componenti reali.

ACCEPTANCE CRITERIA
PASS solo se TUTTI sono veri:

1. Inventory rimane coerente: 36 custom, con classificazione lifecycle corretta.
2. Tutti i 10 always-on rispettano lo standard di resilienza.
3. ADB non presenta più il drift `Restart=on-failure` se incompatibile con lo standard always-on.
4. I 26 non-always-on conservano la loro semantica timer/oneshot/event/lifecycle.
5. Il tooling FSM determina autorevolmente DB e backup Kuma senza guess manuali.
6. Backup Kuma verificato prima della modifica.
7. Write Kuma completata transazionalmente.
8. Readback conferma il contenuto atteso.
9. Tutti i monitor individuali richiesti dallo standard esistono, sono univoci e correttamente associati.
10. Aggregate monitor preservato.
11. MegaVault `services`/indice Kuma corrisponde alla realtà.
12. Kuma è operativo dopo la modifica.
13. I daemon coinvolti sono operativi dopo la modifica.
14. Test mirati PASS.
15. Nessuna regressione rilevata dai check canonici pertinenti.

TESTING
Esegui prima test stretti sulle parti modificate.
Amplia solo se un risultato o il rischio concreto lo richiede.
Non rieseguire suite già PASS senza motivo.

STOP RULE
Quando tutti gli acceptance criteria risultano verificati, fermati immediatamente. Nessun ulteriore audit/esplorazione.

Non restituire BLOCKED soltanto perché il vecchio tooling non esponeva il path Kuma: quella limitazione fa parte del bug da correggere.

OUTPUT FINALE CONCISO
PROMPT_ID=918643
RESULT=PASS|FAIL|BLOCKED
SERVICES=<totale / always-on / lifecycle>
HARDENING=<esito>
FSM_KUMA_PATH=<come viene risolto>
KUMA_BACKUP=<verificato/path>
KUMA_MONITORS=<aggregate + individuali / eventuali differenze motivate>
MEGAVAULT=<stato sincronizzazione>
RUNTIME=<verifiche essenziali>
TESTS=<test ed esito>
COMMITS=<commit diretti alle fonti canoniche>
BLOCKER=<solo se resta un impedimento esterno realmente non risolvibile dal codice/tooling disponibile>