PROMPT_ID=199166
PARENT_PROMPT_ID=254859
PROJECT_ID=92
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT_MODE=FAST
REPO=gernalix/prompt-history
WORKDIR=/home/daniele/projects/prompt-history

# Goal
Confronta direttamente il file ufficiale OpenAI selezionato dall'utente:
  /home/daniele/Downloads/export chatgpt.zip
con il più recente archivio reale ChatGPTExporter sotto:
  /home/daniele/Documents/ChatGPT/ChatGPTExport-*
e stabilisci quale dei due conserva più informazione e se alcuni dati vadano recuperati da una fonte per integrare l'altra/canonical store.

NON assumere che l'export OpenAI sia più completo perché ufficiale e NON assumere che ChatGPTExporter sia più ricco perché ha un formato più dettagliato: misura i dati realmente presenti.

# Contesto già verificato
- Il task 254859 ha trovato nell'ultimo ChatGPTExporter: inventory=7108 conversazioni attese, 6680 complete, 428 capture fallite; audit terminalState=incomplete.
- Sono stati osservati anche asset partial/failed; non usare questi numeri come sostituto della nuova verifica.
- 254859 è stato interrotto dall'utente: questo è un task autonomo. Non continuare la sua lunga ingest.
- Esiste anche /home/daniele/Downloads/openai chatgpt export.zip: NON usarlo al posto del file selezionato salvo che tu dimostri prima con hash che è byte-identico a /home/daniele/Downloads/export chatgpt.zip.

# Vincoli di efficienza
- Avvia con roadmap_start.py per 199166 e usa il worktree restituito.
- Non fare audit generale del repository.
- Non estrarre alla cieca 2.4 GB. Parti da central directory/zipinfo e usa lettura streaming (zipfile/unzip -p/ijson se già disponibile) o estrai solo i membri necessari.
- Evita di caricare interi JSON enormi in RAM se possono essere processati in streaming.
- Una sola scansione completa dei payload quando possibile; riusa inventari/hash già calcolati.
- Nessun retry identico senza nuova evidenza.
- Non stampare testi di chat, nomi/allegati privati o ID completi non necessari.
- Non modificare i due export sorgente.

# Analisi richiesta

## A. Inventario dei due formati reali
Per OpenAI ZIP e ChatGPTExporter costruisci un inventario strutturato di categorie e sottocategorie effettivamente presenti, con evidenza di path/field/schema e conteggi dove sensato. Includi almeno:
- conversazioni e ID;
- messaggi, ruoli, timestamp, modelli/autori;
- struttura ad albero, parent/child, branch e selezione del ramo;
- titoli e metadati conversazione;
- progetti/workspace/shared links se presenti;
- citazioni, URL, search/tool metadata se presenti;
- file caricati dall'utente;
- immagini/media generati;
- altri allegati/asset;
- metadati asset: nome, MIME, dimensione, hash, collegamento al messaggio;
- dati account/preferences/memory/GPTs o altre categorie non-conversazionali, se presenti;
- raw provider/API responses o altra evidenza grezza;
- manifest, hash, completion markers, audit/validation/provenance.

## B. Tre liste obbligatorie
Produci esattamente queste tre sezioni nel report:

1. DATI PRESENTI IN ENTRAMBI
   - Inserisci qui solo il nucleo semanticamente equivalente presente in entrambe le fonti.
   - Se entrambi hanno "attachments" ma uno conserva campi aggiuntivi, metti il nucleo comune qui e i campi extra nella lista esclusiva corretta.
   - Indica per ogni voce se la fedeltà è davvero equivalente oppure se uno dei due è più ricco.

2. DATI PRESENTI SOLO NELL'EXPORT UFFICIALE OPENAI
   - Categorie/sottocategorie o payload realmente assenti da ChatGPTExporter.
   - Distingui "assente per design" da "assente perché il run Exporter è incompleto".

3. DATI PRESENTI SOLO IN CHATGPTEXPORTER
   - Categorie/sottocategorie o payload realmente assenti dallo ZIP OpenAI.
   - Distingui dati originali di ChatGPT da metadati derivati dall'Exporter (hash, audit, Markdown, completion markers, ecc.): i derivati non vanno confusi con informazione utente aggiuntiva.

## C. Completezza reale delle conversazioni
- Conta le conversazioni OpenAI in modo affidabile anche se conversations.json è splittato.
- Confronta gli ID con inventory 7108 e set complete 6680 dell'Exporter.
- Determina quante delle 428 conversazioni mancanti nell'Exporter sono presenti nello ZIP OpenAI.
- Quantifica anche:
  OpenAI ∩ Exporter-complete,
  OpenAI-only,
  Exporter-only,
  inventory-Exporter non presente in OpenAI.
- Considera differenze temporali/scope prima di chiamare un record "mancante".

## D. Completezza reale di file/media
- Risolvi i riferimenti agli asset nel JSON OpenAI contro i membri ZIP effettivi.
- Per ChatGPTExporter usa assets indexes/record reali.
- Conta almeno: riferimenti logici, file fisici, missing/failed/zero-byte quando verificabili.
- Verifica se foto/upload/generated images presenti in una fonte sono realmente recuperabili nell'altra; non basarti solo sul fatto che esista un URL o un descriptor.

## E. Verdetto e strategia di integrazione
Fornisci una conclusione netta ma motivata su:
- quale fonte è più completa per DATI ORIGINALI ChatGPT;
- quale è più ricca per METADATI/PROVENANCE derivati;
- se una sola fonte può sostituire l'altra;
- oppure se serve una strategia ibrida.

Per ogni categoria non coperta dalla fonte scelta come primaria indica:
- SOURCE -> DESTINATION consigliata;
- cosa importare esattamente;
- chiave di dedup/merge consigliata;
- rischio di perdita/duplicazione;
- se il dato può essere ricostruito oppure deve essere preservato dalla sorgente.

"Destination" preferita è prompt-history o un nuovo canonical merged archive, NON la modifica distruttiva dell'export OpenAI o ChatGPTExporter originale.

# Output persistente
Scrivi atomicamente, senza contenuti privati:
- ~/.local/share/prompt-history/reports/openai-vs-chatgpt-exporter-199166.md
- ~/.local/share/prompt-history/reports/openai-vs-chatgpt-exporter-199166.json

Il Markdown deve contenere le 3 liste richieste + matrice di conteggi + verdetto + piano SOURCE→DESTINATION.
Il JSON deve essere machine-readable e includere categorie, evidence paths, counts, overlap sets solo come conteggi/hash (non dump di ID privati).

# Modifiche codice
Task principalmente read-only. Modifica prompt-history solo se è strettamente necessario per ottenere un confronto corretto e riutilizzabile; altrimenti usa script temporanei fuori repo. Niente refactor/cleanup.
Non avviare alcuna importazione/merge dei dati: questo task decide COSA importare e da dove. L'esecuzione dell'integrazione sarà un task successivo separato.

# Acceptance
PASS solo se:
- lo ZIP selezionato è stato ispezionato realmente ed è integro abbastanza da analizzarlo;
- il ChatGPTExporter reale è stato confrontato;
- le 3 liste sono complete e supportate da evidenza;
- overlap/missing conversations sono quantificati;
- file/media sono verificati fisicamente, non solo per schema;
- il verdetto distingue dati originali da metadata derivati;
- esiste un piano preciso SOURCE→DESTINATION per ogni lacuna utile;
- nessun export sorgente è stato modificato.

Finalizza con roadmap_finish.py sullo stesso PROMPT_ID.
Output finale conciso: PROMPT_ID, RESULT, OPENAI_ARCHIVE, EXPORTER_ARCHIVE, CONVERSATION_MATRIX, ASSET_MATRIX, PRIMARY_SOURCE, UNIQUE_OPENAI, UNIQUE_EXPORTER, MERGE_PLAN, REPORTS, BLOCKER.