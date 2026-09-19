PROMPT_ID=947306
PROJECT_ID=96
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=FAST
WORKDIR=/home/daniele/projects/workflowy-importer

# Goal
Completa SOLO il pezzo runtime locale che ChatGPT non può fare: per i prompt che la dashboard Workflowy porta a BLOCKED o FAIL, recupera automaticamente il report finale Codex corrispondente e rendi disponibile a ChatGPT un fix-packet minimale tramite la roadmap canonica/single writer.

# Starting point
- workflowy-importer main deve già contenere la dashboard compatta R/P/B/F e i marker #needs_fix; non reimplementarli.
- roadmap.sqlite resta l’unica source of truth; ogni scrittura canonica passa dal single writer esistente.
- Riusa il session archive/codex-usage publisher e gli identificatori PROMPT_ID già esistenti. Parti dai file/servizi direttamente pertinenti; niente audit generale dei repo.
- Non pubblicare transcript completi, secret, token, path sensibili non necessari o contenuto estraneo al blocker.

# Implementazione minima
1. Individua la fonte locale autorevole già usata per associare una sessione Codex a PROMPT_ID e al suo report finale.
2. Quando un PROMPT_ID entra in blocked/failed e ha origine/marker Workflowy, estrai SOLO: outcome, blocker/failure concreto, stato del lavoro (branch/PR/commit se presenti) e prossima azione utile.
3. Pubblica questo fix-packet idempotentemente nella roadmap usando il single writer e lo schema autorevole già disponibile; non introdurre una seconda source of truth. Se serve un piccolo hook in codex-usage-monitor, modifica solo quello strettamente necessario.
4. Il dato pubblicato deve essere sufficiente perché un client ChatGPT/GitHub generi un prompt correttivo senza che l’utente reincolli il report Codex.
5. Deduplica per PROMPT_ID + esecuzione/report: nessun doppione a ogni timer run.

# Vincoli risparmia-token
- Scope stretto; niente refactor/cleanup/modernizzazioni fuori scope.
- Riusa MegaVault/AGENTS.md e risultati già verificati.
- Nessun retry identico senza nuova evidenza.
- Test mirati soltanto ai parser/publisher/dedup/single-writer coinvolti; amplia solo se un failure lo richiede.
- Non eseguire smoke Workflowy reale se non indispensabile al nuovo hook.
- Stop immediato quando acceptance criteria sono PASS.

# Acceptance
- Un fixture/report BLOCKED e uno FAIL producono fix-packet corretti e sanitizzati.
- Un secondo passaggio identico non pubblica nulla di nuovo.
- PASS/R non producono fix-packet.
- Ogni write roadmap passa dal single writer.
- Servizio/timer locale interessato resta healthy.
- Output finale conciso: RESULT, file/repo modificati, test, dove ChatGPT può leggere il fix-packet, blocker eventuale.
