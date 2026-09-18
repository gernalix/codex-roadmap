PROMPT_ID=845312 | project_id=49 | campaign_id=ph-obsidian-archive | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Completa su PersonalHub `main` la qualità/copertura v1 della vault Obsidian per **tutti i moduli mantenuti**, mantenendo la proiezione document-oriented e bounded. Chiudi Settings/AVD QA e lascia `main` pronto per il gate Git History successivo.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`;
- esegui SOLO dopo PROMPT_ID=671904 PASS/finalizzato;
- branch obbligatorio `main`, già contenente foundation + incremental engine PASS;
- `docs/OBSIDIAN_ARCHIVE.md` è autoritativo;
- full rebuild + incremental engine sono già PASS: non ridisegnarli;
- Obsidian non calcola relazioni temporali cross-module; timestamp esatti possono essere Properties, ma le associazioni temporali dinamiche restano Hub/SQLite/Datasette;
- `version.txt` resta 50; nessuna release/delivery in questa fase.

# Esecuzione minima
1. Acquisisci task lock PH con PROMPT_ID 845312. Usa i provider già creati e CODE_MAP dei moduli; niente audit repo-wide.
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
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 845312 --confirm-executed`

Output massimo 8 righe: RESULT, HEAD, COVERAGE, GRAIN, LINKS_LONGFORM, HOST_GATES, AVD_QA, BLOCKER.
