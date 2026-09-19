PROMPT_ID=641582 | Repository=~/projects/workflowy-importer | MegaVault=FAST

# Goal
Trasforma Workflowy nel control surface operativo della roadmap Codex.

Workflowy NON deve diventare una seconda source of truth. La source of truth resta esclusivamente roadmap.sqlite del repository codex-roadmap. Workflowy deve essere una proiezione completa, aggiornata automaticamente.

# Obiettivo
Implementare `wf roadmap-sync` che legge il roadmap.sqlite canonico, senza usare roadmap.md o spiegazioni.md come sorgente, e importa automaticamente l'intera roadmap. Per ogni prompt importa PROMPT_ID, titolo, spiegazione, stato, progetto, modello, reasoning, queue_position, dipendenze, dipendenti, relazioni, fix, followup e replacement.

Crea automaticamente `Codex roadmap` con i gruppi Pending, Running, Completed, Failed, Blocked, Cancelled, Superseded e Unknown. Ogni prompt deve avere #roadmap, #status_xxx e #project_xxx e backlink Workflowy per dipendenze, dipendenti, fix, followup, replacement e related.

Sotto ciascun prompt riconosci esclusivamente `running`, `PASS` e `FAIL`; ignora qualunque altro testo e fallisci chiuso se più stati sono presenti. `running` invia la mutation canonica al single writer. `PASS` usa solo il lifecycle canonico esistente. `FAIL` invia la mutation e crea `Fix ChatGPT` con il testo richiesto.

Installa workflowy-roadmap-sync.service e workflowy-roadmap-sync.timer circa ogni 75 secondi, aggiorna README e AUTOMATIONS, rimuovi codice ridondante, porta CI completamente PASS, fai merge su main ed elimina i branch temporanei.

# Acceptance criteria
Roadmap completa importata; tag e backlink presenti; running/PASS/FAIL funzionanti; timer installato; README aggiornati; CI PASS; solo main rimasto.
