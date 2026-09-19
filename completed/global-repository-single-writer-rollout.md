PROMPT_ID=642913 | project=GitHub Autosync | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Completa il rollout locale del generic per-repository single writer già mergiato:
- github-autosync main >= e08944664c6190ba1222dd4948d9f981624c0086
- codex-roadmap main >= c9aabeea3a6aba99581eb86b75a00d111e2f0163

Il risultato finale deve essere: ogni repo Git attivo usa main/master come branch canonico single-writer; ogni task Codex/ChatGPT usa un worktree+task branch isolato; github-reconcile integra serialmente le PR [single-writer]; codex-roadmap mantiene il suo writer dedicato; github-autosync non invia alcuna notifica Telegram e Kuma resta l'unico monitor operativo.

# Scope
Solo rollout/verifica locale e fix strettamente necessari nello stesso failure domain. Nessun audit generale o refactor.
Usa il worktree_path restituito da roadmap_start per eventuali modifiche al codice; non lavorare direttamente sul main canonico.

# Esecuzione
1. Verifica che il claim abbia restituito worktree_path/task_branch per questo task; se manca, diagnostica il bridge roadmap_start -> repo-task e correggi il minimo necessario.
2. Assicurati che i checkout canonici locali di github-autosync e codex-roadmap siano aggiornati ai commit sopra tramite i rispettivi reconciler sicuri; non bypassare i guard.
3. Esegui da ~/projects/github-autosync:
   - python3 install_systemd.py
   - un github-reconcile reale
   - un secondo github-reconcile per idempotenza.
4. Verifica che il timer user sia enabled/active, cadenza 1 minuto, lingering attivo e ultimo service run sano.
5. Verifica per tutti i repository Git attivi scoperti da github-reconcile/MegaVault:
   - codex-roadmap usa il guard dedicato;
   - ogni altro canonical branch ha il generic single-writer guard installato;
   - il canonical checkout non viene usato come worker;
   - repo-task start crea worktree/branch separati e task concorrenti sullo stesso repo possono coesistere.
   Usa fixture/temp repo per smoke distruttivi; non creare modifiche inutili sui repo reali.
6. Verifica il bridge roadmap:
   - roadmap_start alloca automaticamente task/<PROMPT_ID> per task Git;
   - roadmap_finish attende integrazione writer/CI prima di PASS;
   - task validation-only/no-diff chiude come no-op senza PR vuota;
   - worktree/branch puliti vengono rimossi dopo merge; lavoro sporco post-merge non viene force-deleted.
7. Conferma che github-autosync non contiene/invoca alcun sender Telegram e che il servizio non produce notifiche Telegram. Non eliminare integrazioni Telegram appartenenti ad altri servizi.
8. Verifica Uptime Kuma: unico monitor Push "Fedora GitHub Reconcile" (attuale #46 se invariato), attivo e heartbeat reale UP. Nessun duplicato.
9. Esegui solo test mirati se emerge un difetto; altrimenti riusa CI già PASS. Se modifichi codice, test mirati -> suite repo -> CI, poi lascia che il single writer integri.

# Acceptance
PASS solo se:
- tutti i repo attivi sono protetti/gestibili dal single-writer appropriato;
- 2+ task sullo stesso repo possono avere worktree distinti senza condividere checkout;
- main/master è serializzato e non scrivibile direttamente dagli agenti;
- github-reconcile continua a girare ogni minuto ed è idempotente;
- zero notifiche Telegram originate da github-autosync;
- Kuma Push è UP;
- nessun dato/lavoro locale perso.

Finalizza con roadmap_finish.py; il PASS deve avvenire solo dopo l'integrazione del task branch (o no-op validato).

Output max 10 righe, prima riga PROMPT_ID=642913:
RESULT, REPOS, WORKTREES, WRITERS, ROADMAP_BRIDGE, SYSTEMD, TELEGRAM, KUMA, TESTS, BLOCKER.
