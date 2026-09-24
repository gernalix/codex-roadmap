PROMPT_ID=697920
PARENT_PROMPT_ID=199166
PROJECT_ID=92

# Goal
Rendi ChatGPTExporter una sorgente live molto più resiliente per ChatGPT Web, senza trasformare prompt-history in uno scraper e senza rendere l'export ufficiale OpenAI una dipendenza runtime. Implementa e valida gli hardening emersi dall'analisi 199166, mantenendo gli export esistenti immutati.

# Contesto già verificato — non riscoprirlo
- Runtime locale upstream: ~/.local/share/prompt-history/upstream/ChatGPTExporter
- Upstream/pin attuale: siraht/ChatGPTExporter@c5618b3cc06eeb5b273d3727fe8729071441f291
- prompt-history: /home/daniele/projects/prompt-history
- Archivio reale: /home/daniele/Documents/ChatGPT/ChatGPTExport-4dd6389abca763a639b4a330914cc8e0
- Report 199166:
  ~/.local/share/prompt-history/reports/openai-vs-chatgpt-exporter-199166.md
  ~/.local/share/prompt-history/reports/openai-vs-chatgpt-exporter-199166.json
- 199166 ha misurato: inventory Exporter 7108, complete 6680, 428 non complete; OpenAI recupera 416 di quelle 428; restano 12 ID solo inventory Exporter. Asset: 826 media senza byte falliscono in entrambe le fonti.
- Questi numeri sono evidenza iniziale, non acceptance da riconfermare con una nuova scansione completa.
- prompt-history è DERIVATO/rebuildable: non trasformarlo in fonte canonica né copiarvi endpoint/auth ChatGPT privati.
- L'export ufficiale OpenAI resta backfill/reconciliation occasionale, NON requisito del collector live.

# Regole di scope/efficienza
1. Leggi AGENTS.md e docs/UPSTREAM_INTEGRATIONS.md di prompt-history e i file direttamente pertinenti di ChatGPTExporter: capture engine, provider adapter/bridge, asset downloader, journal/audit/dashboard, test. Niente esplorazione generale.
2. Riusa report 199166 e fixture/test esistenti. Non ripetere il confronto da 2.4 GB né una capture completa 7108-chat.
3. Non modificare né cancellare gli export OpenAI/ChatGPTExporter esistenti.
4. Non introdurre token/cookie/credenziali in file, log, Git o messaggi.
5. Niente refactor/cleanup/modernizzazione fuori scope. Segnala problemi laterali senza investigarli salvo blocco.
6. Test mirati prima; allarga solo se un failure/rischio concreto lo richiede. Dopo PASS, STOP.

# A. Rendere durevoli le modifiche a ChatGPTExporter
- Non lasciare patch importanti solo nel checkout locale.
- Se non esiste già un fork scrivibile dell'utente, crea con gh un fork/repository durevole di siraht/ChatGPTExporter sotto gernalix mantenendo upstream separato; parti dal pin verificato. Non aprire PR verso siraht.
- Tutto l'hardening deve essere commit/pushato nel fork o, se il fork non è tecnicamente creabile, termina BLOCKED prima di lasciare modifiche non durevoli.
- Conserva licenza/attribuzione upstream.
- Dopo l'hardening, aggiorna prompt-history per pin/documentare la revisione durevole effettivamente usata; non cambiare pin prima che build/test del fork siano PASS.

# B. Retry/recovery conversazioni
Implementa solo ciò che manca già:
- coda persistente dei record incompleti/retryable, ricostruibile dai journal/marker e resistente a chiusura dashboard/service-worker/Chrome;
- retry automatici bounded con backoff e Retry-After per rete, 429 e 5xx;
- refresh della sessione/token secondo l'architettura page-world esistente quando l'autenticazione temporanea scade, senza persistere token;
- fallback conversation batch -> detail individuale -> shared detail quando semanticamente applicabile;
- checkpoint atomico dopo progressi utili, così un crash non ricomincia il lavoro riuscito;
- nessun retry infinito e nessun retry identico senza nuova condizione/evidenza.

Classifica ogni failure in una categoria stabile almeno tra:
retryable_network, rate_limited, auth_refresh_required, schema_drift, access_denied, provider_not_found_or_gone, malformed_provider_payload, local_io, unknown.
unknown non può essere considerato terminale senza evidenza.

# C. Asset/media
- Per asset con URL/sessione temporanei, prima di dichiarare failure prova a riottenere descriptor/sessione firmata con il flusso provider già autorizzato, poi retry bounded.
- Rispetta Retry-After/backoff anche per asset.
- Conserva hash/size e dedup content-addressed già esistenti.
- Distingui chiaramente provider_unavailable/gone da bug/transient capture.
- I ~826 media mancanti in entrambe le fonti NON devono causare retry infinito: dopo evidenza sufficiente possono diventare terminali provider-unavailable, mantenendo descriptor/provenance.

# D. Semantica di completamento e audit
- complete solo se non restano conversazioni attese incomplete/retryable/unclassified.
- conversations_complete_assets_partial solo quando tutte le conversazioni recuperabili sono complete e gli unici residui sono asset esplicitamente terminali/indisponibili.
- Se restano conversazioni terminali non recuperabili, il report deve distinguerle da failure operative e non mascherarle come successo pieno.
- validation.json/md deve includere conteggi per failure_class, retry backlog, terminal provider failures e first/last attempt senza dati privati.
- Aggiungi/aggiorna un piccolo health/status JSON machine-readable con: last successful progress, inventory/complete/backlog counts, failure classes, schema/auth state e versione build. Scrittura atomica; niente contenuti conversazionali.

# E. I 12 inventory-only
Usa SOLO richieste mirate/revalidation per i 12 ID residui, se l'autenticazione live è disponibile senza azioni distruttive.
Classifica ciascun caso in aggregate counts: captured, provider_not_found/gone, access_denied, schema_drift, retryable, unknown.
Non stampare gli ID nel report finale.
La mancata possibilità tecnica/policy di pilotare chrome-extension:// non è da sola un failure del codice: usa test core/fixture e percorsi consentiti. Non aggirare policy browser.

# F. prompt-history
Aggiorna solo l'integrazione necessaria:
- pin/documentazione al fork/revisione verificata;
- ChatGPTExporter = sorgente live primaria; export OpenAI = backfill/reconciliation facoltativo;
- sync deve poter funzionare con il solo collector live + Codex source; non deve richiedere entrambi;
- preserva provenance quando lo stesso conversation/message compare da più fonti senza duplicare il prompt logico. Se oggi la provenance viene sovrascritta, aggiungi il minimo schema/adapter necessario in modo rebuildable, con test; non trasformare il DB derivato in archivio canonico.
- Mantieni la stessa identità logica chatgpt:<conversation>:<message> per convergenza.

# G. Test obbligatori mirati
ChatGPTExporter:
- retry 429 + Retry-After;
- transient 5xx/network -> retry -> success;
- auth expiry -> refresh -> success senza token persistito;
- batch failure -> individual fallback;
- resume da journal/backlog dopo restart;
- signed asset refresh -> success;
- provider-gone asset/conversation -> terminal classification;
- schema drift -> fail closed, non complete;
- audit non produce complete con backlog conversazioni;
- nessun file temporaneo/zero-byte viene marcato complete.

prompt-history:
- entrambe le fonti convergono sullo stesso prompt_uid;
- provenance di OpenAI + Exporter viene preservata;
- sync funziona con solo Exporter e con solo OpenAI fallback;
- pin/docs coerenti con revisione realmente buildata.

Esegui build extension e test mirati. Non fare full browser-history export.

# Runtime cutover
Solo dopo build/test PASS:
- installa/aggiorna la build locale del fork nel path già usato dal runtime, preservando configurazione e directory handle;
- non fare logout/login, reset profilo Chrome o cancellazione dati;
- esegui revalidate dell'archivio esistente e, se consentito dal runtime corrente, un retry mirato dei soli residui; niente full recapture;
- verifica che un riavvio innocuo del componente necessario non perda backlog/progress.
Se l'estensione unpacked richiede un reload manuale che Codex non può effettuare, prepara tutto e riportalo come singolo prerequisito manuale; non creare workaround di controllo browser vietati.

# Acceptance
PASS solo se:
- hardening durevole nel fork scrivibile e pin prompt-history aggiornato alla revisione testata;
- retry/resume/classificazione/audit/health hanno test mirati PASS;
- nessun retryable/unclassified viene trattato come terminal success;
- asset terminali provider-unavailable non causano loop infinito;
- provenance multi-fonte in prompt-history non viene persa;
- runtime continua a NON dipendere dall'export OpenAI;
- nessun export sorgente o dato Chrome viene distruttivamente modificato.

Finalizza tramite il flusso roadmap canonico per PROMPT_ID 697920. Output massimo 12 righe:
PROMPT_ID, RESULT, EXPORTER_FORK, EXPORTER_COMMIT, PROMPT_HISTORY_COMMIT, RETRY_ENGINE, FAILURE_CLASSES, ASSET_RECOVERY, INVENTORY_ONLY_12, AUDIT_HEALTH, RUNTIME_CUTOVER, BLOCKER.