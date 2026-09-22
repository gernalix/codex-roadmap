PROMPT_ID=391742 | PARENT_PROMPT_ID=978216 | project_id=8 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
WORKDIR=/home/daniele/projects/codex-roadmap

# Goal
Riconcilia SOLO il BLOCKED storico 978216 con la recovery successiva del publisher Codex. Non rieseguire deploy, backfill globale, scansioni session archive o benchmark del publisher.

# Evidenza già verificata
- 978216 è canonically blocked, senza fix/follow-up; fix-packet: record recuperato ma `prompt_id_source` ancora mismatched dopo l'unico publisher run consentito.
- il work-state di 978216 punta a `be19be45f1c01e8ba21b311cdc17cd7d54072c17` in `gernalix/codex-usage-monitor`.
- 817264 ha poi chiuso autonomamente lo stesso sottosistema ed è `completed/PASS`; tra i fix PASS c'è `bdeda6a7dadbe47eace8fd67c9edde4039b4c970`, che preserva PROMPT_ID attraverso turn_context ripetuti.
- `bdeda6a7...` è ancora ancestor di `codex-usage-monitor/main`.

# Esecuzione minima
1. Avvia SOLO 391742 con `roadmap_start.py`; non riavviare 978216 o 817264.
2. Leggi SOLO i record canonici 978216 e 817264 e il codice/test direttamente responsabile della provenienza `prompt_id_source` se serve. Niente audit repo-wide.
3. Verifica con un fixture/test mirato già esistente, o con il minimo test aggiuntivo se manca, che l'attuale publisher assegni e rileggа coerentemente PROMPT_ID/source nel caso equivalente a 978216. Non fare un publisher run reale se il test deterministico basta.
4. Se il comportamento corrente è già corretto, non modificare codice: registra tramite single writer la recovery canonica minima che rende 978216 non più un blocker operativo, preservando la sua execution storica BLOCKED.
5. Modifica `codex-usage-monitor` SOLO se il mismatch è ancora riproducibile sul main corrente; fix minimo + test mirato, nessun refactor.
6. Verifica idempotenza: un secondo reconcile non produce nuove mutazioni. Finalizza 391742 e STOP.

# Acceptance
PASS solo se il caso `prompt_id_source` equivalente a 978216 è coerente sul codice corrente, 817264 resta completed/PASS, la execution storica di 978216 non viene falsificata, nessun deploy/backfill globale viene ripetuto e il secondo reconcile è no-op.

# Report
Massimo 6 righe: RESULT, ROOT_CAUSE, PARENT_978216, CURRENT_BEHAVIOR, MUTATION_OR_CODE, BLOCKER.