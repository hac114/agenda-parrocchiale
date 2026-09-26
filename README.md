# Agenda Parrocchiale

Generatore automatico di agende liturgiche per parrocchie e santuari.

Produce un PDF impaginato (formato tipografico) partendo da un file Excel
compilato dall'utente + regole liturgiche configurabili in YAML.

## Caratteristiche

- Calcolo automatico del calendario liturgico (Pasqua, feste mobili)
- Orari stagionali configurabili (inverno, estate, maggio, ecc.)
- Divieti pomeridiani (Assunta, San Nicola, Corpus Domini)
- Ricorrenze proprie del santuario (es. San Salvatore da Horta)
- Registro intenzioni di Messa
- Output PDF pronto per la tipografia (A4 verticale, fronte/retro)
- Multi-profilo: una configurazione per ogni parrocchia

## Installazione

```bash
git clone https://github.com/<tuo-utente>/agenda-parrocchiale.git
cd agenda-parrocchiale
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
