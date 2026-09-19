PROMPT_ID=381904
PROJECT=Facilitatori di prompt
MODEL=GPT-5.6 Luna
REASONING=low
MEGAVAULT=FAST
REPO=gernalix/workflowy-importer

GOAL
Elimina i failure transienti di workflowy-roadmap-sync causati dal rate limit ufficiale di /nodes-export (1 richiesta/minuto), mantenendo il cockpit reattivo senza overengineering.

ACCEPTANCE
- timer roadmap-sync non può pianificare due export entro un minuto;
- usare OnUnitInactiveSec così il countdown parte dopo la fine del oneshot;
- una GET retry-safe che riceve 429 senza Retry-After aspetta una finestra prudente di 60s invece di esaurire backoff troppo presto;
- nessuna retry automatica per mutation POST;
- test mirato del fallback 429;
- CI PASS.
