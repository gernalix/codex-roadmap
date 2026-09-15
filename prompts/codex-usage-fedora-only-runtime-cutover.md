[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=472913 | project_id=8 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Completare il cutover di `codex-usage-monitor` a **un solo runtime canonico Fedora**, verificare end-to-end monitor/archive/publisher/chat dump, preservare eventuale storico unico della vecchia Oracle VM e poi dismettere in sicurezza il runtime/clone Codex-monitor sulla VM. Uptime Kuma/Datasette e altri servizi realmente always-on della VM restano fuori scope e non vanno rimossi.

# Starting point autoritativo
- Repo Fedora: `/home/daniele/projects/codex-usage-monitor`.
- Repo dati privato: `/home/daniele/projects/codex-usage`.
- Runtime Fedora: `/home/daniele/.local/lib/codex-usage-monitor`.
- Native sessions: `/home/daniele/.codex/sessions`.
- Stato/DB Fedora: `~/.local/state/codex-usage-monitor` e `~/.local/share/codex-usage-monitor/codex_usage_monitor.db`.
- `gernalix/codex-usage-monitor/main` deve contenere almeno `6c3441393a6894883f7815ecb36cebd9fb43900c` (README/unit/Kuma già resi Fedora-canonical in remoto).
- La VM/connessione/path canonici vanno presi da MegaVault; non fare inventory generale della VM.
- La VM può continuare a ospitare Uptime Kuma/Datasette. Va eliminata soltanto la seconda istanza/runtime di `codex-usage-monitor` e il relativo clone se sicuro.

# Esecuzione minima

## 1. Gate Fedora prima di toccare la VM
1. Nel clone Fedora fai una sola fotografia Git (`status --short --branch`), `fetch origin`, poi `pull --ff-only origin main` solo se il worktree è pulito. Non stashare/resetare modifiche preesistenti.
2. Verifica che HEAD contenga il commit autoritativo sopra. Se `main` è avanzato va bene; non tornare indietro.
3. Esegui solo questi gate mirati:
   - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_chat_dump_publisher tests.test_uptime_kuma_push tests.test_quota_notification_policy -v`
   - `python3 -m py_compile codex_usage_monitor.py codex_usage_publisher.py codex_chat_dump_publisher.py codex_session_archive.py deploy_runtime.py uptime_kuma_push.py`
4. Se un gate fallisce, correggi SOLO il blocker direttamente collegato al cutover/runtime Fedora, esegui il leaf test interessato e poi una sola conferma dei gate sopra. Commit/push del fix su `main` solo dopo PASS. Niente full-suite salvo failure che dimostri dipendenza più ampia.

## 2. Deploy canonico Fedora
1. Da `main` pulito e sincronizzato esegui `python3 deploy_runtime.py` una sola volta.
2. Installa/aggiorna in `~/.config/systemd/user/` le unit canoniche del repo per:
   - `codex-usage-monitor.service/.timer`
   - `codex-session-archive.service/.timer`
   - `codex-usage-publisher.service/.timer`
   senza inventare unit parallele.
3. `systemctl --user daemon-reload`; abilita/avvia solo i tre timer canonici se necessario.
4. Verifica che non esista sul Fedora una seconda unit/runtime legacy equivalente. Se ne esiste una, disabilitala/rimuovila solo dopo aver dimostrato che punta allo stesso sottosistema.

## 3. Smoke end-to-end Fedora
Esegui al massimo una volta ciascuno, nell'ordine:
1. `codex-usage-monitor.service`: deve produrre una lettura valida/attesa nel DB Fedora; una failure esterna transitoria va diagnosticata solo quanto basta per distinguere config da rete.
2. `codex-session-archive.service`: deve aggiornare l'archivio locale senza full rebuild non necessario.
3. `codex-usage-publisher.service`: deve eseguire usage publisher + complete chat dump publisher.

Verifica poi, senza audit massivo:
- i tre timer sono enabled/active;
- runtime `current` corrisponde al commit finale;
- `~/projects/codex-usage` è clean e sincronizzato con `origin/main`;
- esistono `index/native-sessions.jsonl` e almeno un `native-sessions/.../manifest.json` con chunk;
- un solo dump recente contiene record strutturati e redatti;
- esegui un solo heartbeat Kuma `--strict` da Fedora se il Push URL è configurato. Kuma può restare sulla Oracle VM.

## 4. Preserva eventuale storico unico Oracle prima della dismissione
Solo dopo PASS Fedora:
1. Con la connessione canonica MegaVault, individua esclusivamente unit/process/path già collegati al vecchio monitor Codex (`codex-usage-monitor` e/o il precedente nome legacy registrato). Non fare inventory generale dei servizi VM.
2. Individua il DB storico effettivamente usato dal vecchio runtime e confronta solo metadati economici con il DB Fedora: schema/tabelle rilevanti, numero snapshot, primo/ultimo timestamp. Non fare merge SQLite automatico.
3. Se la VM contiene storia non presente su Fedora, prima di rimuovere alcunché copia quel DB in:
   `~/.local/share/codex-usage-monitor/legacy-oracle/`
   sul Fedora, con nome timestampato, checksum SHA256 e permessi privati. È un archivio storico read-only, NON il DB di produzione.
4. Non cancellare DB storici VM, secret, Kuma, Datasette o altri dati infrastrutturali come parte di questo task.

## 5. Dismetti il runtime Oracle
1. Ferma e disabilita SOLO service/timer del vecchio monitor Codex verificati al punto precedente; `daemon-reload` e conferma inactive/disabled.
2. Verifica che nessun processo/unit restante referenzi il checkout/runtime del monitor.
3. Prima di eliminare il clone VM di `codex-usage-monitor`, verifica una sola volta:
   - origin corretto;
   - worktree pulito;
   - nessun commit locale non pushato/divergenza.
   Se uno di questi gate fallisce: **BLOCKED**, non cancellare/stashare/resetare nulla.
4. Se tutti i gate passano, rimuovi il solo clone/runtime obsoleto `codex-usage-monitor` dalla VM. Non rimuovere Codex CLI o librerie condivise se possono essere usate da altri progetti.
5. Conferma che Uptime Kuma/Datasette e gli altri servizi VM non coinvolti siano rimasti intatti; niente audit aggiuntivo.

## 6. Aggiorna MegaVault dopo il cutover reale
Aggiorna solo il record/documentazione canonica strettamente pertinente a `project_id=8`:
- runtime/host canonico = Fedora;
- VM Oracle = nessun runtime `codex-usage-monitor`;
- Kuma/Datasette possono restare servizi VM separati;
- percorsi Fedora effettivi verificati;
- eventuale archivio storico Oracle copiato e relativo path/checksum, se creato.

Usa gli helper/protocollo MegaVault esistenti e pusha solo le modifiche strettamente necessarie. Non fare audit generale MegaVault.

# Non-goal / risparmio token
- niente refactor, cleanup o modernizzazione non necessari;
- niente nuova architettura, nuovi timer o nuovi daemon;
- niente full scan di `~/.codex/sessions` se i servizi incrementali passano;
- niente merge del DB storico Oracle nel DB Fedora;
- niente migrazione di Kuma/Datasette dalla VM;
- niente esplorazione di altri servizi/repo VM;
- niente reinstallazione Codex CLI;
- niente retry identici senza nuova evidenza;
- dopo PASS non cercare altri colli di bottiglia.

# Acceptance
- Fedora è l'unico runtime attivo di `codex-usage-monitor`;
- gate mirati PASS e runtime deployato dal `main` finale;
- monitor + archive + publisher/chat dump PASS sul Fedora;
- `codex-usage` clean/synced dopo la pubblicazione;
- heartbeat Kuma da Fedora PASS se configurato;
- eventuale storia VM unica preservata senza alterare il DB produzione;
- vecchie unit monitor VM inactive/disabled;
- clone/runtime VM del monitor rimosso solo con gate Git sicuri;
- Kuma/Datasette/altro runtime VM non coinvolto resta intatto;
- MegaVault riflette la topologia reale finale.

# Finalizzazione
Solo dopo tutti gli acceptance criteria:
```bash
python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 472913 --dry-run && \
python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 472913
```
Dopo `status=completed` + `push_verified=git_push_exit_0`, STOP immediato: niente git status/fetch/pull, nessun audit post-PASS e non aprire il task successivo.

Output finale massimo 7 righe: `RESULT`, Fedora SHA/deploy, tre servizi/timer, codex-usage publish, eventuale storico Oracle preservato, runtime VM retired, MegaVault oppure blocker minimo.