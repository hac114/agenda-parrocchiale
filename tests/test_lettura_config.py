"""Test per il modulo lettura_config."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import cast

import pytest
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from lettura_config import (
    leggi_foglio_impostazioni,
    leggi_yaml,
    parse_orari,
)

# ======================================================================
# HELPER
# ======================================================================


def crea_foglio_vuoto() -> Worksheet:
    """Crea un foglio Excel vuoto per i test.

    Il cast è necessario perché openpyxl tipizza `wb.active` come
    `Worksheet | None`, anche se per un Workbook appena creato è
    sempre valorizzato.
    """
    wb = Workbook()
    return cast(Worksheet, wb.active)


# ======================================================================
# FIXTURE — YAML
# ======================================================================


@pytest.fixture
def yaml_valido(tmp_path: Path) -> Path:
    """Crea un file YAML valido temporaneo."""
    percorso = tmp_path / "valido.yaml"
    percorso.write_text(
        """
nome: Test
valori:
  - 1
  - 2
  - 3
""",
        encoding="utf-8",
    )
    return percorso


@pytest.fixture
def yaml_vuoto(tmp_path: Path) -> Path:
    """Crea un file YAML vuoto."""
    percorso = tmp_path / "vuoto.yaml"
    percorso.write_text("", encoding="utf-8")
    return percorso


@pytest.fixture
def yaml_malformato(tmp_path: Path) -> Path:
    """Crea un file YAML malformato (tab character dove non ammesso)."""
    percorso = tmp_path / "malformato.yaml"
    percorso.write_text(
        "chiave:\n\tvalore\n",
        encoding="utf-8",
    )
    return percorso


# ======================================================================
# FIXTURE — Foglio Impostazioni
# ======================================================================


@pytest.fixture
def foglio_impostazioni_valido() -> Worksheet:
    """Crea un foglio Impostazioni valido in memoria."""
    ws = crea_foglio_vuoto()
    ws.title = "Impostazioni"

    # Dati generali
    ws["B5"] = 2027
    ws["B6"] = "San Pietro in Silki"
    ws["B7"] = "Sassari"

    # Periodo 1: inverno
    ws.cell(row=13, column=1, value=date(2027, 10, 1))
    ws.cell(row=13, column=2, value=date(2028, 4, 30))
    ws.cell(row=13, column=3, value="7:00,10:00,18:00")
    ws.cell(row=13, column=4, value="8:30,10:00,11:30,18:00")

    # Periodo 2: maggio
    ws.cell(row=14, column=1, value=date(2027, 5, 1))
    ws.cell(row=14, column=2, value=date(2027, 5, 31))
    ws.cell(row=14, column=3, value="6:15,7:00,8:30,10:00,11:30,17:30,18:30")
    ws.cell(row=14, column=4, value="6:15,7:00,8:30,10:00,11:30,17:30,18:30")

    return ws


# ======================================================================
# TEST — leggi_yaml
# ======================================================================


def test_leggi_yaml_valido(yaml_valido: Path) -> None:
    """Un YAML valido viene letto correttamente."""
    dati = leggi_yaml(yaml_valido)
    assert dati["nome"] == "Test"
    assert dati["valori"] == [1, 2, 3]


def test_leggi_yaml_vuoto(yaml_vuoto: Path) -> None:
    """Un YAML vuoto restituisce un dict vuoto."""
    dati = leggi_yaml(yaml_vuoto)
    assert dati == {}


def test_leggi_yaml_non_esiste(tmp_path: Path) -> None:
    """Un file inesistente solleva FileNotFoundError."""
    percorso = tmp_path / "non_esiste.yaml"
    with pytest.raises(FileNotFoundError):
        leggi_yaml(percorso)


def test_leggi_yaml_malformato(yaml_malformato: Path) -> None:
    """Uno YAML malformato solleva ValueError."""
    with pytest.raises(ValueError, match="YAML malformato"):
        leggi_yaml(yaml_malformato)


# ======================================================================
# TEST — parse_orari
# ======================================================================


def test_parse_orari_virgole() -> None:
    """Orari separati da virgola."""
    assert parse_orari("7:00,10:00,18:00") == ["7:00", "10:00", "18:00"]


def test_parse_orari_punto_virgola() -> None:
    """Orari separati da punto e virgola."""
    assert parse_orari("7:00;10:00") == ["7:00", "10:00"]


def test_parse_orari_spazi() -> None:
    """Orari separati da spazi."""
    assert parse_orari("7:00 10:00 18:00") == ["7:00", "10:00", "18:00"]


def test_parse_orari_vuoto() -> None:
    """Stringa vuota → lista vuota."""
    assert parse_orari("") == []


def test_parse_orari_valori_invalidi() -> None:
    """Valori non validi vengono ignorati."""
    assert parse_orari("7:00,pippo,18:00") == ["7:00", "18:00"]
    assert parse_orari("7.00,10:00") == ["10:00"]


def test_parse_orari_misto() -> None:
    """Separatori misti."""
    assert parse_orari("7:00, 10:00; 18:00") == ["7:00", "10:00", "18:00"]


# ======================================================================
# TEST — leggi_foglio_impostazioni
# ======================================================================


def test_leggi_impostazioni_valido(foglio_impostazioni_valido: Worksheet) -> None:
    """Un foglio valido viene letto correttamente."""
    dati = leggi_foglio_impostazioni(foglio_impostazioni_valido)
    assert dati["anno"] == 2027
    assert dati["nome_parrocchia"] == "San Pietro in Silki"
    assert dati["citta"] == "Sassari"
    assert len(dati["periodi"]) == 2
    assert dati["periodi"][0]["dal"] == date(2027, 10, 1)
    assert dati["periodi"][0]["orari_feriali"] == ["7:00", "10:00", "18:00"]
    assert dati["periodi"][1]["orari_festivi"] == [
        "6:15",
        "7:00",
        "8:30",
        "10:00",
        "11:30",
        "17:30",
        "18:30",
    ]


def test_leggi_impostazioni_anno_mancante() -> None:
    """Se manca l'anno → ValueError."""
    ws = crea_foglio_vuoto()
    ws["B5"] = None
    ws["B6"] = "Test"
    ws["B7"] = "Test"

    with pytest.raises(ValueError, match="Anno"):
        leggi_foglio_impostazioni(ws)


def test_leggi_impostazioni_nome_mancante() -> None:
    """Se manca il nome parrocchia → ValueError."""
    ws = crea_foglio_vuoto()
    ws["B5"] = 2027
    ws["B6"] = None
    ws["B7"] = "Test"

    with pytest.raises(ValueError, match="Nome parrocchia"):
        leggi_foglio_impostazioni(ws)


def test_leggi_impostazioni_riga_parziale() -> None:
    """Una riga con solo 'Dal' viene ignorata con warning."""
    ws = crea_foglio_vuoto()
    ws["B5"] = 2027
    ws["B6"] = "Test"
    ws["B7"] = "Test"

    ws.cell(row=13, column=1, value=date(2027, 10, 1))
    ws.cell(row=13, column=3, value="7:00")

    dati = leggi_foglio_impostazioni(ws)
    assert len(dati["periodi"]) == 0


def test_leggi_impostazioni_riga_non_data() -> None:
    """Una riga con valore non-data viene ignorata con warning."""
    ws = crea_foglio_vuoto()
    ws["B5"] = 2027
    ws["B6"] = "Test"
    ws["B7"] = "Test"

    ws.cell(row=13, column=1, value="01/10/2027")
    ws.cell(row=13, column=2, value="30/04/2028")

    dati = leggi_foglio_impostazioni(ws)
    assert len(dati["periodi"]) == 0
