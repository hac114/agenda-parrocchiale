"""Test per il modulo generatore_agenda."""

from __future__ import annotations

from datetime import date

import pytest

from config import carica_config
from dataclass_config import Config, Festa
from generatore_agenda import _determina_tipo_giorno, _festivo_fisso

# ======================================================================
# FIXTURE
# ======================================================================


@pytest.fixture
def config_minima() -> Config:
    """Config minima con festivi fissi di base."""
    return Config(
        nome_parrocchia="Test",
        citta="Roma",
        festivi_fissi=[
            Festa(nome="Natale", mese=12, giorno=25),
            Festa(nome="Epifania", mese=1, giorno=6),
            Festa(nome="Maria SS. Madre di Dio", mese=1, giorno=1),
        ],
    )


# ======================================================================
# TEST — _festivo_fisso
# ======================================================================


def test_festivo_fisso_trovato(config_minima: Config) -> None:
    """Trova il nome del festivo."""
    assert _festivo_fisso(date(2027, 12, 25), config_minima) == "Natale"
    assert _festivo_fisso(date(2027, 1, 6), config_minima) == "Epifania"


def test_festivo_fisso_non_trovato(config_minima: Config) -> None:
    """Ritorna None se non è un festivo."""
    assert _festivo_fisso(date(2027, 1, 2), config_minima) is None
    assert _festivo_fisso(date(2027, 6, 15), config_minima) is None


# ======================================================================
# TEST — _determina_tipo_giorno
# ======================================================================


def test_tipo_giorno_festivo(config_minima: Config) -> None:
    """Un festivo fisso è tipo='festivo' con nome."""
    tipo, nome = _determina_tipo_giorno(date(2027, 12, 25), config_minima)
    assert tipo == "festivo"
    assert nome == "Natale"


def test_tipo_giorno_domenica(config_minima: Config) -> None:
    """Una domenica non festiva è tipo='domenica' senza nome."""
    # 3 gennaio 2027 = domenica, non è un festivo fisso
    tipo, nome = _determina_tipo_giorno(date(2027, 1, 3), config_minima)
    assert tipo == "domenica"
    assert nome is None


def test_tipo_giorno_feriale(config_minima: Config) -> None:
    """Un giorno feriale è tipo='feriale' senza nome."""
    # 4 gennaio 2027 = lunedì
    tipo, nome = _determina_tipo_giorno(date(2027, 1, 4), config_minima)
    assert tipo == "feriale"
    assert nome is None


def test_tipo_giorno_festivo_che_cade_di_domenica(config_minima: Config) -> None:
    """Un festivo che cade di domenica è festivo (non domenica)."""
    # Natale 2027 cade di sabato, ma testiamo il caso generale
    # Festa di Maria SS. Madre di Dio 2028 cade di sabato
    # Usiamo una data in cui un festivo cade di domenica:
    # 6 gennaio 2029 = sabato, 1 gennaio 2028 = sabato
    # Cerchiamo: 25 dicembre 2027 = sabato
    # 6 gennaio 2028 = giovedì
    # 1 gennaio 2028 = sabato
    # Festivo che cade di domenica:
    # 1 gennaio 2028 = sabato, 6 gennaio 2028 = giovedì
    # Prova: 25 dicembre 2028 = lunedì
    # Troviamo un anno in cui uno dei 3 festivi cade di domenica:
    # 25 dicembre 2022 = domenica ✓
    tipo, nome = _determina_tipo_giorno(date(2022, 12, 25), config_minima)
    assert tipo == "festivo"
    assert nome == "Natale"


def test_tipo_giorno_domenica_di_quaresima(config_minima: Config) -> None:
    """Una domenica di Quaresima è tipo='domenica' (non festivo)."""
    # 14 febbraio 2027 = I domenica di Quaresima (domenica, non festivo fisso)
    tipo, nome = _determina_tipo_giorno(date(2027, 2, 14), config_minima)
    assert tipo == "domenica"
    assert nome is None


# ======================================================================
# TEST INTEGRATIVI (con Config reale)
# ======================================================================


def test_config_reale_natale() -> None:
    """Con la Config reale, Natale 2027 è festivo."""
    config = carica_config("san_pietro_in_silki")
    tipo, nome = _determina_tipo_giorno(date(2027, 12, 25), config)
    assert tipo == "festivo"
    assert nome == "Natale"


def test_config_reale_san_salvatore_e_feriale() -> None:
    """San Salvatore (17 marzo) è feriale (è ricorrenza propria, non festivo fisso)."""
    config = carica_config("san_pietro_in_silki")
    # 17 marzo 2027 = mercoledì
    tipo, nome = _determina_tipo_giorno(date(2027, 3, 17), config)
    assert tipo == "feriale"
    assert nome is None
