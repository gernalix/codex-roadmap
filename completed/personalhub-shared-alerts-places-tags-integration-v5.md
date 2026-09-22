PROMPT_ID=380812 | PARENT_PROMPT_ID=663657 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Riprendi e chiudi 663657 senza ripetere il lavoro già verificato: integra in PersonalHub i branch esistenti `feature/shared-alerts-place-tags` e `chatgpt/918274-runtime-restore`, poi valida e porta tutto in `main`.

# Stato già verificato
- 663657 si è fermato per orchestrazione prima della vera integrazione: non trattarlo come failure del codice prodotto.
- Non dipendere dallo stato roadmap di 418844. La PR capsule #14 è già in main e il branch remoto `feature/100-capsule-isolation` risulta già assente.
- `feature/shared-alerts-place-tags` contiene almeno `d79251ce17695e310bdafe0919475c6786545464`.
- `chatgpt/918274-runtime-restore` contiene almeno `dd5f7ed51e16be5256b4fbed1c626edf36d0d439`.
- Riusa CODE_MAP, `docs/ALERTS.md` e risultati già verificati nella sessione. Niente audit repo-wide.

# Esecuzione minima
1. Un solo fetch mirato di `main` e dei due branch. Se esiste ancora solo localmente `feature/100-capsule-isolation`, eliminalo esclusivamente se è completamente contenuto in `origin/main`; non ricrearlo e non rifare il lavoro capsule.
2. Continua sul candidate shared-alerts; integra una volta l'ultimo `origin/main`, poi integra solo il diff runtime necessario da `chatgpt/918274-runtime-restore` (ProfileRuntimeCoordinator, HubSettings e test). Non lavorare direttamente su main durante implementazione.
3. Preserva l'hardening Profili e non resuscitare codice Timer eliminato da main. Mantieni distinti TimerTag e PlaceTag.
4. Verifica/genera solo lo schema Room e i migration test necessari. Esegui gate host mirati per database, `:core:alerts`, Places e Timer; compila `:app` solo dopo i leaf PASS. Niente test equivalenti/ridondanti.
5. Verifica: Places ANY/ALL; target place UUID esatto; CHECK_IN/CHECK_OUT/BOTH; one-time/cooldown; eventi Places solo manuali; direct-tap solo per messaggio composto esclusivamente da `http|https|workflowy`; mixed text/unsafe scheme non auto-aprono; bridge Tasker opzionale e package-scoped.
6. Dopo branch-local PASS, incrementa `version.txt` esattamente una volta rispetto alla base canonica integrata. Push candidate + PR.
7. Acquisisci il lease solo per l'integrazione finale. Refresh main una volta, review semantica mirata e QA `Pixel_8a` via facade. Correggi solo incompatibilità necessarie sul candidate.
8. Merge/push solo dopo PASS. Elimina i branch `feature/shared-alerts-place-tags` e `chatgpt/918274-runtime-restore` quando completamente contenuti in main; rilascia lease. Nessuna release e nessun Pixel fisico.

# Acceptance / stop
PASS solo con migration/FK, gate host, QA AVD, semantica alert, un solo bump versione e cleanup branch tutti PASS. Finalizza PROMPT_ID 380812. Se emerge un blocker nuovo e concreto, termina BLOCKED con evidenza minima; niente esplorazione ulteriore. Output finale max 8 righe.
