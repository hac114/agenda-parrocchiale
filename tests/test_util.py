"""Test per il modulo util."""

from __future__ import annotations

import logging

from util import WarningCollector, valore_come_stringa

# ======================================================================
# TEST — WarningCollector
# ======================================================================


def test_warning_collector_vuoto() -> None:
    """Un collector nuovo non ha warning."""
    collector = WarningCollector()
    assert not collector.ha_warning()
    assert collector.conta_warning() == 0


def test_warning_collector_raccoglie() -> None:
    """Il collector raccoglie i warning emessi."""
    collector = WarningCollector()
    collector.setFormatter(logging.Formatter("%(message)s"))

    # Emette un warning manualmente
    record = logging.LogRecord(
        name="test",
        level=logging.WARNING,
        pathname="",
        lineno=0,
        msg="Test warning",
        args=(),
        exc_info=None,
    )
    collector.emit(record)

    assert collector.ha_warning()
    assert collector.conta_warning() == 1
    assert "Test warning" in collector.warnings[0]


def test_warning_collector_svuota() -> None:
    """Svuota rimuove tutti i warning."""
    collector = WarningCollector()
    collector.setFormatter(logging.Formatter("%(message)s"))

    record = logging.LogRecord(
        name="test",
        level=logging.WARNING,
        pathname="",
        lineno=0,
        msg="Test",
        args=(),
        exc_info=None,
    )
    collector.emit(record)
    assert collector.conta_warning() == 1

    collector.svuota()
    assert not collector.ha_warning()


# ======================================================================
# TEST — valore_come_stringa
# ======================================================================


class CellaFinta:
    """Cella finta per i test."""

    def __init__(self, value: object) -> None:
        self.value = value


def test_valore_come_stringa_none() -> None:
    """Cella vuota → stringa vuota."""
    cella = CellaFinta(None)
    assert valore_come_stringa(cella) == ""


def test_valore_come_stringa_str() -> None:
    """Stringa → stessa stringa."""
    cella = CellaFinta("ciao")
    assert valore_come_stringa(cella) == "ciao"


def test_valore_come_stringa_int() -> None:
    """Numero → stringa del numero."""
    cella = CellaFinta(42)
    assert valore_come_stringa(cella) == "42"


def test_valore_come_stringa_float() -> None:
    """Float → stringa del float."""
    cella = CellaFinta(3.14)
    assert valore_come_stringa(cella) == "3.14"
