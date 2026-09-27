"""Test per il modulo lettura_yaml."""

from __future__ import annotations

from pathlib import Path

import pytest

from lettura_yaml import leggi_yaml

# ======================================================================
# FIXTURE
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
# TEST
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
