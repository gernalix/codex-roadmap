PROMPT_ID=374820
PROJECT=fedora-system-monitor
MODEL=GPT-5.6 Luna
REASONING=low
MegaVault=FAST

# Goal
Chiudere SOLO il gate Uptime Kuma di fedora-system-monitor. Non richiedere preventivamente un nuovo login: usa l'accesso/sessione già disponibile e considera l'autenticazione un blocker solo se fallisce realmente durante questa esecuzione.

# Starting point
- repo: /home/daniele/projects/fedora-system-monitor;
- baseline 46235552ee292c96f6e4b00de39db2e520493b32 deve essere antenata, non exact HEAD;
- profilo Chrome canonico: /home/daniele/.var/app/com.google.Chrome/config/google-chrome;
- attesi: monitor #39=180/60; #40=480/180 con upside_down=1;
- config locale: inverted_categories=["storage"];
- deploy/test/CI precedenti sono già conclusi: non ripeterli.

# Execution
1. Claim con roadmap_start.py e usa il worktree_path restituito. Un solo sync/fetch bounded.
2. Fai prima un readback mirato di #39/#40 con il meccanismo autenticato già supportato dal repo/sessione locale. Se valori e config sono già esatti, PASS senza riconfigurare.
3. Solo se esiste un mismatch, esegui UNA volta il comando/configuratore Kuma mantenuto dal repo usando il profilo Chrome canonico già esistente, poi un solo readback.
4. Non chiedere né imporre un nuovo login in anticipo. Se l'accesso corrente viene davvero rifiutato/stale, controlla solo un eventuale meccanismo auth/sessione locale già documentato e supportato, senza stampare segreti e senza creare nuovi token/account. Nessun retry identico.
5. Se nessun accesso supportato funziona, BLOCKED immediato riportando l'esatto passo UI necessario; altrimenti continua.
6. Correggi solo un mismatch tecnico concreto di #39/#40 o della config storage. Niente redeploy, suite, CI, README, MegaVault audit o esplorazione repo-wide.

# Acceptance
PASS con baseline antenata, #39/#40 esatti e storage inversion preservata. Un login già valido conta come prerequisito soddisfatto. Stop immediato dopo PASS.

# Output
Massimo 7 righe. Prima riga PROMPT_ID=374820, seconda RESULT=PASS|BLOCKED|FAIL, poi AUTH, MONITOR_39, MONITOR_40, STORAGE_INVERSION, BLOCKER.
