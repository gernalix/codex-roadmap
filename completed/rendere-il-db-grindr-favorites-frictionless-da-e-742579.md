PROMPT_ID=742579

# Obiettivo
Rendi il DB di gernalix/grindr-favorites-monitor realmente intuitivo e frictionless da esplorare a mano in DB Browser, senza sacrificare correttezza, storia o compatibilità.

# Contesto verificato
- C2 work item: wi:05ef765b5715478797f3e1c2ddcef851.
- Repo: gernalix/grindr-favorites-monitor.
- DB live: ~/.local/state/grindr-favorites-monitor/state.sqlite.
- La regressione DB Browser precedente (PROMPT_ID 366587) è completed e merged: le view esistenti sono ora compatibili con SQLCipher/SQLite 3.39.2.
- DB Browser 3.13.1 usa libsqlcipher/SQLite 3.39.2; questo è il floor di compatibilità.
- Schema attuale include almeno favorites, scan_meta/history, profiles, profile_aliases, profile_snapshots + append-only changes/link, lookup fk_profile_*, media tables, outbox/defav e view enriched_profiles, unavailable_profiles, profile_media_paths_by_profile.
- I dati live devono essere preservati integralmente.

# Goal
Fai un audit end-to-end del modello dati e implementa un human-facing schema/view layer che renda la consultazione manuale semplice anche senza conoscere ID interni, JSON path o codici numerici.

# Requisiti
1. Prima inventaria il DB live in sola lettura: tabelle, colonne, PK/FK, indici, trigger, view, cardinalità e relazioni implicite. Identifica solo problemi reali di navigabilità/integrità.
2. Normalizza o aggiungi FK REALI dove la relazione è semanticamente stabile e migliora integrità/navigazione. Non introdurre FK artificiali che impediscano stati legittimi. Se una tabella esistente va ricostruita per aggiungere FK, usa migrazione transazionale/idempotente con row-preservation verificata.
3. Usa un'entità profilo canonica coerente dove opportuno e collega tabelle profile-scoped senza duplicare identità. Valuta favorites, aliases, fetch hints, snapshots, outbox, defav, media links e altre tabelle reali.
4. I codici enum già presenti nelle lookup tables devono essere leggibili nelle view. Non perdere il valore raw: quando utile mostra sia label sia code.
5. Mantieni la storia append-only; nessuna perdita/riscrittura distruttiva di snapshot, changes o media.
6. Crea un set PICCOLO ma completo di view human-facing, con nomi autoesplicativi e SQL compatibile con 3.39.2, pensate per DB Browser. Devono coprire almeno:
   - quadro profilo/favorite corrente, alias, disponibilità/missing ed ultimo enrichment;
   - ultimo snapshot con campi ad alto valore estratti/leggibili + JSON raw;
   - timeline/storico modifiche con timestamp/profilo/alias/path/old/new leggibili;
   - media per profilo con stato/path e contesto profilo;
   - scans/availability history in forma leggibile;
   - eventuali altre combinazioni ad alto valore che emergono dai dati reali (es. de-fav/outbox) solo se utili.
7. Le view devono minimizzare la necessità di join manuali e ID tecnici. Se un ID è utile per lookup/debug, mantenerlo come colonna ma non come unica informazione.
8. Valuta indici solo sulla base delle query/view reali; aggiungi solo quelli giustificati.
9. Aggiorna/centralizza migrate() affinché lo schema/view contract sia idempotente e aggiorni installazioni esistenti. Compatibilità minima: SQLCipher/SQLite 3.39.2 + SQLite moderno.
10. Test:
    - regressioni schema/FK/view;
    - PRAGMA foreign_key_check=[];
    - row counts/dati preservati prima/dopo;
    - migrate() due volte = stesso risultato semantico;
    - tutte le human views interrogabili con /usr/bin/sqlcipher 3.39.2;
    - suite repo completa.
11. Integra l'exact tested head secondo il single-writer del repo.
12. Solo DOPO merge del codice, crea un backup timestamped sicuro del DB live (fuori Git), applica la migrazione canonica al DB live e verifica:
    - integrity_check=ok;
    - foreign_key_check vuoto;
    - cardinalità fondamentali preservate;
    - tutte le human views queryabili con sqlite3 moderno e sqlcipher 3.39.2;
    - campioni leggibili/semanticamente coerenti.
13. Documenta nel README una sezione breve "Human-readable database views": quali view aprire in DB Browser e cosa mostrano.
14. Chiudi il task via terminal protocol C2 solo quando codice merged + DB live migrato/verificato.

# Vincoli
- Scope solo grindr-favorites-monitor; nessun altro repo Grindr.
- Non cancellare/azzerare il DB live.
- Nessuna modifica diretta a main.
- Non esporre segreti o contenuto sensibile nei log/commit.
- Non fare polling modello su CI: checkpoint e stop; il supervisor riprenderà sulla transizione.
- Evita overengineering: ogni tabella/FK/view/indice nuovo deve avere un beneficio concreto di integrità o consultazione manuale.

# Report finale
PROMPT_ID=<id>
RESULT=PASS|BLOCKED|FAIL
SCHEMA=<summary>
HUMAN_VIEWS=<names>
TESTS=<summary>
LIVE_DB=<summary>
C2_RESULT=<json compatto>
