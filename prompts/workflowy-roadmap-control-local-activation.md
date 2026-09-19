PROMPT_ID=578439
PROJECT=workflowy-importer
MODEL=GPT-5.6 Luna
REASONING=low
MEGAVAULT=FAST
WORKDIR=/home/daniele/projects/workflowy-importer

Goal
Attivare sul ThinkPad il bridge gia implementato che proietta automaticamente l'intera codex-roadmap in Workflowy e rileva i figli esatti running/PASS/FAIL.

Starting point autoritativo
- Repo: /home/daniele/projects/workflowy-importer
- main remoto contiene il merge 7ce528fb19a2952daca627f80c4cfd47f74b3e0e.
- Unit: deploy/systemd/workflowy-roadmap-sync.service e .timer.
- CLI: wf roadmap-sync.
- La roadmap canonica resta gernaIix/codex-roadmap/roadmap.sqlite; il bridge invia solo mutation Issue al single writer.

Scope
1. Porta il checkout locale di workflowy-importer a origin/main senza refactor/cleanup.
2. Assicurati che la .venv usi il codice corrente (pip install -e . solo se necessario).
3. Installa/aggiorna le due user unit roadmap-sync in ~/.config/systemd/user, daemon-reload e abilita/avvia il timer.
4. Esegui una volta wf roadmap-sync.
5. Verifica via Workflowy API/CLI che esistano: root "Codex roadmap #roadmap", gruppi di stato, nodi PROMPT_ID con tag stato/progetto e note con link reciproci per almeno una dipendenza reale.
6. Verifica systemctl --user che il timer sia enabled+active e che l'ultimo service run sia PASS.
7. NON creare running/PASS/FAIL sotto prompt reali durante lo smoke: non modificare stati canonici solo per testare.
8. Se emerge un problema locale direttamente collegato, correggilo nel repo, esegui test mirati e pusha su main; niente lavoro fuori scope.

Acceptance criteria
- wf roadmap-sync termina 0 sul Workflowy reale.
- proiezione completa presente e navigabile con tag/link.
- workflowy-roadmap-sync.timer enabled e active.
- nessuna mutation di stato di prompt reali generata dallo smoke.
- git status finale pulito; eventuali fix pushati.
- Prima riga del report finale: PROMPT_ID=578439
- Poi RESULT: PASS, BLOCKED o FAIL con evidenza concisa.
- Stop immediato al PASS.
