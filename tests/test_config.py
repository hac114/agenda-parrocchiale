"""Test per il modulo config (unisci_config, carica_config)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from config import carica_config, unisci_config

# ======================================================================
# TEST — unisci_config
# ======================================================================


def test_unisci_config_minimo() -> None:
    """Unione con dati minimi."""
    dati_yaml = {
        "nome_parrocchia": "Test",
        "citta": "Roma",
        "festivi_fissi": [],
        "eccezioni_festivi": [],
        "divieti_pomeridiani": {"fissi": [], "mobili": []},
        "ricorrenze_proprie": [],
    }
    dati_excel = {
        "anno": 2027,
        "nome_parrocchia": "Test",
        "citta": "Roma",
        "periodi": [],
    }

    config = unisci_config(dati_yaml, dati_excel)
    assert config.nome_parrocchia == "Test"
    assert config.citta == "Roma"
    assert config.anno == 2027
    assert config.periodi == []


def test_unisci_config_feste() -> None:
    """Le feste del YAML diventano oggetti Festa."""
    dati_yaml = {
        "nome_parrocchia": "Test",
        "citta": "Roma",
        "festivi_fissi": [
            {"mese": 12, "giorno": 25, "nome": "Natale"},
        ],
        "eccezioni_festivi": [],
        "divieti_pomeridiani": {"fissi": [], "mobili": []},
        "ricorrenze_proprie": [],
    }
    dati_excel = {"anno": 2027, "periodi": []}

    config = unisci_config(dati_yaml, dati_excel)
    assert len(config.festivi_fissi) == 1
    assert config.festivi_fissi[0].nome == "Natale"
    assert config.festivi_fissi[0].mese == 12
    assert config.festivi_fissi[0].giorno == 25


def test_unisci_config_ricorrenza_fissa() -> None:
    """Una ricorrenza a data fissa diventa oggetto Ricorrenza."""
    dati_yaml = {
        "nome_parrocchia": "Test",
        "citta": "Roma",
        "festivi_fissi": [],
        "eccezioni_festivi": [],
        "divieti_pomeridiani": {"fissi": [], "mobili": []},
        "ricorrenze_proprie": [
            {
                "nome": "San Salvatore",
                "data": {"mese": 3, "giorno": 17},
                "durata_giorni": 2,
            },
        ],
    }
    dati_excel = {"anno": 2027, "periodi": []}

    config = unisci_config(dati_yaml, dati_excel)
    assert len(config.ricorrenze_proprie) == 1
    ric = config.ricorrenze_proprie[0]
    assert ric.nome == "San Salvatore"
    assert ric.data_inizio == date(2027, 3, 17)
    assert ric.data_fine == date(2027, 3, 18)


def test_unisci_config_mismatch_nome() -> None:
    """Nome YAML vince su nome Excel."""
    dati_yaml = {"nome_parrocchia": "YAML Parrocchia", "citta": "Roma"}
    dati_excel = {"anno": 2027, "nome_parrocchia": "Excel Parrocchia", "citta": "Roma"}

    config = unisci_config(dati_yaml, dati_excel)
    assert config.nome_parrocchia == "YAML Parrocchia"


def test_unisci_config_periodi() -> None:
    """I periodi Excel diventano oggetti Periodo."""
    dati_yaml = {"nome_parrocchia": "Test", "citta": "Roma"}
    dati_excel = {
        "anno": 2027,
        "periodi": [
            {
                "dal": date(2027, 1, 1),
                "al": date(2027, 1, 31),
                "orari_feriali": ["7:00"],
                "orari_festivi": ["10:00"],
            },
        ],
    }

    config = unisci_config(dati_yaml, dati_excel)
    assert len(config.periodi) == 1
    assert config.periodi[0].dal == date(2027, 1, 1)
    assert config.periodi[0].orari_feriali == ["7:00"]


# ======================================================================
# TEST — carica_config
# ======================================================================


def test_carica_config_profilo_inesistente(tmp_path: Path) -> None:
    """Un profilo inesistente solleva FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Profilo non trovato"):
        carica_config("profilo_inesistente", cartella_configs=tmp_path)


def test_carica_config_yaml_mancante(tmp_path: Path) -> None:
    """Un profilo senza regole.yaml solleva FileNotFoundError."""
    profilo_dir = tmp_path / "test_profilo"
    profilo_dir.mkdir()

    with pytest.raises(FileNotFoundError, match="regole.yaml non trovato"):
        carica_config("test_profilo", cartella_configs=tmp_path)


def test_carica_config_excel_mancante(tmp_path: Path) -> None:
    """Un profilo senza config.xlsx solleva FileNotFoundError."""
    profilo_dir = tmp_path / "test_profilo"
    profilo_dir.mkdir()

    (profilo_dir / "regole.yaml").write_text(
        'nome_parrocchia: "Test"\ncitta: "Roma"\n',
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError, match="config.xlsx non trovato"):
        carica_config("test_profilo", cartella_configs=tmp_path)
