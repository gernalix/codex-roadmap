PROMPT_ID=111265 | PARENT_PROMPT_ID=521404 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST

# Goal
Chiudi esclusivamente la PR PersonalHub #15 già implementata e mergeable. Non rifare feature, migrazioni o gate host già superati.

# Stato verificato
- repo: /home/daniele/projects/PersonalHub;
- PR #15 è OPEN/mergeable;
- head corrente verificato: d17c4aa3143cd122451e99ee9201e9012e71cc9c;
- l'ultimo fix ha reso AlertLinkPolicy JVM-safe;
- Architecture boundaries è già PASS; gli altri workflow del nuovo head erano ancora in progress;
- version.txt è già stato aggiornato: nessun nuovo bump.

# Esecuzione minima
1. roadmap_start e un solo refresh PR/main. Se head è avanzato, usa quello corrente.
2. Non rilanciare test host già PASS. Attendi/leggi una volta i check del PR head corrente. Per un failure apri solo job/step fallito, correggi solo regressione del candidate e riesegui il gate pertinente.
3. Esegui solo la QA AVD mancante su Pixel_8a via facade: avvio, profile switch, Places tags/alert, Timer regression minima, link-only http|https|workflowy diretto, mixed/unsafe non auto-open. Nessun Pixel fisico.
4. Acquisisci lease solo per QA/integrazione; recupera solo lock scaduti con helper canonico. Un lock vivo di altro task è l'unico blocker locale ammesso.
5. Con check richiesti + AVD verdi, refresh main una volta, merge PR #15 e verifica containment.
6. Elimina i branch shared-alerts/runtime-restore solo se contenuti in main; rilascia lease sempre.

# Acceptance
PASS solo con PR #15 merged, check richiesti PASS, AVD scope PASS, main contiene head PR e branch cleanup completato. Nessuna release, redesign o audit. Stop immediato dopo PASS.
