"""Test manuale: carica_config su profilo reale.

Questo file è un test "di integrazione" che verifica che
carica_config funzioni davvero sul profilo san_pietro_in_silki.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Aggiungi src/ al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import carica_config

# ======================================================================
# ESECUZIONE
# ======================================================================


def test_carica_config_reale() -> None:
    """Carica il profilo reale e stampa i dati."""
    config = carica_config("san_pietro_in_silki")

    # Stampa tutto
    print("\n" + "=" * 70)
    print("CONFIGURAZIONE CARICATA")
    print("=" * 70)
    print(f"Nome parrocchia:     {config.nome_parrocchia}")
    print(f"Città:               {config.citta}")
    print(f"Anno:                {config.anno}")
    print(f"Periodi:             {len(config.periodi)}")
    print(f"Festivi fissi:       {len(config.festivi_fissi)}")
    print(f"Eccezioni festivi:   {len(config.eccezioni_festivi)}")
    print(f"Divieti fissi:       {len(config.divieti_pomeridiani_fissi)}")
    print(f"Divieti mobili:      {len(config.divieti_pomeridiani_mobili)}")
    print(f"Ricorrenze proprie:  {len(config.ricorrenze_proprie)}")
    print(f"Celebrazioni mobili: {len(config.celebrazioni_mobili)}")
    print(f"Giorni accorpati:    {len(config.giorni_accorpati)}")
    print(f"Intenzioni:          {len(config.intenzioni)}")
    print(f"Matrimoni:           {len(config.matrimoni_prenotati)}")
    print(f"Note:                {len(config.note_annuali)}")
    print("=" * 70)

    # Verifiche di base
    assert config.nome_parrocchia == "San Pietro in Silki"
    assert config.citta == "Sassari"
    assert config.anno == 2027
    assert len(config.periodi) == 5
    assert len(config.festivi_fissi) == 16
    assert len(config.ricorrenze_proprie) > 0

    # Stampa i periodi
    print("\nPERIODI CARICATI:")
    for p in config.periodi:
        print(f"  {p.dal} → {p.al}")
        print(f"    Feriali: {p.orari_feriali}")
        print(f"    Festivi: {p.orari_festivi}")

    # Stampa le ricorrenze
    print("\nRICORRENZE PROPRIE:")
    for r in config.ricorrenze_proprie:
        print(f"  {r.nome}: {r.data_inizio}", end="")
        if r.data_fine:
            print(f" → {r.data_fine}", end="")
        print()
