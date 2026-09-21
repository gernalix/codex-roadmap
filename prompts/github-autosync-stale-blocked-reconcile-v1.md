PROMPT_ID=296843 | PARENT_PROMPT_ID=684217 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
WORKDIR=/home/daniele/projects/codex-roadmap

# Goal
Riconcilia SOLO lo stato canonico stale di 684217. Non rieseguire audit, test github-autosync, servizio systemd, pull-reliability work o runtime smoke: il lavoro sostanziale è già chiuso e verificato.

# Evidenza già verificata
- 684217 è canonically `blocked`; ultimo BLOCKED: `roadmap_start: start_claim_rejected:137:not_planned`.
- Lo stesso PROMPT_ID 684217 ha il prompt sostanziale già archiviato in `completed/github-autosync-pull-reliability.md`.
- Il follow-up di verifica 417806 dichiara esplicitamente di verificare i fix già implementati dopo 684217 ed è canonically `completed` con outcome PASS.
- Il commit `262598ffd4799d3f05ad1359f1fc46a698c24d32`, usato come baseline della verifica 417806, è ancora antenato di `gernalix/github-autosync/main` (main è avanti, non divergente).
- 684217 non ha fix/follow-up canonico registrato.

# Esecuzione minima
1. Avvia SOLO 296843 con `roadmap_start.py`; non tentare di avviare o rieseguire 684217.
2. Leggi SOLO i record canonici 684217 e 417806, il prompt completed di 684217 e la relazione Git minima necessaria. Niente audit repo-wide.
3. Determina perché l'ultimo start rifiutato ha lasciato 684217 `blocked` nonostante il lavoro completato e la verifica 417806 PASS.
4. Se la semantica canonica consente di rappresentare correttamente 684217 come `completed` sulla base dell'evidenza già registrata, applica la mutazione minima tramite single writer senza inventare nuove execution. Se il parent storico deve restare blocked, registra invece la chiusura/recovery canonica minima che impedisce ulteriori fix duplicati e documenta 417806 come recovery PASS.
5. Non modificare github-autosync salvo che emerga una prova concreta che il problema è nel codice runtime corrente; in assenza di tale prova, nessun code change.
6. Verifica idempotenza: un secondo reconcile deve essere no-op. Finalizza 296843 e STOP.

# Acceptance
PASS solo se la roadmap non presenta più 684217 come blocker azionabile non risolto, 417806 resta completed/PASS, nessun test/runtime github-autosync viene rieseguito, nessuna execution viene falsificata e un secondo reconcile non crea nuove mutazioni.

# Report
Massimo 6 righe: RESULT, ROOT_CAUSE, PARENT_684217, RECOVERY_417806, MUTATION, BLOCKER.
