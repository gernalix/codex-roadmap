PROMPT_ID=999198

# Obiettivo
Correggi il bug C2 di mapping prompt_id→work_item_id nel cutover e completa la riconciliazione PBF lasciata da 886300.

# Starting point verificato
- C2 work item: wi:64d7e420d7584b4eb74fe72e3988a687.
- In roadmap_db.py, prompt_work_item_id(prompt_id) restituisce sempre prompt:<id>.
- Nel DB canonico reale:
  - 528123 -> wi:787f93c506dd4f3f8be56439372529db (blocked)
  - 340495 -> wi:6d318704d7bd441c930832c927116a97 (blocked)
  - 886300 -> wi:87a441b2adc749c5b65943e80ef6c249 (completed)
- La mutation #1874 con resolved_by 528123/340495 -> 886300 è stata respinta dal single writer con sqlite3.IntegrityError FOREIGN KEY constraint failed perché add_relation usa gli ID sintetici prompt:<id>.
- 886300 è già completed; PR #1873 e i fix finalizer sono su main.
- I receipt BLOCKED storici di 528123 e 340495 sono immutabili e vanno preservati.

# Lavoro
1. Aggiungi un test regressivo che riproduca il FK failure con prompt materializzati sopra work item wi:<uuid>.
2. Implementa una risoluzione canonica prompt_id -> work_item_id reale quando work_items cutover è attivo, con fallback legacy prompt:<id> solo quando quello è davvero l'ID canonico esistente.
3. Audit limitato a tutti gli usi di prompt_work_item_id nel cutover: correggi quelli che possono produrre FK/mapping sbagliati; non fare refactor non necessario.
4. Preserva comportamento legacy e compatibilità dei DB storici.
5. Test focused-first, poi suite C2 pertinente; non investigare failure estranei, catturali solo in Inbox.
6. Integra l'exact tested head via percorso codex-roadmap dedicato.
7. Dopo il merge, invia e verifica le relazioni canoniche:
   - 528123 resolved_by 886300
   - 340495 resolved_by 886300
   Senza cambiare gli outcome/status storici BLOCKED.
8. Verifica che v_pbf_dispositions mostri entrambi come resolved e che 886300 resti completed.
9. Chiudi questo leaf col terminal contract C2.

# Vincoli
- Nessun lavoro Grindr.
- Nessun direct write a main/roadmap.sqlite.
- Nessun polling modello per CI: checkpoint e stop se serve attendere una transizione esterna.
- Non riaprire né rieseguire 528123, 340495 o 886300.

# Report finale
PROMPT_ID=<id>
RESULT=PASS|BLOCKED|FAIL
C2_RESULT=<json compatto>
