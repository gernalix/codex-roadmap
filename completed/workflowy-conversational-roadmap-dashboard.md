PROMPT_ID=764381
PROJECT=Facilitatori di prompt
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=FAST
REPO=gernalix/workflowy-importer

GOAL
Rendere la dashboard Workflowy conversazionale e immediatamente comprensibile senza trasformarla in un sistema complesso.

ACCEPTANCE
- Ogni prompt mostra in cima una breve frase umana su cosa sta succedendo e cosa fare.
- Link Chrome/Codex mancanti vengono descritti esplicitamente con domanda/azione: es. 'Mi manca il link Codex. Vuoi aggiungerlo?'.
- BLOCKED/FAIL mostrano un riassunto umano del problema e un prossimo passo concreto, usando il fix-packet canonico quando disponibile.
- Se non c'è fix-packet, fallback semplice e veritiero, senza inventare una causa.
- Running/Integration/Waiting/Ready/Done hanno messaggi brevi e non invadenti.
- Fix-packet B/F viene pubblicato automaticamente quando disponibile, anche senza comando manuale B/F in Workflowy.
- Struttura visuale usa formati Workflowy ufficiali: root H1, gruppi H2, problemi H3, titoli in grassetto.
- Nessuna proliferazione di casi speciali o frasi per ogni possibile errore.
- Test mirati + CI PASS.