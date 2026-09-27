PROMPT_ID=625582

Implementa SOLO il work item C2 assegnato sulla UX foto/profile_id di grindr-favorites-monitor.

Requisiti:
- ogni foto profilo scaricata deve avere naming stabile/deterministico che includa chiaramente il profile_id ed eventuali metadati già necessari ai flussi esistenti;
- il profile_id deve essere ricavabile direttamente dal filename/titolo del viewer con attrito minimo; EXIF/XMP solo come fallback sicuro, senza introdurre dipendenze fragili;
- aggiungi una piccola azione/script Nautilus che, partendo da una foto scaricata, estragga il profile_id dal filename e apra direttamente il profilo corrispondente nel Datasette configurato;
- mapping foto→profile_id univoco e stabile; backfill/rinomina delle foto esistenti solo se conservativo, idempotente e senza perdita/dedup break;
- riusa convenzioni e primitive esistenti; niente UI/DB paralleli o refactor estranei.

Verifica con test mirati del naming/parser/backfill e dello script/azione; preserva compatibilità runtime. Commit+push del checkpoint verificato. Usa il percorso repo single-writer già assegnato; non modificare roadmap.sqlite direttamente.

Alla fine integra tramite il percorso canonico del repo e terminalizza PROMPT_ID con roadmap_finish.py. Se emerge un problema incidentale, cattura solo la descrizione con c2_issue_capture.py e continua.
