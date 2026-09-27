"""Test per il modulo calcolo_liturgico."""

from __future__ import annotations

from datetime import date

import pytest

from calcolo_liturgico import (
    calcola_domenica_palme,
    calcola_mercoledi_ceneri,
    calcola_pasqua,
)

# ======================================================================
# TEST — calcola_pasqua
# ======================================================================


def test_calcola_pasqua_2027() -> None:
    """Pasqua 2027 = 28 marzo."""
    assert calcola_pasqua(2027) == date(2027, 3, 28)


def test_calcola_pasqua_2028() -> None:
    """Pasqua 2028 = 16 aprile."""
    assert calcola_pasqua(2028) == date(2028, 4, 16)


def test_calcola_pasqua_2024() -> None:
    """Pasqua 2024 = 31 marzo."""
    assert calcola_pasqua(2024) == date(2024, 3, 31)


def test_calcola_pasqua_2025() -> None:
    """Pasqua 2025 = 20 aprile."""
    assert calcola_pasqua(2025) == date(2025, 4, 20)


def test_calcola_pasqua_2026() -> None:
    """Pasqua 2026 = 5 aprile."""
    assert calcola_pasqua(2026) == date(2026, 4, 5)


def test_calcola_pasqua_e_sempre_domenica() -> None:
    """La Pasqua cade sempre di domenica (weekday() == 6)."""
    for anno in range(2024, 2034):
        assert calcola_pasqua(anno).weekday() == 6


# ======================================================================
# TEST — calcola_mercoledi_ceneri
# ======================================================================


def test_calcola_mercoledi_ceneri_2027() -> None:
    """Mercoledì delle Ceneri 2027 = 10 febbraio."""
    assert calcola_mercoledi_ceneri(2027) == date(2027, 2, 10)


def test_calcola_mercoledi_ceneri_2028() -> None:
    """Mercoledì delle Ceneri 2028 = 1 marzo."""
    assert calcola_mercoledi_ceneri(2028) == date(2028, 3, 1)


def test_calcola_mercoledi_ceneri_e_mercoledi() -> None:
    """Le Ceneri cadono sempre di mercoledì (weekday() == 2)."""
    for anno in range(2024, 2034):
        assert calcola_mercoledi_ceneri(anno).weekday() == 2


def test_calcola_mercoledi_ceneri_46_giorni_prima() -> None:
    """Le Ceneri sono esattamente 46 giorni prima della Pasqua."""
    for anno in range(2024, 2034):
        differenza = calcola_pasqua(anno) - calcola_mercoledi_ceneri(anno)
        assert differenza.days == 46


# ======================================================================
# TEST — calcola_domenica_palme
# ======================================================================


def test_calcola_domenica_palme_2027() -> None:
    """Domenica delle Palme 2027 = 21 marzo."""
    assert calcola_domenica_palme(2027) == date(2027, 3, 21)


def test_calcola_domenica_palme_2028() -> None:
    """Domenica delle Palme 2028 = 9 aprile."""
    assert calcola_domenica_palme(2028) == date(2028, 4, 9)


def test_calcola_domenica_palme_e_domenica() -> None:
    """Le Palme cadono sempre di domenica (weekday() == 6)."""
    for anno in range(2024, 2034):
        assert calcola_domenica_palme(anno).weekday() == 6


def test_calcola_domenica_palme_7_giorni_prima() -> None:
    """Le Palme sono esattamente 7 giorni prima della Pasqua."""
    for anno in range(2024, 2034):
        differenza = calcola_pasqua(anno) - calcola_domenica_palme(anno)
        assert differenza.days == 7
