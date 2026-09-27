PROMPT_ID=366587

# Obiettivo
Correggi la regressione per cui le view umane di grindr-favorites-monitor risultano vuote/non consultabili in DB Browser for SQLite.

# Root cause già riprodotta
DB live: ~/.local/state/grindr-favorites-monitor/state.sqlite
- sqlite3 CLI usa SQLite 3.50.6 e vede:
  - enriched_profiles = 42 righe
  - profile_media_paths_by_profile = 4 righe
  - unavailable_profiles = 2 righe
- DB Browser 3.13.1 è linkato a libsqlcipher 3.39.2.
- Con /usr/bin/sqlcipher sullo stesso DB: SELECT count(*) FROM enriched_profiles fallisce con:
  no such function: json_pretty
- enriched_profiles usa json_pretty(r.snapshot_json); unavailable_profiles dipende da enriched_profiles.
- src/grindr_favorites_monitor/history.py crea enriched_profiles con CREATE VIEW IF NOT EXISTS, quindi cambiare solo il SQL non migra la view già esistente.

# Lavoro
1. Aggiungi test regressivi che rendano evidente che le view non devono dipendere da funzioni SQLite >3.39 necessarie solo alla presentazione.
2. Rendi enriched_profiles compatibile con SQLite/SQLCipher 3.39.2 mantenendo il campo details utile e JSON valido; non introdurre pseudo-pretty-print SQL fragile.
3. Rendi migrate() idempotente e capace di aggiornare le view già esistenti nel DB live. Gestisci correttamente la dipendenza unavailable_profiles -> enriched_profiles durante DROP/CREATE.
4. Mantieni invariati dati, FK, append-only history e profile_media_paths_by_profile.
5. Aggiorna README solo se il contratto utente “formatted JSON” cambia.
6. Esegui test focalizzati e suite pertinente.
7. Migra il DB live ~/.local/state/grindr-favorites-monitor/state.sqlite con un backup sicuro se il percorso di migrazione del progetto non lo fa già.
8. Verifica sul DB live con ENTRAMBI i motori:
   - sqlite3
   - sqlcipher 3.39.2
   che enriched_profiles, unavailable_profiles e profile_media_paths_by_profile siano interrogabili e restituiscano conteggi coerenti; niente hardcode dei conteggi nei test.
9. Integra il commit verificato nel repo secondo il normale percorso Git/C2 e chiudi il work item.

# Vincoli
- Non modificare altri repo Grindr.
- Non toccare i dati storico/profilo se non tramite la migrazione canonica del progetto.
- Nessuna perdita di snapshot/media/history.
- Nessun polling modello per CI: se serve attendere, checkpoint e termina il turn.

# Report finale
RESULT=PASS|BLOCKED|FAIL
COMMIT=<sha>
LIVE_DB=PASS|FAIL
SQLCIPHER_3_39=PASS|FAIL
TESTS=<summary>
