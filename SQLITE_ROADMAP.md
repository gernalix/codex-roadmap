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

Un PASS ordinario viene chiuso autorevolmente da `roadmap_finish.py`; `executions` aggiunge poi telemetria automatica senza trattenere lo scheduling. Non si crea un'analisi dedicata, un file audit o un follow-up salvo failure, retry, costo/tool-call anomali, conflitto/loop osservato, bug infrastrutturale o richiesta esplicita.

Questo evita che il sistema di misurazione generi più lavoro del task misurato.

## Scrittori

### Codex

Prima di iniziare qualunque lavoro sostanziale per un task della roadmap, Codex acquisisce un claim remoto:

```bash
python3 tools/roadmap_start.py --repo . --prompt-id 123456
```

Il client crea una mutation `pending -> running`, aspetta che il single writer l'abbia applicata e verifica il DB remoto. Se il prompt è già terminale o il claim non arriva a `running`, fallisce chiuso e Codex non deve iniziare il task.

Una volta `running`, il prompt è **writer-locked** per le mutation che possono cambiare l'esecuzione: stato, modello, ordine, dipendenze, tag, relazioni, testo canonico e altri metadati operativi non possono essere modificati. `explanation` è l'unica eccezione: è testo puramente user-facing della dashboard e può essere chiarito anche durante l'esecuzione. Il file resta in `prompts/` e le viste generate continuano a mostrarlo come `running`.

Il risultato immediato viene consegnato da:

```bash
python3 tools/roadmap_result.py --repo . --prompt-id 123456 --result PASS --confirm-executed
```

`roadmap_finish.py` resta compatibile ed equivale a `PASS`. Il comando non modifica il DB o Git locale: crea una GitHub Issue immutabile `[roadmap-mutation] terminal-<PROMPT_ID>`. Il single writer registra la `terminal_request` e applica **subito** lo stato terminale richiesto; su PASS i figli diventano immediatamente lanciabili quando le altre dipendenze sono soddisfatte. `usage_execution` arriva in seguito per costi/audit e non è più un prerequisito di scheduling. Se telemetria e richiesta terminale divergono, viene registrata l'anomalia senza riaprire automaticamente il prompt. Per ogni PROMPT_ID esiste una sola chiave terminale; un retry identico è idempotente, mentre un esito terminale diverso viene rifiutato.

Prima dell'import ogni prompt attivo deve avere una fingerprint della propria materializzazione. Se un vecchio `PROMPT_ID` ricompare con testo diverso, il sistema registra una collisione e non sovrascrive automaticamente lo stato del prompt corrente.

Sul Fedora reale, `codex-roadmap-sync.timer` legge periodicamente `~/projects/codex-usage/prompts/*/metrics.json`, scarica in sola lettura il DB remoto per sapere quali `cycle_key` sono già presenti e consegna soltanto le nuove esecuzioni come mutazioni `usage_execution`. Non modifica più il DB/Git locale. Il single writer remoto conserva anche il controllo della fingerprint: in caso di mismatch registra il conflitto di identità senza cambiare automaticamente lo stato del prompt. Il sync importa solo metadati; non copia prompt completi, risposte finali o path raw delle sessioni nel repository pubblico. `import_codex_usage.py` è ora solo un wrapper di compatibilità che delega allo stesso `roadmap_sync.py`: non apre né modifica più il DB locale.

### ChatGPT

ChatGPT crea una GitHub Issue per ogni richiesta, con titolo `[roadmap-mutation] <request_key>` e body contenente direttamente il documento JSON `codex-roadmap.mutation.v1`. Non committa file di inbox, DB, prompt o viste. Per una `register`, `prompt_text` e `current_path` viaggiano nella stessa Issue e il writer materializza il file `prompts/...`.

Per un **nuovo** prompt, la `register` non può essere il primo passo: ChatGPT deve prima ottenere un ID dal registry canonico MegaVault. Da remoto usa `gernalix/MegaVault:.github/prompt-id-request.json` con `command=allocate` e attende che `.github/prompt-id-response.json` riporti lo stesso `request_id`, un PROMPT_ID di sei cifre e `status=allocated`. Solo allora invia la mutation `register`. Dopo che il single writer ha materializzato il file canonico, ChatGPT invia al bridge MegaVault `command=materialize` con il `content_url` esatto del file su `codex-roadmap/main` e attende `status=materialized`.

Una Issue normale o `[plan]` non è parte del writer e non soddisfa mai una richiesta di inserimento/aggiornamento roadmap. Se ChatGPT crea per errore una Issue informativa al posto della mutation, deve correggere con il percorso canonico e poi chiudere l'Issue errata come superseded. Non può dire all'utente che il prompt è stato aggiunto finché writer roadmap e materializzazione MegaVault non sono entrambi confermati.

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

Operazioni supportate: `analysis`, `code_change`, `model`, `explanation`, `status`, `terminal_request`, `reconcile_terminals`, `relation`, `dependency`, `dependency_replace`, `tag`, `execution`, `register`. Il writer esegue inoltre una riconciliazione terminale automatica a ogni Issue, così richieste terminali lasciate da versioni precedenti non restano zombie `running`. Relazioni `fix`/`replacement`/`merge` inoltrano automaticamente le dipendenze dei figli pending; `replacement`/`merge` supersedono automaticamente la sorgente pending. Le transizioni di stato sono fail-closed: un prompt terminale non torna attivo e un prompt `running` non può essere portato a `superseded` da una mutation successiva. `model` aggiorna esclusivamente il modello assegnato al prompt esistente ed è bloccato mentre il prompt è `running`; `explanation` aggiorna esclusivamente la spiegazione user-facing mostrata nelle viste generate ed è ammessa anche durante `running`, perché non altera il task. La spiegazione deve essere una o due frasi semplici, comprensibili senza conoscenze di programmazione e prive di dettagli tecnici non necessari. Entrambe registrano l'audit dell'operazione. `analysis` e `code_change` sono usate solo per eccezioni reali; `code_change` si collega di default all’ultima analisi del PROMPT_ID e registra repository, tipo di intervento, commit opzionale e riepilogo.

## Proiezioni generate

- `roadmap.md`: coda operativa;
- `spiegazioni.md`: tabella semplice dei pendenti con eseguibilità corrente calcolata da dipendenze e prerequisiti manuali registrati;
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

