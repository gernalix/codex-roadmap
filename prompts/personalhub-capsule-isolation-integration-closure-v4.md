PROMPT_ID=223679 | PARENT_PROMPT_ID=284916 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Chiudi l'anomalia lasciata da 284916: integra in modo semantico il lavoro già verificato di `feature/100-capsule-isolation` nel `main` corrente, preservando i commit CI successivi di main, poi elimina il branch. Non reimplementare la feature.

# Starting point
- repo: `/home/daniele/projects/PersonalHub`;
- baseline main minima: `748c0284f3f59da68aa4721c2dc46179ff00b637`;
- baseline candidate minima: `d334ba0339033f8ffa8f1e1381e644de49a45948`;
- al momento della revisione il branch è 24 commit avanti e 2 indietro rispetto a main e contiene già `version.txt=51`;
- scope noto: manifest dei moduli, boundary checker/docs, launcher shortcuts, Hub module wiring e test/helper relativi.

# Esecuzione minima
1. Un solo fetch di main + candidate. Lavora sul candidate, mai su main come workspace. Integra l'ultimo main nel branch e risolvi solo overlap in-scope preservando sia isolamento capsule sia CI/unit/emulator aggiunte a main.
2. Usa CODE_MAP/symbol search mirato; niente audit generale.
3. Gate branch-local minimi: `python3 tools/check_architecture_boundaries.py`; test mirati di Hub/module routing/shortcut; `:app:compileDebugKotlin`. Esegui solo i leaf aggiuntivi indicati da failure reali.
4. Non applicare un secondo bump versione: il bump della feature è già nel candidate. Non decrementare una versione canonica eventualmente più avanzata.
5. Push candidate e apri/aggiorna PR. Solo ora acquisisci il lease PH, aggiorna main una volta, usa `tools/personalhub_integration_context.py --branch feature/100-capsule-isolation` e fai review semantica del diff contro il main corrente.
6. Se l'integrazione invalida gate pertinenti, correggi sul candidate e rilancia solo quelli. Esegui QA AVD condivisa solo se richiesta dai cambi manifest/shortcut, tramite `tools/android_emulator_control.py`.
7. Merge/push nel canonical solo dopo PASS; elimina subito branch remoto+locale; rilascia lease in ogni esito. Nessuna release/Pixel/delivery.

# Acceptance / stop
PASS solo se main contiene il lavoro capsule + i commit successivi preesistenti, architecture/compile/test pertinenti PASS, nessun secondo bump, e `feature/100-capsule-isolation` è assente locale/remoto.
Finalizza con roadmap_finish PROMPT_ID 223679; BLOCKED/FAIL con roadmap_result. Output max 7 righe.
