PROMPT_ID=830867 | PARENT_PROMPT_ID=734205 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Rendi coerenti i veri timestamp di PersonalHub: i timestamp persistiti devono essere epoch-ms INTEGER; migra solo residui TEXT/ISO che rappresentano istanti; tutte le UI human-facing usano `HubTimestamp` nel formato `EEE d/M/yy HH:mm`. Non trasformare date-only o formati imposti da protocolli esterni.

# Precondizione
Esegui solo dopo 223103 PASS su `/home/daniele/projects/PersonalHub`.

# Esecuzione minima
1. Sul main pulito esegui per prima cosa `tools/check_timestamp_contract.py`; usa l'output come router e apri solo consumer/DAO/entity segnalati. Se non esiste alcuna violazione reale, non creare commit/bump cosmetici.
2. Se servono modifiche, crea branch dedicato dal canonical corrente. Prima di cambiare API/Room usa consumer preflight mirato.
3. Classifica ogni finding come epoch_ok, date_only, external_protocol o violation. Modifica solo violation.
4. Se esistono istanti TEXT/ISO persistiti, implementa migration lossless a epoch-ms con fixture legacy, conteggi/FK/quick_check invariati, staging/rollback import e profili indipendenti. Nessun destructive fallback.
5. Aggiorna solo i consumer reali al formatter canonico locale/timezone device; niente epoch/ISO raw human-facing.
6. Gate: scanner=0 violation non classificate, migration test se necessaria, compile/test dei soli moduli toccati, architecture gate se cambia boundary. QA `Pixel_8a`: superfici globali + moduli rappresentativi, cambio timezone, due profili.
7. Se hai modificato prodotto/schema, bump `version.txt` esattamente una volta rispetto al base; se il task è realmente no-op, nessun bump.
8. Push/PR candidate; lease solo per integrazione/AVD, semantic review contro latest main, merge e delete branch dopo PASS.

# Acceptance / stop
PASS con contratto timestamp verificato, nessuna perdita dati, host+AVD pertinenti PASS e branch chiuso. Finalizza PROMPT_ID 830867. Output max 8 righe.
