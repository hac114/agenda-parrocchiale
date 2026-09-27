"""
Lettura di file YAML di configurazione.

Contiene la funzione `leggi_yaml` che carica un file YAML e restituisce
il suo contenuto come dizionario Python, con gestione errori chiara.

Uso tipico:
    from lettura_yaml import leggi_yaml

    dati = leggi_yaml(Path("configs/san_pietro_in_silki/regole.yaml"))
"""

from __future__ import annotations

from pathlib import Path

import yaml

# ======================================================================
# LETTURA YAML
# ======================================================================


def leggi_yaml(percorso: Path) -> dict:
    """Legge un file YAML e restituisce il contenuto come dizionario.

    Args:
        percorso: percorso del file YAML da leggere

    Returns:
        Dizionario con il contenuto del file.
        Se il file è vuoto, restituisce un dizionario vuoto.

    Raises:
        FileNotFoundError: se il file non esiste
        ValueError: se il file non è uno YAML valido
    """
    if not percorso.exists():
        raise FileNotFoundError(f"File YAML non trovato: {percorso}")

    if not percorso.is_file():
        raise ValueError(f"Il percorso non è un file: {percorso}")

    try:
        with open(percorso, encoding="utf-8") as f:
            dati = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"YAML malformato in {percorso}: {e}") from e

    # yaml.safe_load restituisce None se il file è vuoto
    if dati is None:
        return {}

    # Ci aspettiamo un dizionario alla radice
    if not isinstance(dati, dict):
        raise ValueError(
            f"Il file YAML deve contenere un dizionario alla radice, "
            f"trovato invece: {type(dati).__name__}"
        )

    return dati
