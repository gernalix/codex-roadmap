PROMPT_ID=576041 | PARENT_PROMPT_ID=521404 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST

# Goal
Chiudi la PR PersonalHub #15 già implementata e corretta. Non rifare discovery, implementazione, migrazioni o gate già PASS: completa solo i gate ancora necessari, QA AVD, merge e cleanup.

# Starting point autorevole
- repo: /home/daniele/projects/PersonalHub;
- PR #15 è OPEN e mergeable;
- candidate: feature/shared-alerts-place-tags;
- head minimo già corretto: 8103410c3f92e4b5f567072224622c7916034bb6;
- il candidate include già: shared alerts, Places tags, profile runtime restore, Room v16, version.txt=52;
- include inoltre i fix successivi: link validation JVM-safe e recupero automatico dei lease PersonalHub orfani/terminali;
- non fare un secondo bump versione;
- la readiness delle dipendenze è già stata verificata da roadmap_start: non ricontrollare PROMPT_ID predecessori.

# Esecuzione autonoma
1. Esegui roadmap_start 576041. Un solo fetch mirato di main + PR #15. Usa il latest PR head se più avanti del minimo sopra.
2. Esegui solo il test mirato del nuovo helper lease (`tools/test_personalhub_task_lock.py`) se non è già coperto/green sul latest head. Non ripetere migration/FK/alerts/Places/Timer/app compile già validati salvo diff successivo che li invalidi.
3. Controlla CI una volta. CI pending/in-progress NON è BLOCKED: svolgi nel frattempo il lavoro locale utile. Se un job fallisce, apri solo il job/step fallito, correggi in-scope sul candidate e rilancia il minimo gate invalidato.
4. Acquisisci il lease con `tools/personalhub_task_lock.py acquire --prompt-id 576041`. Il helper ora recupera automaticamente lock orfani se il prompt proprietario è terminale nel DB locale o il PID locale è morto. Non cancellare manualmente lock vivi.
5. QA `Pixel_8a` via facade canonica, solo scope PR: avvio; switch profilo; Places tags; alert Places; regressione Timer alert minima; direct-tap link-only http/https/workflowy; mixed/unsafe non auto-open. Riusa un artifact valido o fai una sola build debug necessaria.
6. Refresh main una sola volta, semantic review del delta corrente, attendi solo i required check ancora realmente necessari e verdi; non duplicare CI con test locali equivalenti.
7. Merge PR #15. Verifica containment del PR head in origin/main.
8. Elimina feature/shared-alerts-place-tags e chatgpt/918274-runtime-restore locale/remoto solo dopo containment. Rilascia sempre il lease.

# Recovery / stop
Un helper difettoso, lock orfano, CI pending, test fallito correggibile, remote advance o conflitto Git riconciliabile NON sono motivi per BLOCKED: correggi e continua nello stesso prompt. BLOCKED solo per credenziale/permesso/hardware indisponibile, rischio dati o blocker esterno non risolvibile autonomamente.

# Acceptance
PASS solo con PR #15 merged, required CI PASS, QA AVD PASS, main contenente candidate, branch cleanup e lease rilasciato.
Finalizza con roadmap_finish 576041. BLOCKED/FAIL solo secondo la regola sopra.
Prima riga output: PROMPT_ID=576041
Seconda riga: RESULT=PASS|BLOCKED|FAIL
Poi max 6 righe.
