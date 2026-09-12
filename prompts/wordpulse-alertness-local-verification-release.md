# WordPulse — verifica locale Alertness/Fatigue

`PROMPT_ID=483217 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD | type=Prompt`

Esegui direttamente questo file. Non usare `roadmap_guard.py select` e non rileggere roadmap/README/spiegazioni/altri prompt. Questo è un task di **verifica locale**, non di redesign.

# Goal
Finalizzare l'implementazione Alertness/Fatigue già presente su `gernalix/wordpulse`: generare lo schema Room 4 con la toolchain locale, eseguire test/lint/build e QA isolata Pixel. Correggere solo failure concrete.

# Starting point verificato
- remoto canonico `gernalix/wordpulse/main`, checkout atteso `/home/daniele/projects/wordpulse`;
- feature già implementata: metriche typing, fatigue 0–100/alertness, baseline, Health Connect sleep opzionale, PVT 3 min, migration 3→4, backup/import, UI e test;
- `version.txt=3` al momento della preparazione; usa il remoto corrente come autorità;
- manca intenzionalmente `app/schemas/com.wordpulse.app.data.WordPulseDatabase/4.json`, da generare con KSP/Room locale.

# Procedura minima
1. Sincronizza una volta con `origin/main`; se modifiche/commit locali impediscono fast-forward sicuro => `BLOCKED`, niente stash/reset/force.
2. Esegui in modo compatto test JVM + lint + `--no-configuration-cache assembleDebug`. Non ripetere gate PASS.
3. Verifica/genera schema Room 4 e migration 3→4; mai costruire a mano identity hash.
4. Su failure, fix minimo nel file direttamente coinvolto; niente refactor/audit generale.
5. QA Pixel solo package `.qa`: overlay Alertness, baseline insufficiente, Health Connect presente/assente senza loggare dati personali, PVT attesa→stimolo→tap poi annulla, fallback typing-only.
6. Disinstalla sempre il package QA. Non installare sopra l'app reale.
7. Commit/push solo schema generato + eventuali fix indispensabili. Niente APK/cache/log/runtime DB.

# Acceptance
PASS: test/lint/build, schema/migration, QA isolata e cleanup QA passano; diff resta stretto; push senza force. Health Connect può essere oggettivamente indisponibile purché fallback sia provato.

Su PASS completa solo `PROMPT_ID=483217` con dry-run+real `roadmap_guard complete`; `push_verified=git_push_exit_0` basta, nessun controllo roadmap successivo.

Output massimo 6 righe: RESULT, SHA, gate locali, schema/migration, Pixel/Health Connect/PVT+cleanup, blocker.
