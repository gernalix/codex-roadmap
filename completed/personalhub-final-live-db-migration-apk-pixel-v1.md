PROMPT_ID=913264

# Goal
Porta il Pixel principale allo stato PersonalHub finale usando ESATTAMENTE gli artefatti congelati da 788606, con rollback completo e migrazione esterna one-shot del DB reale.

# Precondizione
- parte solo dopo 788606 PASS;
- usa FINAL_HEAD, schema/identity, APK/AAB path+SHA e release manifest di 788606;
- non modificare sorgenti e non ricostruire artefatti salvo file mancante/corrotto; in quel solo caso ricostruisci lo stesso FINAL_HEAD/config e verifica lo stesso SHA atteso o registra il nuovo rebuild come blocker;
- usa sempre seriale ADB esplicito.

# Esecuzione ottimizzata
1. Verifica una volta release manifest/artifact SHA e che non esistano integrazioni PH sorgente pendenti.
2. Risolvi il Pixel fisico e blocca altra QA PH sul device durante il cutover.
3. Prima di modificare app o DB, crea rollback immutabile: APK/riferimento ripristinabile, personalhub.db + sidecar coerenti, SHA-256 e manifest package/version/schema. Mai uninstall/clear-data.
4. Su COPIA del DB reale leggi user_version, Room identity, quick_check, FK e inventario/row-count/hash delle tabelle user-data. Stato ambiguo => BLOCKED senza modifica live.
5. Migra solo in staging locale fino allo schema/identity congelati da 788606, riusando migratori esterni esistenti; transizioni aggiuntive certe possono usare script temporanei /tmp. Mai destructive fallback o solo PRAGMA user_version.
6. Richiedi target schema+identity esatti, quick_check=ok, FK vuoto e preservazione verificata dei dati; solo allora sostituisci il DB live con percorso reversibile.
7. Installa l'APK ESATTO di 788606 senza wipe; verifica SHA/versione/readback.
8. Avvia Home e enumera dinamicamente ogni modulo user-facing dalla registry finale; aprili tutti con dati reali, incluse History/Search e le surface P0. Zero crash/FATAL/Room mismatch.
9. Se replacement/install/primo avvio falliscono, ripristina rollback e termina BLOCKED con causa precisa; niente retry identici.
10. Dopo PASS conserva rollback locale, registra evidenze finali e termina. Nessuna build/test release duplicata.

# Acceptance
PASS solo se DB live = schema/identity finali validi, rollback completo esiste, integrità/FK/preservazione dati PASS, APK installato ha hash esatto del preflight e Home + tutti i moduli finali aprono con dati preservati senza crash.
