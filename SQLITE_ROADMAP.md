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

`roadmap_finish.py` resta compatibile ed equivale a `PASS`. Il comando non modifica più il DB o Git locale: usa `gh api` per creare una richiesta immutabile nella inbox remota. Per ogni PROMPT_ID esiste una sola chiave terminale; un retry identico è idempotente, mentre un esito terminale diverso con la stessa chiave viene rifiutato. GitHub Actions applica la richiesta al DB canonico e rigenera le viste. Le righe di `executions` continuano a provenire dai dati reali di `codex-usage`, evitando doppi conteggi.

Prima dell'import ogni prompt attivo deve avere una fingerprint della propria materializzazione. Se un vecchio `PROMPT_ID` ricompare con testo diverso, il sistema registra una collisione e non sovrascrive automaticamente lo stato del prompt corrente.

Sul Fedora reale, `codex-roadmap-sync.timer` legge periodicamente `~/projects/codex-usage/prompts/*/metrics.json`, scarica in sola lettura il DB remoto per sapere quali `cycle_key` sono già presenti e consegna soltanto le nuove esecuzioni come mutazioni `usage_execution`. Non modifica più il DB/Git locale. Il single writer remoto conserva anche il controllo della fingerprint: in caso di mismatch registra il conflitto di identità senza cambiare automaticamente lo stato del prompt. Il sync importa solo metadati; non copia prompt completi, risposte finali o path raw delle sessioni nel repository pubblico. `import_codex_usage.py` resta disponibile per backfill/manutenzione manuale, non come writer periodico.

### ChatGPT

ChatGPT crea richieste JSON univoche in `mutations/inbox/` e non modifica direttamente `roadmap.sqlite` o le viste generate. GitHub Actions applica le operazioni in transazione, rigenera le viste e archivia la richiesta in `mutations/applied/`.

### Single writer

Il workflow `Apply roadmap mutations` usa un'unica coda di concorrenza GitHub Actions. È l'unico componente autorizzato nel flusso normale a modificare il DB canonico e le sue proiezioni. ChatGPT, Codex e il sync `codex-usage` producono richieste indipendenti; la serializzazione avviene soltanto al momento dell'applicazione. Le CLI che mutano direttamente il DB restano solo strumenti di manutenzione eccezionale e non vanno usate durante l'esecuzione ordinaria della roadmap.

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

Quando ChatGPT aggiunge sia il file `prompts/<slug>.md` sia la relativa mutazione `register`, i due artefatti vanno preferibilmente pubblicati nello stesso commit. In questo modo la CI non osserva per pochi secondi un file prompt ancora assente dal database. Se una mutazione viene applicata da GitHub Actions subito dopo un commit separato, la vista generata finale resta autorevole; il controllo successivo va eseguito sul nuovo HEAD prodotto dall'azione.

