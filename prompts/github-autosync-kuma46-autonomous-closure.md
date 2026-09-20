PROMPT_ID=404936 | PARENT_PROMPT_ID=642913 | project_id=92 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT
Codex Desktop project: Fedora

# Goal
Risolvi definitivamente il monitor Uptime Kuma **Fedora GitHub Reconcile** che è ancora rosso. Questa è una closure end-to-end: NON terminare il task mentre il monitor è DOWN, l'heartbeat manca, `github-autosync.service` continua a fallire o la correzione non è stabile nel runtime reale.

Diagnostica dalla causa reale, correggi qualunque componente nello stesso failure domain e continua autonomamente fino alla prova live di stabilità. I passi sotto sono un piano iniziale, non una whitelist.

# Starting point autoritativo
- checkout canonico Fedora: `/home/daniele/projects/github-autosync`;
- monitor Kuma: `Fedora GitHub Reconcile`, storico ID #46 salvo sostituzione necessaria;
- evidenza live utente più recente: `github-autosync.timer` è enabled/active; `github-autosync-watchdog.timer` è enabled/active; la service usa già `ExecStart=/usr/bin/python3 /home/daniele/projects/github-autosync/github_autosync.py run` ma termina ripetutamente con `status=75/TEMPFAIL` ogni minuto;
- remoto `gernalix/github-autosync/main` contiene almeno `299a4631e9b174b0c4a91d5620082ca15403d310`;
- fix già mergiati da NON reimplementare alla cieca:
  - `914ae93a...`: heartbeat periodico + DOWN esplicito;
  - `a5319700...`: refresh unit systemd stale;
  - `d2880289...`: watchdog indipendente;
  - `299a4631...`: discovery GitHub REST-first + errore fatale esplicito nel journal.
Non assumere che l'ultima ipotesi sia ancora corretta: usa il runtime live per identificare il blocker attuale.

# Piene autorizzazioni in-scope
Hai autorizzazione a fare tutto ciò che è tecnicamente necessario per questo goal, senza chiedere conferme intermedie:
- usare `sudo`/root sul Fedora per systemd, file di configurazione, permessi, pacchetti di sistema e diagnostica;
- usare il canonical Oracle SSH helper e `sudo` sulla VM per Uptime Kuma; fermare/riavviare il container, fare backup del DB Kuma e correggere direttamente configurazione/record del monitor se necessario;
- leggere/modificare in modo sicuro `~/.config/github-autosync/reconcile.env`; rigenerare/reassociare il Push token se corrotto o incoerente, senza stamparlo nei log/report;
- riavviare/reloadare unit user, timer, watchdog, user daemon e servizi coinvolti; terminare processi realmente bloccati e rimuovere lock solo dopo aver provato che sono stale;
- modificare codice, test, script, unit, config e documentazione tecnica in `github-autosync`; se l'evidenza lo richiede puoi toccare anche `vm_oracle` o `fedora-system-monitor`, ma SOLO per questo incident;
- per ogni modifica Git usa il single-writer/worktree/PR canonico; segui l'integrazione fino al merge, sincronizza il runtime e continua la stessa diagnosi;
- se il monitor #46 è corrotto irreparabilmente, puoi ricrearlo: alla fine deve esistere **un solo** monitor Push attivo chiamato `Fedora GitHub Reconcile`; disabilita/rimuovi il duplicato stale solo dopo backup e verifica;
- usa solo Python/librerie globali e pacchetti di sistema: **nessun venv**.

Non sei autorizzato a perdere lavoro/dati non correlati, force-pushare branch canonici, cancellare repo/history o esporre segreti. Questi sono limiti di sicurezza, non ragioni per fermarti davanti a un normale failure tecnico.

# Esecuzione autonoma
1. Esegui subito `roadmap_start.py` per 404936.
2. Fai UNA raccolta diagnostica iniziale compatta e salvane l'evidenza utile:
   - HEAD/origin/status del repo;
   - `systemctl --user status` + timer list per autosync/integrator/watchdog;
   - journal recente della service e watchdog;
   - esecuzione diretta `python3 github_autosync.py --json run`;
   - `gh auth status` e rate-limit REST/GraphQL;
   - presenza/permessi dell'env Kuma senza stampare il token;
   - test diretto del Push endpoint con token redatto dall'output;
   - stato reale del monitor Kuma/heartbeat lato VM.
3. Identifica il PRIMO errore concreto. Correggilo e riprendi dal gate fallito. Non fare retry identici senza nuova evidenza e non aprire audit generali.
4. Continua il loop diagnose → fix → deploy → verify per TUTTI i blocker successivi dello stesso failure domain. Errori di test, Git, rate limit, unit stale, config, token mismatch, lock stale, DB Kuma, permessi, CI o integrazione sono problemi da risolvere, non risultati terminali.
5. Se serve una modifica codice: test mirati → suite pertinente una volta → PR single-writer → attendi l'integrazione in modo bounded → sincronizza/install runtime → riprendi la verifica live. Non fermarti a "PR aperta", "CI pending" o "fix mergiato".
6. Se serve una modifica Kuma: prima backup consistente del DB/config; poi modifica minima; verifica integrità e riavvio prima di procedere.
7. Mantieni output/tool-call compatti. Riusa evidenze già verificate in questa sessione.

# Acceptance — tutte obbligatorie
PASS solo quando:
- `github-autosync` canonico contiene tutti i fix necessari e il runtime installato corrisponde al canonico;
- un run manuale reale termina senza TEMPFAIL/errori e restituisce stato coerente;
- almeno 4 attivazioni consecutive del timer/service nell'arco di >=3 minuti non falliscono;
- il watchdog è enabled/active e non entra in loop di recovery;
- il Push endpoint reale accetta heartbeat senza esporre il token;
- Uptime Kuma mostra **un solo** monitor attivo `Fedora GitHub Reconcile` e stato **UP/verde**;
- l'ultimo heartbeat lato Kuma è fresco e il monitor resta UP per >=3 minuti, oltre una singola transizione momentanea;
- nessun altro monitor/servizio GitHub/Fedora è stato rotto dal fix.

# Politica di arresto
NON dichiarare BLOCKED/FAIL per un blocker tecnico in-scope finché esiste una recovery sicura ragionevole. Non chiedere autorizzazioni aggiuntive per azioni già autorizzate sopra.
BLOCKED è ammesso soltanto se, dopo aver esaurito le alternative sicure, serve inevitabilmente un'azione umana non automatizzabile (es. 2FA/credenziale non accessibile o intervento fisico). In quel caso indica UNA sola azione precisa necessaria. FAIL solo se gli acceptance criteria sono tecnicamente irraggiungibili con le risorse disponibili.

Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 404936 --confirm-executed`
e STOP immediato.

# Report finale
Massimo 8 righe:
PROMPT_ID=404936
RESULT=PASS|BLOCKED|FAIL
ROOT_CAUSE=<causa verificata>
FIX=<fix realmente applicato>
FEDORA=<service/timer/watchdog>
KUMA=<monitor/id/status/heartbeat>
TESTS=<gate e CI>
BLOCKER=<none|unica azione umana indispensabile>
