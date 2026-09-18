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
- ogni analisi ChatGPT, inclusi presenza di colli di bottiglia e PROMPT_ID del fix;
- le modifiche di codice fatte da ChatGPT dopo un’analisi, separate per repository/tipo/commit;
- cronologia dei cambi di stato e audit degli aggiornamenti;
- collisioni sospette di PROMPT_ID/materializzazione.

## Scrittori

### Codex

Il risultato immediato viene registrato da:

```bash
python3 tools/roadmap_result.py --repo . --prompt-id 123456 --result PASS --confirm-executed
```

`roadmap_finish.py` resta compatibile ed equivale a `PASS`. Questo aggiornamento immediato modifica stato/audit ma **non** inventa una seconda esecuzione: le righe di `executions` vengono alimentate dai dati reali di `codex-usage`, evitando doppi conteggi.

Prima dell'import ogni prompt attivo deve avere una fingerprint della propria materializzazione. Se un vecchio `PROMPT_ID` ricompare con testo diverso, il sistema registra una collisione e non sovrascrive automaticamente lo stato del prompt corrente.

Sul Fedora reale, `codex-roadmap-sync.timer` riconcilia periodicamente `~/projects/codex-usage/prompts/*/metrics.json`. È la fonte per timestamp e metriche reali e permette il backfill storico. Importa solo metadati; non copia prompt completi, risposte finali o path raw delle sessioni nel repository pubblico.

### ChatGPT

ChatGPT può creare un file JSON in `mutations/inbox/`. GitHub Actions applica le operazioni in transazione, rigenera le viste e archivia la richiesta in `mutations/applied/`.

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

Operazioni supportate: `analysis`, `code_change`, `status`, `relation`, `dependency`, `tag`, `execution`, `register`. `code_change` si collega di default all’ultima analisi del PROMPT_ID e registra repository, tipo di intervento, commit opzionale e riepilogo.

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
