PROMPT_ID=609279 | project_id=49 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
Codex Desktop project: Personal Hub

# Goal
Applica due modifiche UX/policy ristrette a PersonalHub:
1. sospendi per ora le stringhe/localizzazioni italiane: l’UI attiva deve usare solo le stringhe inglesi;
2. in Places rimuovi dalla Home l’enorme sezione inline “Check-in diagnostics” e rendila accessibile solo tramite un pulsante/controllo discreto dedicato.

# Starting point verificato
- repo/workdir: /home/daniele/projects/PersonalHub, branch finale main;
- Places Home: feature/luoghi/src/main/java/com/gernalix/luoghi/ui/home/HomeScreen.kt;
- English Places strings: feature/luoghi/src/main/res/values/strings.xml;
- Italian Places strings: feature/luoghi/src/main/res/values-it/strings.xml;
- esistono anche risorse values-it nell’app/altri moduli: individua SOLO i resource set italiani necessari a rendere PH effettivamente English-only, senza audit generale;
- l’attuale Home inserisce CheckInDiagnosticsPanel inline subito dopo l’header Places.

# Requisiti
- English-only deve valere per PersonalHub nel suo complesso, non solo Places: nessuna schermata deve scegliere risorse italiane quando il device è in italiano.
- Metodo semplice e reversibile: rimuovi/disattiva i resource set values-it* attivi; non duplicare né riscrivere inutilmente le stringhe inglesi.
- Build/lint non devono più richiedere traduzioni italiane.
- Places: nessun dettaglio diagnostico deve occupare spazio nella lista principale.
- Aggiungi un controllo discreto “Diagnostics” nella Home/area Places; se non ci sono tentativi può essere disabilitato o nascosto.
- Al tap, mostra gli stessi recent attempts in una superficie scrollabile on-demand (dialog/sheet/schermata equivalente).
- Conserva filtri Outcome/Place, copy report e contenuto diagnostico esistente; nessuna modifica alla logica di check-in o ai dati.
- Tutto il testo utente introdotto deve essere inglese.
- Non cambiare altre feature, non refactorizzare, non fare cleanup fuori scope.

# Esecuzione minima
1. Un solo preflight Git; sincronizza main in modo non distruttivo. Parti dai path sopra e amplia solo se necessario per values-it.
2. Implementa il minimo diff.
3. Esegui test/compile mirati a feature:luoghi e il lint/app gate minimo che dimostri che la sospensione dell’italiano non produce MissingTranslation.
4. Verifica su emulatore Android, senza device fisici: con locale italiano la Home/Places deve apparire in inglese; il pannello diagnostico non deve essere inline; il controllo Diagnostics deve aprirlo e chiuderlo correttamente.
5. Se un gate fallisce, correggi solo lo stesso failure domain e rilancia il minimo gate invalidato. Nessun retry identico, audit generale, refactor o test ridondante.
6. Commit/push main una sola volta dopo PASS; se serve un branch temporaneo, mergialo subito e cancellalo.

# Acceptance
PASS solo se:
- PH usa UI inglese anche con device locale italiano;
- values-it non è più un requisito di manutenzione/lint;
- Places Home non mostra più la card diagnostica inline;
- Diagnostics è accessibile on-demand con filtri e copia preservati;
- compile/test/lint mirati PASS;
- smoke emulatore PASS;
- main pulito e sincronizzato.

Finalizza:
python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 609279 --confirm-executed

BLOCKED/FAIL via roadmap_result. Output finale max 6 righe: RESULT, HEAD, ENGLISH_ONLY, PLACES_DIAGNOSTICS, TESTS, BLOCKER.
