PROMPT_ID=223103 | PARENT_PROMPT_ID=593728 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Chiudi in un'unica integrazione i branch già preparati `feature/shared-alerts-place-tags` e `chatgpt/918274-runtime-restore`: runtime profile restore sicuro, tag Places indipendenti da Timer, alert condivisi Timer/Places, alert Places su check-in/out manuali, direct-tap link-only e bridge Tasker opzionale.

# Starting point
- repo `/home/daniele/projects/PersonalHub`;
- candidate minimo `d79251ce17695e310bdafe0919475c6786545464`;
- runtime-fix minimo `dd5f7ed51e16be5256b4fbed1c626edf36d0d439`, limitato a ProfileRuntimeCoordinator/HubSettings/test;
- esegui solo dopo 223679 PASS.

# Esecuzione minima
1. Un solo fetch mirato dei due branch + main. Continua sul branch shared-alerts; integra prima l'ultimo main e poi il runtime-fix nel candidate. Mai modificare main come workspace e non acquisire lease durante implementazione.
2. Preserva l'hardening Profili e non resuscitare codice Timer eliminato da main. Usa CODE_MAP + `docs/ALERTS.md`; niente audit repo-wide.
3. Verifica/genera lo schema Room necessario e i migration test. Gate host mirati per `:core:alerts`, Places, Timer e database; compile fino a `:app` solo dopo i leaf PASS.
4. Copertura obbligatoria: namespace TimerTag/PlaceTag separati; Places ANY/ALL; target place UUID esatto; CHECK_IN/CHECK_OUT/BOTH; one-time/cooldown; eventi Places solo manuali (non Geofence); direct-tap solo link-only `http|https|workflowy`; mixed text/unsafe scheme non auto-aprono; Tasker resta opzionale e package-scoped.
5. Dopo branch-local PASS, incrementa `version.txt` esattamente una volta rispetto al canonical base integrato. Push candidate + PR.
6. Passa a integratore nella stessa sessione: acquisisci lease, refresh main una volta, integration_context + review semantica, poi QA `Pixel_8a` via facade. Correggi compatibilità solo sul candidate.
7. Merge/push solo dopo PASS; elimina `feature/shared-alerts-place-tags` e, quando il suo diff è contenuto in main, anche `chatgpt/918274-runtime-restore`; rilascia lease. Nessuna release/Pixel fisico.

# Acceptance / stop
PASS con migration/FK, host+AVD, semantica alert e branch cleanup tutti PASS, e un solo bump versione. Finalizza PROMPT_ID 223103; failure terminali via roadmap_result. Output max 8 righe.
