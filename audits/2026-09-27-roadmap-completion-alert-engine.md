# Roadmap completion alerts

Sì. Per C2 questa dovrebbe diventare un’infrastruttura nativa, non una convenzione affidata alle chat. La implementerei come **alert engine della roadmap basato sul DB canonico + transactional outbox + dispatcher Telegram**.

### Architettura consigliata

```text
Executor / processor
       │
       │ aggiorna stato
       ▼
┌─────────────────────┐
│ Roadmap DB canonico │
│                     │
│ task / bundle / tag │
│ alert_subscription  │
│ notification_outbox │
└─────────┬───────────┘
          │
          │ 1–2 s
          ▼
┌─────────────────────┐
│ Alert dispatcher    │
│ systemd service     │
└─────────┬───────────┘
          │
          ▼
   Telegram helper
          │
          ▼
      📱 notifica
```

La regola fondamentale è: **l’executor non invia la notifica**. L’executor si limita a cambiare lo stato canonico. È il sistema roadmap che osserva quella transizione e genera un evento persistente. Così un Codex che crasha, una chat che freeza o un supervisor che viene riavviato non possono farti perdere l’avviso.

### Tre tipi di watch

Supporterei direttamente:

- **Task** → avvisa quando quel task raggiunge realmente `completed/PASS`.
- **Bundle** → insieme esplicito di task; avvisa quando tutti soddisfano le condizioni.
- **Tag** → per esempio `#personalhub`, `#release-ready`, `#workflowy-dashboard`; scatta quando l’insieme di task corrispondente raggiunge la condizione configurata.

Aggiungerei però anche un quarto tipo, probabilmente quello che useresti più spesso:

**`repo_ready`** → non significa semplicemente «l’ultimo task è diventato DONE», ma:

```text
tutti i task richiesti completati
AND acceptance gate PASS
AND test richiesti PASS
AND nessun blocker aperto
AND stato Git previsto raggiunto
AND eventuale artifact/build disponibile
```

È questo che permette una notifica realmente utile come:

> ✅ PersonalHub pronto  
> Bundle: Alerts engine  
> 8/8 task PASS  
> Tests: PASS  
> Repo: PersonalHub  
> Commit: a81c27e  
> APK: disponibile  
> Completed: 20:41

anziché un ambiguo «task terminato».

### Persistenza: transactional outbox

Questo è il componente che rende il sistema resistente.

Quando, per esempio, l’ultimo task di un bundle passa a PASS, nella **stessa transazione DB** si registra:

```text
roadmap state -> aggiornato
notification_outbox -> evento da consegnare
```

Quindi non può verificarsi:

```text
task completato
↓
processo crasha
↓
notifica mai generata
```

Il dispatcher Telegram legge esclusivamente l’outbox.

Schema concettuale:

```text
alert_subscription
──────────────────
id
selector_type       task | bundle | tag | repo_ready
selector
completion_policy
channel              telegram
enabled
one_shot
created_at

notification_outbox
──────────────────
id
subscription_id
event_type
subject_id
generation
payload
status               pending | sending | delivered | retry
attempt_count
next_attempt_at
created_at
delivered_at
telegram_message_id
```

Con una constraint tipo:

```text
UNIQUE(subscription_id, subject_id, generation)
```

per impedire che 20 aggiornamenti dello stesso task producano 20 notifiche.

### Reopen e completamenti successivi

Qui eviterei un banale flag `notified=true`.

Ogni task/bundle avrebbe una **completion generation**:

```text
generation 17 → completato → alert
task riaperto
generation 18 → completato nuovamente → nuovo alert
```

Così un task che viene riaperto per un bug e corretto di nuovo può legittimamente notificarti una seconda volta, senza confondersi con un retry della vecchia notifica.

Per i tag farei due modalità:

```text
one-shot
```

«Avvisami quando tutti i task attualmente appartenenti a `#foo` saranno completati.»

e

```text
persistent
```

«Ogni volta che `#foo` torna completamente soddisfatto dopo essere stato nuovamente reso pending, avvisami.»

La prima dovrebbe essere il default perché è molto meno sorprendente.

### Telegram: consegna almeno una volta

Userei **la libreria/helper Telegram C2 già centralizzata**, senza introdurre chiamate Bot API sparse nel codice.

Retry:

```text
1 min
5 min
15 min
1 h
...
```

con backoff e limite ragionevole.

Per Telegram non puoi ottenere un vero *exactly once* distribuito: c'è sempre il caso teorico «Telegram ha ricevuto il messaggio ma il processo muore prima di scrivere `delivered`». Quindi sceglierei deliberatamente **at-least-once**: nel raro caso estremo preferisco che tu riceva due notifiche piuttosto che nessuna.

### Dove valutare gli alert

Non farei un altro crawler che controlla periodicamente tutta la roadmap.

Quando cambia qualcosa che può influire sul risultato:

```text
task status changed
task added/removed from bundle
tag changed
test gate changed
blocker changed
repo/build state changed
```

il mutation layer individua soltanto le subscription potenzialmente interessate e ne rivaluta la condizione.

Per SQLite, il dispatcher può poi controllare l'outbox ogni ~1–2 secondi. È praticamente realtime ma molto più semplice e robusto di IPC, socket o sistemi pub/sub aggiuntivi.

### UX che userei

Nella dashboard metterei una piccola **🔔** su task, bundle e tag.

Le operazioni dovrebbero ridursi a:

```text
🔔 Notify when complete
🔔 Notify whenever complete
🔕 Remove alert
```

e niente configurazioni tecniche.

Lo stato dell'alert deve stare nel DB roadmap; Workflowy/dashboard ne è solo una proiezione. Se Workflowy è rotto, l'alert continua a funzionare.

### Una distinzione importante

Separerei:

```text
COMPLETED
```

da

```text
READY
```

Perché il tuo vero problema non è sapere che «Codex ha finito qualcosa». Vuoi sapere:

> **“Questo pezzo del mio sistema ora è effettivamente pronto perché io lo usi.”**

Quindi una subscription potrebbe essere:

```text
watch:
  type: repo_ready
  repo: PersonalHub
  scope: alerts-engine
```

e partire soltanto quando sono soddisfatti tutti i gate di quel bundle.

### Resilienza operativa

Aggiungerei anche un piccolo health check:

```text
c2-alert-dispatcher.service
```

con:

- `Restart=always`;
- recovery automatico delle entry `sending` rimaste orfane dopo un crash;
- `busy_timeout`/WAL se SQLite;
- metriche `pending`, `oldest_pending_age`, `failed`, `last_delivery`;
- monitor Kuma se già usi Kuma per C2;
- test E2E che crea un task fittizio → lo completa → verifica la registrazione nell'outbox → intercetta/invia Telegram → verifica `delivered`.

Non costruirei invece un secondo framework general-purpose di eventi: **subscription + evaluator + transactional outbox + dispatcher** sono sufficienti.

Il risultato elimina contemporaneamente tre workflow che oggi ti fanno perdere tempo: chiedere alla chat di ricordarsi di avvisarti, aprire chat per chiedere «a che punto è?», e sorvegliare manualmente la dashboard. È una delle poche aggiunte infrastrutturali a C2 che, invece di aggiungere burocrazia agli executor, può effettivamente **togliergliela**.
