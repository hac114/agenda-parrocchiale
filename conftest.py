"""Configurazione pytest: aggiunge src/ al PYTHONPATH."""

import sys
from pathlib import Path

# Aggiunge src/ al path di Python per gli import dei test
sys.path.insert(0, str(Path(__file__).parent / "src"))
