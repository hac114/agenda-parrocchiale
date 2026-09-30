#!/usr/bin/env bash
# =====================================================================
# Generatore Agenda Parrocchiale — Launcher Linux
# =====================================================================
# Uso:
#   ./scripts/genera_agenda.sh <profilo> [anno]
#
# Esempi:
#   ./scripts/genera_agenda.sh san_pietro_in_silki 2027
#   ./scripts/genera_agenda.sh san_pietro_in_silki
# =====================================================================

set -e  # esci in caso di errore

# Directory del progetto (parent di scripts/)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROGETTO_DIR="$( dirname "$SCRIPT_DIR" )"

cd "$PROGETTO_DIR"

# Argomenti
PROFILO="${1:-san_pietro_in_silki}"
ANNO="${2:-$(date +%Y)}"

echo "======================================================================"
echo "  GENERAZIONE AGENDA"
echo "  Profilo: $PROFILO"
echo "  Anno:    $ANNO"
echo "======================================================================"
echo

# Attiva venv se esiste
if [ -d ".venv" ]; then
    # shellcheck source=/dev/null
    source .venv/bin/activate
else
    echo "⚠️  Nessun venv trovato in .venv/"
    echo "   Esegui prima: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# STEP 1: Genera config.xlsx solo se non esiste
echo ">>> STEP 1/3: Verifica config.xlsx"
if [ -f "configs/$PROFILO/config.xlsx" ]; then
    echo "    ✅ config.xlsx esiste già, salto la generazione"
else
    echo "    ⚙️  config.xlsx non trovato, lo genero"
    python src/crea_config_template.py --profilo "$PROFILO" --anno "$ANNO"
fi
echo

# STEP 2: Genera PDF
echo ">>> STEP 2/3: Generazione PDF"
python -c "
import sys
sys.path.insert(0, 'src')
from generatore_pdf import genera_pdf_da_profilo
percorso = genera_pdf_da_profilo('$PROFILO')
print(f'PDF generato: {percorso}')
"
echo

# STEP 3: Riepilogo
echo ">>> STEP 3/3: Riepilogo"
PERCORSO_PDF="$PROGETTO_DIR/output/Agenda_${ANNO}.pdf"
if [ -f "$PERCORSO_PDF" ]; then
    echo "✅ Fatto! PDF generato:"
    echo "   $PERCORSO_PDF"
    ls -lh "$PERCORSO_PDF"
else
    echo "❌ PDF non trovato in $PERCORSO_PDF"
    exit 1
fi

echo
echo "======================================================================"
echo "  COMPLETATO"
echo "======================================================================"