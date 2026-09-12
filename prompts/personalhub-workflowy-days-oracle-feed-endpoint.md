[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=681427 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

> Esecuzione diretta. Non rifare l'analisi architetturale già conclusa: il producer Workflowy-days e il consumer PersonalHub esistono già. Questo task serve solo a trovare/configurare l'endpoint reale sulla VM Oracle e a chiudere l'eventuale autenticazione read-only.

# Goal
Rendere realmente operativo il sync **Workflowy-days → PersonalHub** determinando l'URL HTTPS esatto raggiungibile dal Pixel, verificandolo end-to-end e aggiungendo solo l'eventuale supporto minimo di autenticazione necessario.

# Fatti già verificati
- `workflowy-import` è `project_id=94` e genera sia la tabella `workflowy_days` in `workflowy.db` sia il file compatto `/home/ubuntu/imports/workflowy_days.json`.
- `PersonalHub` è `project_id=49` e `main` contiene già `WorkflowyDaysSync`, DB locale separato `workflowy_days.db`, scheduling WorkManager giornaliero, ETag/304, deep-link Workflowy e schermata Impostazioni → Giorni Workflowy.
- Il deep link è derivato deterministicamente dagli ultimi 12 caratteri dell'UUID Workflowy.
- Non modificare la pipeline OCR/transazioni, `DatasetteSync` o `SyncJournal` salvo blocker tecnico inevitabile e direttamente dimostrato.
- `datasette5` documenta già un runtime Oracle con nginx/reverse proxy e API HTTPS mobili; hostname, route e segreti reali appartengono alla configurazione runtime privata, non vanno inventati.

# Procedura minima
1. Prima di lavorare sulla VM, pullare il checkout canonico di `vm_oracle`. Pullare anche `workflowy-import`, `PersonalHub` e `datasette5` **solo se vengono realmente letti/modificati**; non fare discovery generale dei repo.
2. Sulla VM Oracle individua, partendo dai service/config già pertinenti a Datasette/nginx:
   - runtime Datasette attivo;
   - se `workflowy.db` è già servito;
   - hostname HTTPS pubblico già usato dalle API PersonalHub;
   - route reverse-proxy applicabile a `workflowy_days`;
   - autenticazione effettiva: nessuna, Bearer, Cloudflare Access o combinazione.
3. Determina l'endpoint più semplice e stabile. Preferenza:
   - A. riusare Datasette con una route equivalente a `.../workflowy/workflowy_days.json?_shape=array` se il DB è già servito;
   - B. altrimenti esporre il piccolo `workflowy_days.json` tramite l'infrastruttura HTTPS esistente;
   - non creare un nuovo server/daemon se nginx/Datasette esistenti bastano.
4. Non rendere anonimamente pubblico il feed se l'infrastruttura mobile esistente usa autenticazione.
5. Verifica l'endpoint con richiesta reale da un host esterno alla VM (preferibilmente Fedora) e non limitarti a localhost. Deve restituire HTTP 200 e JSON parseabile dal formato già supportato da `WorkflowyDaysFeed`.
6. Verifica che il payload contenga nodi-data reali noti quando presenti nel DB, includendo almeno un giorno tra `2026-09-01` e `2026-09-07`.

# Autenticazione
Se l'endpoint richiede Bearer auth:
1. crea/riusa il meccanismo Datasette esistente per un actor/token **read-only dedicato a Workflowy-days**;
2. concedi solo il minimo necessario per leggere `workflowy_days`; nessun insert/update/delete/write-sql e nessun accesso non necessario ad altre tabelle;
3. mantieni token/segreti fuori da Git e non stamparli nei log/output;
4. estendi `WorkflowyDaysSync` e la relativa schermata impostazioni con il minimo supporto Bearer necessario, senza toccare `DatasetteSync`/`SyncJournal`;
5. verifica con lo stesso token che `workflowy_days` sia leggibile e che almeno una risorsa non autorizzata resti negata.

Se invece la route funziona in sicurezza senza token applicativo, non aggiungere autenticazione artificiale a PH.

# Concorrenza / sicurezza Git
Prima di modificare PersonalHub:
- fetch/pull remoto corrente;
- controlla se `main` è avanzato e se ci sono modifiche concorrenti sui file che devi toccare;
- se c'è sovrapposizione reale con un'altra sessione, non sovrascrivere: integra solo con merge/rebase pulito oppure `RESULT=BLOCKED`.

# Acceptance
PASS solo se:
- esiste un `FEED_URL` HTTPS esatto e verificato dall'esterno della VM;
- HTTP 200 e JSON valido;
- PH può consumarlo con il meccanismo implementato;
- se serve auth, è read-only e least-privilege;
- nessuna modifica alla pipeline OCR/transazioni o al sync upload generico;
- eventuali repo modificati sono pushati.

Non fare build/install APK o QA Android completa se non necessaria per dimostrare specificamente il supporto auth aggiunto. Se il codice PH non cambia, nessuna build.

Su PASS completa solo questo prompt:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 681427 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 681427`

`push_verified=git_push_exit_0` è terminale: niente status/fetch/rev-parse successivi sulla roadmap.

Output massimo 8 righe:
`RESULT=PASS|BLOCKED`
`FEED_URL=<url esatto>`
`AUTH=none|bearer|other`
`DATABASE=<nome Datasette o file>`
`TABLE=workflowy_days`
`PH_CHANGE=<none|descrizione minima>`
`TEST=<esito sintetico>`
`BLOCKER=<solo se presente>`
