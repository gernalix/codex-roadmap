PROMPT_ID=684930 | project_id=49 | campaign_id=ph-obsidian-archive | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD


# Contratto Git/integrazione PH aggiornato — prevale su ogni istruzione successiva incompatibile
- `main` è baseline/target finale, non area di implementazione. Qualunque riferimento successivo a “branch obbligatorio main”, “lavora su main”, “push main”, “non creare PR”, “mantieni il branch separato” o equivalenti è superato da questo contratto.
- Se il task parte già da un branch feature nominato nel prompt, continua su QUEL branch. Altrimenti crea/usa il branch dedicato `codex/684930-obsidian-archive-projections` dal più recente `origin/main`.
- Durante implementazione/fix branch-local NON acquisire il lock PH. Esegui i gate host branch-local necessari e pusha solo il branch candidato.
- Quando il branch è pronto, apri/aggiorna una PR verso `main`. A quel punto la stessa sessione può diventare integratore: acquisisci `tools/personalhub_task_lock.py`, fai un solo refresh di `origin/main`, usa `tools/personalhub_integration_context.py --branch <branch>`, rileggi il diff rispetto al main corrente e valuta semanticamente le interazioni. Un merge Git senza conflitti non basta.
- Se servono fix di compatibilità, applicali SOLO sul branch candidato e rilancia i gate pertinenti. Ambiguità sostanziale/out-of-scope => BLOCKED senza toccare `main`.
- Solo dopo review semantica + gate pertinenti PASS, integra la PR in `main`, pusha il canonico, elimina subito il branch remoto+locale e rilascia il lock. Se il task include QA condivisa su AVD/device o release, il lock deve essere acquisito prima di quella fase e può restare detenuto fino a fine integrazione/release.
- Se il task è davvero read-only e non produce alcuna modifica, branch/PR non sono necessari; resta comunque obbligatorio il lock per QA condivisa/release.

# Goal
Completa su PersonalHub `main` la qualità/copertura v1 della vault Obsidian per **tutti i moduli mantenuti**, mantenendo la proiezione document-oriented e bounded. Chiudi Settings/AVD QA e lascia `main` pronto per il gate Git History successivo.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`;
- esegui SOLO dopo PROMPT_ID=528163 PASS/finalizzato;
- branch obbligatorio `main`, già contenente foundation + incremental engine PASS;
- `docs/OBSIDIAN_ARCHIVE.md` è autoritativo;
- full rebuild + incremental engine sono già PASS: non ridisegnarli;
- Obsidian non calcola relazioni temporali cross-module; timestamp esatti possono essere Properties, ma le associazioni temporali dinamiche restano Hub/SQLite/Datasette;
- `version.txt` resta 50; nessuna release/delivery in questa fase.

# Esecuzione minima
1. Acquisisci task lock PH con PROMPT_ID 684930. Usa i provider già creati e CODE_MAP dei moduli; niente audit repo-wide.
2. Completa i provider con grain documentale esplicito e deterministico:
   - People: contatti + item user-facing significativi; niente technical rows;
   - Places: luogo + visite/check-in significativi;
   - Timer: sessioni/attività user-facing, aggregando quando evita file explosion senza perdere leggibilità;
   - Soldi: conti/transazioni/trasferimenti/ricorrenze user-facing; importi/valuta leggibili;
   - Substances: sostanze/prescrizioni/intake a granularità utile;
   - WordPulse: sessioni/summaries o aggregati utili; vietate note separate per keystroke/correction-level noise;
   - Salute: sample/esami/journal e testo lungo; measurement può essere embedded/aggregata quando una nota separata non migliora la lettura.
3. Ogni provider documenta con comment/test la scelta di grain. Per fixture ad alto volume verifica file count bounded rispetto ai record user-facing; non creare una nota per ogni riga tecnica.
4. Cross-link:
   - usa solo canonical relation/identity esistente;
   - niente inferenza per nome;
   - usa stable path + alias leggibile;
   - non materializzare reverse backlinks duplicati;
   - Salute collega clinician→People, place→Places, medication→Substances e purchase→Soldi solo con evidenza canonica reale.
5. Long-form:
   - journal/notes/descriptions nel body Markdown, non in celle/frontmatter giganti;
   - Salute separa chiaramente contenuto clinico, AI, evidenze e originale;
   - titoli/Properties rimangono leggibili e non espongono raw IDs come label primaria.
6. Temporal:
   - Properties possono includere full datetime + epoch machine field quando utile;
   - non usare Daily Notes come unica rappresentazione temporale;
   - non implementare un motore timestamp-association Obsidian;
   - eventuali relazioni temporali mostrate devono provenire da una relazione già calcolata/canonica PH, non essere dedotte dal renderer.
7. Settings/UX:
   - toggle OFF/ON, folder picker, Rebuild now, last success/error;
   - messaggi chiari che la vault è opzionale e derivata;
   - nessun testo suggerisce che Obsidian sostituisca Datasette.
8. Test host sintetici:
   - golden Markdown per almeno un documento di ogni modulo;
   - representative wikilinks/backlinks impliciti;
   - fixture high-volume WordPulse/Timer bounded;
   - full rebuild + incremental after create/update/delete su almeno quattro moduli;
   - Datasette sync continua a funzionare con Obsidian ON/OFF;
   - nessun Markdown read nel normale app path;
   - compile interessati + `checkArchitectureBoundaries`.
9. QA AVD Pixel_8a tramite helper canonico:
   - Settings → abilita Obsidian export con directory QA SAF;
   - Rebuild now;
   - modifica dati sintetici in almeno People, Places, Soldi, Salute e verifica aggiornamento incrementale;
   - OFF => nuove write PH continuano e nessun export parte;
   - ON/rebuild converge;
   - revoca/riassegna directory senza crash/data loss;
   - nessun raw epoch/id/backend encoding user-facing nelle UI PH.
   Non serve installare Obsidian nell'AVD: valida i file generati tramite test/helper SAF bounded, non con ispezione manuale massiva.
10. Aggiorna docs/CODE_MAP solo per comportamento finale. Solo dopo i gate PASS, commit/push `main` una sola volta; non creare branch remoti temporanei. Rilascia lock.

# Acceptance
PASS solo se tutti i moduli mantenuti hanno una projection policy testata, long-form/link/frontmatter sono leggibili e deterministici, file count high-volume è bounded, Obsidian resta opzionale/one-way, Datasette continua in parallelo, host+AVD+architecture PASS e `version.txt=50`.

# Non-goal
Import Obsidian→PH, replacement di Datasette, temporal association engine in Markdown, plugin Obsidian custom obbligatori, Logseq, release/install Pixel fisico/delivery, refactor generale.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 684930 --confirm-executed`

Output massimo 8 righe: RESULT, HEAD, COVERAGE, GRAIN, LINKS_LONGFORM, HOST_GATES, AVD_QA, BLOCKER.
