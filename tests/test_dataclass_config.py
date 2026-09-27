"""Test minimi per le dataclass di dataclass_config."""

from __future__ import annotations

from datetime import date

from dataclass_config import (
    Config,
    Festa,
    Intenzione,
    Matrimonio,
    Periodo,
    Ricorrenza,
)

# ======================================================================
# TEST — Periodo
# ======================================================================


def test_periodo_default() -> None:
    """Periodo con valori di default."""
    p = Periodo(dal=date(2027, 1, 1), al=date(2027, 1, 31))
    assert p.dal == date(2027, 1, 1)
    assert p.al == date(2027, 1, 31)
    assert p.orari_feriali == []
    assert p.orari_festivi == []


def test_periodo_con_orari() -> None:
    """Periodo con orari."""
    p = Periodo(
        dal=date(2027, 1, 1),
        al=date(2027, 1, 31),
        orari_feriali=["7:00", "10:00"],
        orari_festivi=["8:30", "11:30"],
    )
    assert p.orari_feriali == ["7:00", "10:00"]
    assert p.orari_festivi == ["8:30", "11:30"]


# ======================================================================
# TEST — Festa
# ======================================================================


def test_festa_default() -> None:
    """Festa con valori di default."""
    f = Festa(nome="Natale")
    assert f.nome == "Natale"
    assert f.mese is None
    assert f.giorno is None
    assert f.tipo == "fissa"
    assert f.salta_se_domenica is False
    assert f.orari_ridotti is None


def test_festa_completa() -> None:
    """Festa con tutti i valori."""
    f = Festa(
        nome="Santo Stefano",
        mese=12,
        giorno=26,
        tipo="fissa",
        salta_se_domenica=False,
        orari_ridotti=["10:00", "18:00"],
    )
    assert f.mese == 12
    assert f.giorno == 26
    assert f.orari_ridotti == ["10:00", "18:00"]


# ======================================================================
# TEST — Ricorrenza
# ======================================================================


def test_ricorrenza_default() -> None:
    """Ricorrenza con valori di default."""
    r = Ricorrenza(nome="Triduo", data_inizio=date(2027, 3, 14))
    assert r.nome == "Triduo"
    assert r.data_inizio == date(2027, 3, 14)
    assert r.data_fine is None
    assert r.tipo == "semplice"
    assert r.compilazione == "auto"
    assert r.nota == ""


# ======================================================================
# TEST — Intenzione
# ======================================================================


def test_intenzione_minima() -> None:
    """Intenzione con solo i campi obbligatori."""
    i = Intenzione(
        numero=1,
        data_consegna=date(2027, 1, 15),
        testo="Per la pace",
    )
    assert i.numero == 1
    assert i.offerta is None
    assert i.data_applicazione is None
    assert i.note == ""


def test_intenzione_completa() -> None:
    """Intenzione con tutti i campi."""
    i = Intenzione(
        numero=5,
        data_consegna=date(2027, 1, 15),
        testo="Per i defunti",
        offerta=10.0,
        data_applicazione=date(2027, 1, 20),
        note="Richiesta da Mario",
    )
    assert i.offerta == 10.0
    assert i.data_applicazione == date(2027, 1, 20)
    assert i.note == "Richiesta da Mario"


# ======================================================================
# TEST — Matrimonio
# ======================================================================


def test_matrimonio_minimo() -> None:
    """Matrimonio con solo i campi obbligatori."""
    m = Matrimonio(
        data=date(2028, 6, 10),
        ora="15:30",
        nome_sposi="Maria e Luca",
    )
    assert m.data == date(2028, 6, 10)
    assert m.ora == "15:30"
    assert m.nome_sposi == "Maria e Luca"
    assert m.contatti == ""
    assert m.note == ""


# ======================================================================
# TEST — Config
# ======================================================================


def test_config_minima() -> None:
    """Config con solo i campi obbligatori."""
    c = Config(nome_parrocchia="Test", citta="Roma")
    assert c.nome_parrocchia == "Test"
    assert c.citta == "Roma"
    assert c.anno == 0
    assert c.festivi_fissi == []
    assert c.periodi == []
    assert c.intenzioni == []
    assert c.matrimoni_prenotati == []
    assert c.note_annuali == []


def test_config_liste_indipendenti() -> None:
    """Due istanze di Config hanno liste indipendenti (default_factory)."""
    c1 = Config(nome_parrocchia="A", citta="Roma")
    c2 = Config(nome_parrocchia="B", citta="Milano")

    c1.periodi.append(Periodo(dal=date(2027, 1, 1), al=date(2027, 1, 31)))

    assert len(c1.periodi) == 1
    assert len(c2.periodi) == 0
