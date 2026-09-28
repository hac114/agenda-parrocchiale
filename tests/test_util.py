"""Test per il modulo util."""

from __future__ import annotations

import logging

import pytest

from util import (
    WarningCollector,
    configura_logging,
    mostra_riepilogo_warning,
    valore_come_stringa,
)

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


# ======================================================================
# TEST — configura_logging
# ======================================================================


def test_configura_logging_restituisce_collector() -> None:
    """configura_logging restituisce un WarningCollector."""
    collector = configura_logging()
    assert isinstance(collector, WarningCollector)


def test_configura_logging_aggiunge_handler() -> None:
    """configura_logging aggiunge il collector al logger root."""
    collector = configura_logging()

    # Emette un warning per verificare che il collector lo catturi
    logger = logging.getLogger("test_configura_logging")
    logger.warning("Test warning")

    assert collector.conta_warning() >= 1


# ======================================================================
# TEST — mostra_riepilogo_warning
# ======================================================================


def test_mostra_riepilogo_senza_warning() -> None:
    """Se non ci sono warning, restituisce True senza chiedere nulla."""
    collector = WarningCollector()
    assert mostra_riepilogo_warning(collector) is True


def test_mostra_riepilogo_con_warning_yes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Con warning e risposta 'y' → True."""
    collector = WarningCollector()
    collector.warnings.append("Test warning")

    # Simula input dell'utente: "y"
    monkeypatch.setattr("builtins.input", lambda _: "y")

    assert mostra_riepilogo_warning(collector) is True


def test_mostra_riepilogo_con_warning_no(monkeypatch: pytest.MonkeyPatch) -> None:
    """Con warning e risposta 'n' → False."""
    collector = WarningCollector()
    collector.warnings.append("Test warning")

    # Simula input dell'utente: "n"
    monkeypatch.setattr("builtins.input", lambda _: "n")

    assert mostra_riepilogo_warning(collector) is False


def test_mostra_riepilogo_con_warning_si(monkeypatch: pytest.MonkeyPatch) -> None:
    """Con warning e risposta 'sì' → True."""
    collector = WarningCollector()
    collector.warnings.append("Test warning")

    monkeypatch.setattr("builtins.input", lambda _: "sì")

    assert mostra_riepilogo_warning(collector) is True
