[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=483217 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=STANDARD | type=Prompt`

# Goal
Finalizza localmente l'Alertness/Fatigue già implementato in `gernalix/wordpulse`: genera schema Room 4 con toolchain reale, verifica migration/build e fai una QA Pixel **solo package `.qa`**. Il commit `origin/main` verificato su PASS diventa il riferimento autoritativo per il successivo porting nel WordPulse incorporato in PersonalHub. Non modificare PersonalHub in questo task.

# Fatti autoritativi
Checkout `/home/daniele/projects/wordpulse`; feature già presente: typing metrics, fatigue 0..100/alertness, baseline, Health Connect sleep opzionale, PVT 3 min, migration 3→4, backup/import/UI/test. Manca intenzionalmente `app/schemas/com.wordpulse.app.data.WordPulseDatabase/4.json`: va generato da Room/KSP, mai scritto a mano.

# Esegui
1. Un solo fetch/pull fast-forward di `origin/main`; lavoro locale incompatibile => `BLOCKED`, niente stash/reset/force.
2. Esegui i test/compile mirati necessari a generare/verificare schema 4 e migration 3→4. Se fallisce un leaf task, leggi tutto il suo report, correggi i blocker in batch e rilancia solo quel leaf task.
3. Quando i leaf gate sono verdi, fai **una sola** invocazione aggregata Gradle che copra test JVM + lint + `--no-configuration-cache assembleDebug`. Non usarla come inner loop e non ripetere un PASS.
4. QA Pixel solo `.qa`: overlay Alertness, baseline insufficiente, Health Connect presente/assente senza loggare dati personali, PVT attesa→stimolo→tap→annulla, fallback typing-only. Non installare sopra app reale.
5. Disinstalla sempre `.qa`. Commit/push solo schema + fix indispensabili; niente APK/cache/log/runtime DB. Registra nell'output lo SHA `origin/main` effettivamente verificato: sarà l'unico riferimento da usare nel task PH successivo.

PASS = test/lint/build + schema/migration + QA isolata + cleanup QA + SHA verificato/pushato. Health Connect può essere indisponibile se fallback è provato. **Dopo PASS il sottosistema standalone è chiuso: niente prompt successivi di micro-ottimizzazione o ri-validazione senza bug concreto.**

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 483217 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 483217`
Poi STOP: niente status/pull/log aggiuntivi sulla roadmap.

Output ≤6 righe: RESULT, SHA WordPulse verificato, gate, schema/migration, Pixel/HC/PVT+cleanup, blocker.
