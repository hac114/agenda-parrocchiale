# Architettura del progetto

Documento tecnico che descrive le scelte architetturali del progetto
**Agenda Parrocchiale**. Per sviluppatori e manutentori.

---

## Indice

1. [Panoramica](#1-panoramica)
2. [Flusso di esecuzione](#2-flusso-di-esecuzione)
3. [Struttura del codice](#3-struttura-del-codice)
4. [Moduli principali](#4-moduli-principali)
5. [Fonti di dati](#5-fonti-di-dati)
6. [Pattern e convenzioni](#6-pattern-e-convenzioni)
7. [Dipendenze](#7-dipendenze)
8. [Testing](#8-testing)

---

## 1. Panoramica

Il progetto è un **generatore automatico di agende liturgiche**.
Prende in input:
- Un file **Excel** con i dati annuali (orari, intenzioni, matrimoni)
- Un file **YAML** con le regole stabili (feste, ricorrenze, divieti)

E produce in output:
- Un **PDF A4** impaginato per la tipografia

### Principi di design

| Principio | Come è applicato |
|---|---|
| **Separazione dati/regole** | Excel = dati annuali, YAML = regole stabili |
| **Multi-profilo** | Ogni parrocchia ha la sua cartella in `configs/` |
| **Warning non bloccanti** | Errori di compilazione → warning + riepilogo finale |
| **Testabilità** | Funzioni piccole, testate al 86% |
| **Estendibilità** | Aggiungere festa = riga YAML, non codice |

---

## 2. Flusso di esecuzione

Il flusso è suddiviso in **3 fasi**: lettura, calcolo, rendering.

### Diagramma completo

```mermaid
flowchart TD
    A[regole.yaml<br/>regole stabili] -->|leggi_yaml| B[dati_yaml]
    B -->|unisci_config| C[Config]
    D[config.xlsx<br/>dati annuali] -->|leggi_foglio_*| C
    C -->|calcola_tutte_date_mobili| E[CalendarioAgenda<br/>365 giorni]
    C -->|calcola date mobili| E
    E -->|genera_pdf| F[PDF A4<br/>367 pagine]
```

### Fase 1 — Lettura

| Step | Input | Funzione | Output |
|---|---|---|---|
| 1 | `regole.yaml` | `leggi_yaml()` | `dati_yaml` (dict) |
| 2 | `config.xlsx` | `leggi_foglio_impostazioni()`<br/>`leggi_foglio_intenzioni()`<br/>`leggi_foglio_matrimoni()`<br/>`leggi_foglio_note()` | `dati_excel` (dict) |
| 3 | `dati_yaml` + `dati_excel` | `unisci_config()` | `Config` (dataclass) |

### Fase 2 — Calcolo

| Step | Input | Funzione | Output |
|---|---|---|---|
| 1 | `Config.anno` | `calcola_tutte_date_mobili()` | `dict` di date mobili |
| 2 | `Config` + date mobili | `genera_agenda()` | `CalendarioAgenda` (365 giorni) |

### Fase 3 — Rendering

| Step | Input | Funzione | Output |
|---|---|---|---|
| 1 | `CalendarioAgenda` + `Config` | `genera_pdf()` | `PDF A4` (367 pagine) |

### I 3 moduli chiave

| Modulo | Fase | Responsabilità |
|---|---|---|
| `config.py` | Lettura | Unisce YAML + Excel in `Config` |
| `generatore_agenda.py` | Calcolo | Trasforma `Config` in `CalendarioAgenda` |
| `generatore_pdf.py` | Rendering | Trasforma `CalendarioAgenda` in PDF |


### Le 3 fasi

1. **Lettura** — i moduli `lettura_yaml` e `lettura_excel` estraggono i dati
2. **Calcolo** — `calcolo_liturgico` e `generatore_agenda` producono il calendario
3. **Rendering** — `generatore_pdf` converte il calendario in PDF

---

## 3. Struttura del codice
- src/
- **stili.py:**                    Stili Excel (colori, font, bordi)
- **util.py:**                     Utility (logging, formattazione, helper)

- **dataclass_config.py:**         Dataclass condivise (Periodo, Festa, ...)

- **lettura_yaml.py:**             Lettura regole.yaml
- **lettura_excel.py:**            Lettura config.xlsx (4 fogli)
- **config.py:**                   unisci_config, carica_config

- **calcolo_liturgico.py:**        Pasqua, feste mobili, 9 mercoledì
- **generatore_agenda.py:**        Calendario giorno per giorno

- **fogli_excel.py:**              Creazione dei 4 fogli Excel
- **crea_config_template.py:**     CLI: genera config.xlsx

- **generatore_pdf.py:**           HTML → PDF (WeasyPrint)

## 💡 Note
- Triple backtick senza etichetta → blocco di codice generico (monospazio, no colorazione)
- I # sono commenti visivi, non parte della struttura
- Gli allineamenti sono estetici — Markdown non li richiede
