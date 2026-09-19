PROMPT_ID=811925 | PARENT_PROMPT_ID=918536 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STANDARD

# Goal
Completa il Data Explorer Datasette Lite di PersonalHub: runtime realmente offline, semantica FK/Context/temporal equivalente al server e UI mobile PH-specifica. Dopo integrazione esegui una sola build/delivery dell'APK debug canonico.

# Precondizioni
- esegui dopo 825405 PASS e 904631 PASS;
- repo `/home/daniele/projects/PersonalHub`;
- `personalhub_read` server resta riferimento semantico, ma il runtime Lite deve funzionare senza rete.

# Esecuzione minima
1. Crea branch dedicato dal current main. Usa solo CODE_MAP `database.data_explorer`, docs Data Explorer e i leaf Luoghi già noti; niente audit generale.
2. Vendorizza/pinna Datasette Lite + Pyodide/wheel/assets necessari; nessuna CDN/runtime fetch. Usa detached snapshot validato/read-only.
3. Proiezione locale: FK native cross-modulo, Context graph simmetrico/deduplicato con provenance, temporal graph separato con suppression quando FK/Context spiega già la coppia; WordPulse usa burst, People solo eventi/initiative.
4. Presentazione embedded mantiene table/row/filter/facet/pagination/SQL/FK e aggiunge solo mobile UX necessaria: Related vs Temporal separate, high prima/medium collassate, touch/light-dark; nessun bypass write.
5. Gate mirati: regression check-in Luoghi pre-localizzato; test snapshot/read-only/FK/Context/temporal/Lite offline; compile Data Explorer/app. Niente riesecuzione dei gate Git History già PASS salvo boundary toccato.
6. Bump `version.txt` una volta rispetto al base. Push/PR.
7. Acquisisci lease; latest-main semantic review + QA `Pixel_8a` offline/online bounded, incluse navigation e regressione Luoghi. Merge/delete branch solo dopo PASS.
8. Dopo merge costruisci una sola volta l'APK debug firmato canonico; non ricompilarlo. Installa quello stesso artifact sul Pixel fisico con helper canonico e consegnalo col canale PH previsto. Rilascia lease.

# Acceptance / stop
PASS con Lite self-contained, semantica relazionale/temporale equivalente, read-only, UI mobile/Places regression PASS, un solo bump e stesso APK testato/installato/consegnato. Finalizza PROMPT_ID 811925. Output max 8 righe.
