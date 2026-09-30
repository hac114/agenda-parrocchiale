# Agenda Parrocchiale

Generatore automatico di agende liturgiche per parrocchie e santuari.

Produce un **PDF impaginato per la tipografia** (A4 verticale) partendo da:
- Un file **Excel** compilato dall'utente (dati annuali: orari, intenzioni, matrimoni)
- Un file **YAML** con le regole liturgiche (feste, ricorrenze, divieti)

L'agenda è **multi-profilo**: ogni parrocchia ha la sua configurazione.

---

## Caratteristiche

- ✅ Calcolo automatico del calendario liturgico (Pasqua, feste mobili)
- ✅ Orari stagionali configurabili (inverno, estate, maggio, ecc.)
- ✅ Divieti pomeridiani (Assunta, San Nicola, Corpus Domini)
- ✅ Ricorrenze proprie del santuario (es. San Salvatore da Horta, Triduo)
- ✅ Nove mercoledì di San Salvatore (calcolo automatico)
- ✅ Festa del Voto con slittamento automatico se coincide con Corpus Domini
- ✅ Registro intenzioni di Messa
- ✅ Pagina dedicata alle prenotazioni matrimoni degli anni successivi
- ✅ Output PDF pronto per la tipografia (A4 verticale)
- ✅ Sistema di raccolta warning con riepilogo finale

---

## Requisiti

### Software necessario

| Sistema | Requisito |
|---|---|
| **Windows** | Python 3.12+ (consigliato 3.13), Microsoft Excel o LibreOffice |
| **Linux** | Python 3.12+, LibreOffice |
| **macOS** | Python 3.12+, LibreOffice |

### Librerie di sistema (Linux)

Per WeasyPrint (generazione PDF) servono alcune librerie di sistema:

```bash
sudo apt install libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info -y
```
## Installazione

### 1. Clona il repository
```bash
git clone https://github.com/hac114/agenda-parrocchiale.git
cd agenda-parrocchiale
```
### 2. Crea l'ambiente virtuale
#### Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```    
#### Windows (PowerShell):
```Powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
#### Windows (Prompt dei comandi):
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### 3. Installa le dipendenze
```pip
pip install --upgrade pip
pip install -r requirements.txt
```    

## Utilizzo
Primo avvio — Genera la configurazione
Il primo passo è creare il file config.xlsx (Excel) per la tua parrocchia.

### Linux:
```bash
./scripts/genera_agenda.sh san_pietro_in_silki 2027
```

### Windows:
```cmd
scripts\genera_agenda.bat san_pietro_in_silki 2027
```
### Lo script fa tutto automaticamente:
1. Genera il file configs/<profilo>/config.xlsx
2. Calcola il calendario liturgico per l'anno
3. Produce il PDF output/Agenda_2027.pdf

### Compilare il file Excel
Apri configs/<profilo>/config.xlsx con Excel o LibreOffice e compila i 4 fogli:

| Foglio | Cosa contiene |
|---|---|
| **Impostazioni** | Anno, nome parrocchia, città, periodi stagionali |
| **Intenzioni** | Registro delle intenzioni di Messa |
| **Matrimoni** | Prenotazioni matrimoni per l'anno successivo |
| **Note** | Annotazioni libere (triduo, mese mariano, ecc.) |

Le celle GIALLE sono compilabili. Le altre sono protette.

### Rigenerare il PDF
Dopo aver compilato l'Excel, rigenera il PDF:

### Linux:
```bash
./scripts/genera_agenda.sh san_pietro_in_silki 2027
```
### Windows (cmd):
```cmd
scripts\genera_agenda.bat san_pietro_in_silki 2027
```
**Attenzione: chiudi Excel/LibreOffice prima di rigenerare il PDF.**

## ⚠️ Risoluzione problemi comuni
### Il nome della parrocchia non si aggiorna in Excel

**Causa:** Excel o LibreOffice tiene in memoria una versione precedente del file, anche dopo averlo chiuso.

**Soluzione rapida:**

**Windows:**
1. Chiudi **tutte** le finestre di Excel/LibreOffice
2. `Ctrl+Shift+Esc` → Task Manager → cerca `EXCEL.EXE` o `soffice` → Termina attività
3. Riapri il file

**Linux:**
```bash
pkill soffice
libreoffice --norestore configs/san_pietro_in_silki/config.xlsx
```

L'opzione `--norestore` forza LibreOffice a leggere il file dal disco (bypassa la cache di sessione).

**Se il problema si ripresenta in futuro (Linux):**

Usa sempre l'apertura con `--norestore`:

```bash
libreoffice --norestore configs/san_pietro_in_silki/config.xlsx
```

Questo bypassa completamente la sessione precedente di LibreOffice.

**Verifica che il file su disco sia corretto:**

```bash
python -c "
from openpyxl import load_workbook
wb = load_workbook('configs/san_pietro_in_silki/config.xlsx')
ws = wb['Impostazioni']
print('Anno:', ws['B5'].value)
print('Nome:', ws['B6'].value)
print('Città:', ws['B7'].value)
"
```

- **Se stampa il nome corretto** → il file è OK, era solo la cache dell'editor
- **Se stampa un nome vuoto o sbagliato** → contatta il supporto

**Se il problema persiste (Linux):**

Cancella la cache di LibreOffice:
```bash
rm -rf ~/.config/libreoffice/4/user/backup
rm -rf ~/.config/libreoffice/4/user/registrymodifications.xcu
```

Poi riapri il file.

### WeasyPrint non si installa su Linux
**Errore tipico: OSError: cannot load library 'libgobject-2.0-0'.**

#### Soluzione:
```bash
sudo apt install libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info -y
```
#### Poi riprova:
```pip
pip install -r requirements.txt
```
### Il PDF generato contiene errori
Controlla i warning emessi durante la generazione. Lo script mostra un riepilogo:

```text
⚠️  ATTENZIONE: 3 problemi rilevati durante la lettura
Vuoi comunque procedere? [y/N]:
```
**Rispondi n per correggere, y per procedere comunque.**

## Struttura del progetto

```
agenda-parrocchiale/
├── configs/                       # Una cartella per parrocchia
│   ├── _template/                 # Modello vuoto (da copiare)
│   │   ├── .backup/               # Backup automatici
│   │   ├── config.xlsx            # Excel (dati annuali)
│   │   └── regole.yaml            # YAML (regole stabili)
│   └── san_pietro_in_silki/       # Profilo reale
│       ├── .backup/
│       ├── config.xlsx
│       ├── LEGGIMI.txt            # Istruzioni rapide
│       └── regole.yaml
│
├── docs/                          # Documentazione
│   ├── ARCHITETTURA.md            # Scelte tecniche
│   ├── GUIDA_RAPIDA.md            # Da stampare e tenere accanto al PC
│   ├── GUIDA_UTENTE.md            # Per il frate responsabile
│   ├── INFO_CONSOLIDATE.md        # Riepilogo requisiti
│   └── README.md                  # Indice docs
│
├── output/                        # PDF generati
│   ├── Agenda_2027.pdf            # (ignorato da Git)
│   └── .gitkeep
│
├── scripts/                       # Launcher per l'utente finale
│   ├── genera_agenda.bat          # Per Windows
│   └── genera_agenda.sh           # Per Linux/macOS
│
├── src/                           # Codice Python
│   ├── calcolo_liturgico.py       # Pasqua, feste mobili
│   ├── config.py                  # carica_config, unisci_config
│   ├── crea_config_template.py    # Generatore config.xlsx
│   ├── dataclass_config.py        # Dataclass condivise
│   ├── fogli_excel.py             # Creazione 4 fogli Excel
│   ├── generatore_agenda.py       # Calendario giorno per giorno
│   ├── generatore_pdf.py          # HTML → PDF (WeasyPrint)
│   ├── lettura_excel.py           # Lettura config.xlsx
│   ├── lettura_yaml.py            # Lettura regole.yaml
│   ├── stili.py                   # Stili Excel (colori, font)
│   └── util.py                    # Utility (logging, formattazione)
│
├── templates/                     # Template HTML/CSS per PDF
│   ├── agenda.html                # Pagina giorno
│   ├── copertina.html             # Copertina
│   ├── registro_intenzioni.html   # Registro intenzioni
│   ├── matrimoni_futuri.html      # Prenotazioni matrimoni anno successivo
│   └── style.css                  # Stile A4
│
├── tests/                         # Test pytest
│   ├── test_calcolo_liturgico.py
│   ├── test_config.py
│   ├── test_dataclass_config.py
│   ├── test_fogli_excel.py
│   ├── test_generatore_agenda.py
│   ├── test_generatore_pdf.py
│   ├── test_lettura_excel.py
│   ├── test_lettura_yaml.py
│   ├── test_stili.py
│   └── test_util.py
│
├── .gitignore
├── conftest.py                    # Configurazione pytest
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Documentazione
1. **Guida utente** — come compilare l'agenda (per il frate responsabile)
2. **Architettura** — scelte tecniche e struttura del codice

#### Sviluppo Test
```bash
pytest tests/ -v
```
#### Coverage
```bash
pytest tests/ --cov=src --cov-report=term-missing
```
#### Qualità del codice
```bash
black src/ tests/          # formattazione
isort src/ tests/          # ordinamento import
mypy src/                  # type checking
flake8 src/ tests/         # linting
```
## Licenza
Vedi LICENSE.

## Contatti

Per problemi o domande: [apri una issue](https://github.com/hac114/agenda-parrocchiale/issues) su GitHub.
