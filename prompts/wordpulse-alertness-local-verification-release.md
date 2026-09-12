[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=483217 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD | type=Prompt`

# Goal
Finalizza localmente l'Alertness/Fatigue già implementato in `gernalix/wordpulse`: genera schema Room 4 con toolchain reale, verifica migration/build e fai una QA Pixel **solo package `.qa`**. Correggi solo failure concrete.

# Fatti autoritativi
Checkout `/home/daniele/projects/wordpulse`; feature già presente: typing metrics, fatigue 0..100/alertness, baseline, Health Connect sleep opzionale, PVT 3 min, migration 3→4, backup/import/UI/test. Manca intenzionalmente `app/schemas/com.wordpulse.app.data.WordPulseDatabase/4.json`: va generato da Room/KSP, mai scritto a mano.

# Esegui
1. Un solo fetch/pull fast-forward di `origin/main`; lavoro locale incompatibile => `BLOCKED`, niente stash/reset/force.
2. Un'unica invocazione Gradle che copra test JVM + lint + `--no-configuration-cache assembleDebug`; non ripetere gate PASS.
3. Verifica/genera schema 4 + migration 3→4. Su FAIL, fix minimo nel file direttamente coinvolto; niente audit/refactor generale e niente retry identico senza nuova evidenza.
4. QA Pixel solo `.qa`: overlay Alertness, baseline insufficiente, Health Connect presente/assente senza loggare dati personali, PVT attesa→stimolo→tap→annulla, fallback typing-only. Non installare sopra app reale.
5. Disinstalla sempre `.qa`. Commit/push solo schema + fix indispensabili; niente APK/cache/log/runtime DB.

PASS = test/lint/build + schema/migration + QA isolata + cleanup QA; Health Connect può essere indisponibile se fallback è provato.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 483217 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 483217`
Poi STOP.

Output ≤6 righe: RESULT, SHA, gate, schema/migration, Pixel/HC/PVT+cleanup, blocker.
