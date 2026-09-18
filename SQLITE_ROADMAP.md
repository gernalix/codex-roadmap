# Roadmap SQLite

`roadmap.sqlite` è la **source of truth** dei metadati della roadmap.

I file Markdown non si modificano a mano per cambiare lo stato della roadmap: sono proiezioni generate dal database.

## Cosa viene tracciato

Per ogni `PROMPT_ID`:

- identità immutabile, titolo, progetto/repository, modello, reasoning, MegaVault mode e posizione in coda;
- stato corrente: `pending`, `running`, `completed`, `failed`, `blocked`, `cancelled`, `superseded`, `unknown`;
- dipendenze e relazioni (`parent`, `fix`, `followup`, `replacement`, `split`, `merge`, `related`);
- tag e artefatti;
- ogni esecuzione Codex con start/end, outcome, durata, modello, reasoning, tool-call e token quando disponibili;
- le analisi ChatGPT **solo quando esiste un'eccezione reale** (failure, anomalia, retry, bug infrastrutturale o richiesta esplicita), inclusi eventuali colli di bottiglia e PROMPT_ID del fix;
- le eventuali modifiche di codice fatte da ChatGPT dopo un'analisi eccezionale, separate per repository/tipo/commit;
- cronologia dei cambi di stato e audit degli aggiornamenti;
- collisioni sospette di PROMPT_ID/materializzazione.

## Politica exception-driven

Le tabelle `analyses` e `analysis_code_changes` sono storiche/opzionali: non rappresentano una checklist da completare per ogni prompt.

Un PASS ordinario viene chiuso usando la telemetria automatica di `executions`. Non si crea un'analisi dedicata, un file audit o un follow-up salvo failure, retry, costo/tool-call anomali, conflitto/loop osservato, bug infrastrutturale o richiesta esplicita.

Questo evita che il sistema di misurazione generi più lavoro del task misurato.

## Scrittori

### Codex

Il risultato immediato viene consegnato da:

```bash
python3 tools/roadmap_result.py --repo . --prompt-id 123456 --result PASS --confirm-executed
```

`roadmap_finish.py` resta compatibile ed equivale a `PASS`. Il comando non modifica più il DB o Git locale: crea una GitHub Issue immutabile `[roadmap-mutation] terminal-<PROMPT_ID>`. Per ogni PROMPT_ID esiste una sola chiave terminale; un retry identico è idempotente, mentre un esito terminale diverso con la stessa chiave viene rifiutato. GitHub Actions applica la richiesta al DB canonico, rigenera le viste e chiude la Issue. Le righe di `executions` continuano a provenire dai dati reali di `codex-usage`, evitando doppi conteggi.

Prima dell'import ogni prompt attivo deve avere una fingerprint della propria materializzazione. Se un vecchio `PROMPT_ID` ricompare con testo diverso, il sistema registra una collisione e non sovrascrive automaticamente lo stato del prompt corrente.

Sul Fedora reale, `codex-roadmap-sync.timer` legge periodicamente `~/projects/codex-usage/prompts/*/metrics.json`, scarica in sola lettura il DB remoto per sapere quali `cycle_key` sono già presenti e consegna soltanto le nuove esecuzioni come mutazioni `usage_execution`. Non modifica più il DB/Git locale. Il single writer remoto conserva anche il controllo della fingerprint: in caso di mismatch registra il conflitto di identità senza cambiare automaticamente lo stato del prompt. Il sync importa solo metadati; non copia prompt completi, risposte finali o path raw delle sessioni nel repository pubblico. `import_codex_usage.py` è ora solo un wrapper di compatibilità che delega allo stesso `roadmap_sync.py`: non apre né modifica più il DB locale.

### ChatGPT

ChatGPT crea una GitHub Issue per ogni richiesta, con titolo `[roadmap-mutation] <request_key>` e body contenente direttamente il documento JSON `codex-roadmap.mutation.v1`. Non committa file di inbox, DB, prompt o viste. Per una `register`, `prompt_text` e `current_path` viaggiano nella stessa Issue e il writer materializza il file `prompts/...`.

### Single writer

Il workflow `Apply roadmap mutation Issues` usa un'unica coda di concorrenza GitHub Actions. È l'unico componente autorizzato nel flusso normale a modificare il DB canonico, i prompt materializzati e le proiezioni. Ogni run elenca e drena tutte le mutation Issue ancora aperte, quindi una run pending cancellata dalla semantica di concurrency di GitHub non perde la richiesta: la Issue resta open e il run successivo la applica. Il DB registra una receipt per `request_key`, quindi retry e Issue duplicate identiche sono idempotenti. Una Issue con payload invalido/collisione viene rollbackata, commentata e chiusa `not_planned`; il drain continua sulle altre Issue invece di avvelenare l'intera coda. Dopo push riuscito il workflow commenta e chiude tutte le Issue valide drenate. Gli entry point operativi che in passato mutavano direttamente il DB sono bloccati o convertiti in client del writer. Il percorso ordinario e quello usato da ChatGPT/Codex è sempre mutation Issue → GitHub Actions single writer; i soli hook diretti residui sono interni/test-only.

Formato:

```json
{
  "schema": "codex-roadmap.mutation.v1",
  "actor": "chatgpt",
  "operations": [
    {
      "op": "analysis",
      "prompt_id": "123456",
      "bottlenecks_found": true,
      "summary": "Sintesi",
      "fix_prompt_id": "654321"
    }
  ]
}
```

Operazioni supportate: `analysis`, `code_change`, `status`, `relation`, `dependency`, `dependency_replace`, `tag`, `execution`, `register`. `analysis` e `code_change` sono usate solo per eccezioni reali; `code_change` si collega di default all’ultima analisi del PROMPT_ID e registra repository, tipo di intervento, commit opzionale e riepilogo.

## Proiezioni generate

- `roadmap.md`: coda operativa;
- `spiegazioni.md`: tabella semplice dei pendenti;
- `prompt-registry.md`: tabella completa;
- `obsidian/Prompts/`: una nota per PROMPT_ID;
- `obsidian/Projects/`: viste per progetto;
- `obsidian/Dashboards/`: task lanciabili e task che richiedono attenzione.

Le note Obsidian usano wikilink, backlink e tag per stato/progetto. Le relazioni sono quindi navigabili in entrambe le direzioni.

## Regola PROMPT_ID

`1 prompt materializzato = 1 PROMPT_ID unico e immutabile`.

Un prompt concluso `FAIL/BLOCKED` non viene rilanciato con lo stesso ID. Viene archiviato in `falliti/`; un eventuale fix è un nuovo prompt con nuovo ID e relazione `fix` o `followup`.

## Verifica

```bash
python3 tools/roadmap_db.py --repo . verify
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

`PRAGMA foreign_key_check` deve restare vuoto.

## Inserimento remoto di un nuovo prompt

ChatGPT non crea più il file prompt con un commit separato. La Issue `register` contiene `current_path` e `prompt_text`; il single writer crea `prompts/<slug>.md`, registra la fingerprint nel DB e rigenera tutte le viste nello stesso commit autorevole.

