# Notify when complete vs Notify whenever complete

La differenza è questa:

- **🔔 Notify when complete** → alert **one-shot**. Ti avvisa la prossima volta che il task/bundle raggiunge `complete`, poi la subscription si disattiva.
- **🔔 Notify whenever complete** → alert **persistente**. Ti avvisa ogni volta che quel task/bundle viene riaperto o torna incompleto e successivamente raggiunge di nuovo `complete`.

Esempio:

```text
pending → complete       → 🔔 alert
complete → reopened
reopened → complete      → ?
```

Con **Notify when complete**: nessun secondo alert.

Con **Notify whenever complete**: ricevi anche il secondo alert.

Per il tuo uso normale sceglierei **Notify when complete** come default. `Whenever` serve soprattutto per bundle/tag ricorrenti o workflow che possono essere completati più volte.
