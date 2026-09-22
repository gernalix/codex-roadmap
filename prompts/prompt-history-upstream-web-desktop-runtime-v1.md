PROMPT_ID=571364 | project_id=92 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST
REPO=gernalix/prompt-history
WORKDIR=/home/daniele/projects/prompt-history

# Goal
Attiva sul Fedora reale l'ingestione unificata upstream-first di ChatGPT Web + ChatGPT Desktop/Codex già implementata in prompt-history. Non riscrivere scraper o parser: usa gli upstream OSS fissati e limita le modifiche al deploy/config/runtime necessari.

# Starting point verificato
- prompt-history/main contiene almeno f607ea48d509af8f363804e6a4c45b13762c5bfa.
- Adapter e test sono già implementati: ingest-chatgpt-exporter, ingest-session-bandit, sync --chatgpt-exporter/--session-bandit, tools/session_bandit_dump.mjs.
- CI del commit test 6878f0c182a738fba121bc954862fd6d33375ae4 è PASS. Prima del deploy verifica solo che il CI del main corrente sia verde; niente audit generale.
- ChatGPT Web upstream: siraht/ChatGPTExporter commit c5618b3cc06eeb5b273d3727fe8729071441f291, MIT. prompt-history consuma soltanto conversations/*/conversation.json normalizzati.
- Codex upstream parser: janole/session-bandit commit a618b5b54d804eae8d2537feec77e2d2acdfe3e8 (v0.1.7), MIT. Il bridge importa il core compilato e produce JSONL.
- codex-usage resta l'unica fonte autorevole per execution/token/tool-call/duration/result; Session Bandit aggiunge transcript/provenance e NON deve duplicare executions.
- DB derivato: ~/.local/share/prompt-history/prompt_history.sqlite. Timer esistente: prompt-history-sync.timer circa ogni 15 minuti.

# Esecuzione minima
1. Claim 571364 e fai un solo fetch/fast-forward sicuro di prompt-history/main. Se il worktree ha modifiche sovrapposte, BLOCKED; niente stash/reset distruttivo.
2. Esegui solo: python3 -m py_compile prompt_history/*.py; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v. Se PASS, non fare altri audit.
3. Upstream esterni: usa ~/.local/share/prompt-history/upstream/. Se i checkout esistono, verifica remote+revision; altrimenti clona SOLO i due repo sopra. Checkout esatto dei commit fissati. Non committare upstream dentro prompt-history.
4. Session Bandit: installa/builda solo quanto serve al core secondo il workspace upstream; poi genera atomically ~/.local/share/prompt-history/session-bandit-codex.jsonl da ~/.codex/sessions con tools/session_bandit_dump.mjs. Verifica che almeno una sessione Codex reale sia parseabile senza stampare contenuti.
5. ChatGPT Web: ispeziona SOLO /home/daniele/Documents/ChatGPT e ~/.local/share/prompt-history per un export ChatGPTExporter già presente e/o conversations.json autorevole. Se c'è un archive ChatGPTExporter, configurarlo come fonte primaria; conserva conversations.json come fallback quando presente. Se l'archive non esiste, builda ChatGPTExporter al commit fissato e registra il path della extension build pronta da caricare, senza inventare dati e senza forzare logout/login o riavvio distruttivo di Chrome.
6. Aggiorna il runtime locale di prompt-history, non Git con dati privati: il servizio/timer deve rigenerare il JSONL Session Bandit prima di ogni sync e passare al sync solo le fonti realmente presenti (--chatgpt, --chatgpt-exporter, --session-bandit, --switcher). Mantieni Type=oneshot + timer; niente Restart=always sul oneshot.
7. Esegui una sync completa e una seconda sync invariata. Verifica con soli count/hash che: seconda run non crea duplicati logici; Session Bandit non incrementa executions; ChatGPTExporter e conversations.json convergono sugli stessi message ID quando sovrapposti; literal PROMPT_ID continua a collegare ChatGPT↔Codex.
8. Smoke finale: similar + model-stats o blockers; systemctl --user is-enabled/is-active prompt-history-sync.timer. Non stampare chat, note, URL privati, cookie o token.
9. Modifica codice solo se un test/runtime gate in-scope fallisce. Nessun refactor, cleanup, upgrade upstream o esplorazione generale. Dopo PASS finalizza 571364 e STOP.

# Acceptance
PASS se main/test sono verdi, Session Bandit reale viene parseato tramite upstream, il runtime usa le nuove fonti senza doppio conteggio executions, il sync è idempotente, ChatGPTExporter è configurato se esiste oppure buildato/pronto se non esiste ancora un archive, fallback conversations.json resta valido, timer attivo, e nessun dato privato entra in Git.

# Report
Massimo 9 righe: RESULT, MAIN_REVISION, UPSTREAM_PINS, CODEX_SESSIONS=<count>, CHATGPT_SOURCE=<exporter|conversations|both|ready-no-archive>, DB_COUNTS, IDEMPOTENCE, TIMER, BLOCKER.