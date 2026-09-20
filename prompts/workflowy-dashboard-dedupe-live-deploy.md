PROMPT_ID=843271 | project=workflowy-importer | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal
Distribuisci sul Fedora reale il fix già mergeato di deduplica della dashboard Workflowy e verifica che la proiezione torni idempotente senza righe duplicate.

# Starting point
- repo: /home/daniele/projects/workflowy-importer
- upstream main deve includere commit 72dd84ddabe4f43a0ace2e9cc18525da022d5278 (PR #19)
- CI GitHub Actions run 35500517727 è PASS su Python 3.11 e 3.13: NON rieseguire suite equivalenti complete in locale.
- Root cause già corretta nel codice: export Workflowy temporaneamente incompleto o perdita della mapping cache potevano far ricreare nodi prompt già esistenti; il fix verifica i mapped node direttamente, riscopre root/gruppi esistenti e deduplica i prompt preservandone i figli.
- Il repository contiene già il percorso/helper di deploy runtime: riusalo, non ridisegnare la feature.

# Task
1. Scope stretto: controlla solo stato del repo, percorso di deploy e runtime Workflowy pertinenti. Niente audit repo-wide.
2. Porta il checkout locale al main corrente solo con fast-forward sicuro. Se ci sono modifiche locali non correlate che impediscono il fast-forward, termina BLOCKED senza sovrascriverle.
3. Distribuisci una sola volta il main contenente 72dd84ddabe4f43a0ace2e9cc18525da022d5278 usando il percorso canonico già esistente.
4. Esegui/attendi una sync reale della dashboard.
5. Verifica sullo stato Workflowy reale:
   - esiste un solo nodo generato per ogni PROMPT_ID canonico sotto i gruppi Codex;
   - i conteggi dei gruppi corrispondono ai prompt canonici;
   - 381904 e 257387 non compaiono più ripetuti;
   - una seconda sync non ricrea duplicati;
   - eventuali figli/comandi di stato dei nodi deduplicati sono stati preservati.
6. Riporta le metriche della sync, incluso duplicates_deleted quando disponibile, e il commit effettivamente distribuito.

# Acceptance
PASS solo se il runtime usa il commit richiesto, la dashboard live è deduplicata e una seconda sync resta idempotente.
Se credenziali/API/systemd/stato locale bloccano il deploy, riporta BLOCKED con blocker concreto. Non modificare altro codice salvo una regressione concreta del commit mergeato dimostrata dal runtime.

# Vincoli
- SOLO il minimo necessario.
- Non esplorare repository non pertinenti.
- Non fare refactor, cleanup, modernizzazioni o fix collaterali.
- Non ripetere comandi/test equivalenti senza nuova evidenza.
- Ferma il task subito dopo il PASS.
- Output finale conciso: PROMPT_ID, RESULT, DEPLOYED_SHA, SYNC_1, SYNC_2, DUPLICATES, BLOCKER se presente.
