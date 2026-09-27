"""Test per il modulo calcolo_liturgico."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from calcolo_liturgico import (
    calcola_ascensione,
    calcola_corpus_domini,
    calcola_domenica_palme,
    calcola_domeniche_avvento,
    calcola_domeniche_quaresima,
    calcola_giovedi_santo,
    calcola_lunedi_angelo,
    calcola_mercoledi_ceneri,
    calcola_pasqua,
    calcola_pentecoste,
    calcola_sabato_santo,
    calcola_trinita,
    calcola_venerdi_santo,
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


# ======================================================================
# TEST — Triduo Pasquale
# ======================================================================


def test_calcola_giovedi_santo_2027() -> None:
    """Giovedì Santo 2027 = 25 marzo."""
    assert calcola_giovedi_santo(2027) == date(2027, 3, 25)


def test_calcola_venerdi_santo_2027() -> None:
    """Venerdì Santo 2027 = 26 marzo."""
    assert calcola_venerdi_santo(2027) == date(2027, 3, 26)


def test_calcola_sabato_santo_2027() -> None:
    """Sabato Santo 2027 = 27 marzo."""
    assert calcola_sabato_santo(2027) == date(2027, 3, 27)


def test_triduo_pasquale_ordine() -> None:
    """I tre giorni del Triduo sono consecutivi e nell'ordine giusto."""
    for anno in range(2024, 2034):
        giovedi = calcola_giovedi_santo(anno)
        venerdi = calcola_venerdi_santo(anno)
        sabato = calcola_sabato_santo(anno)
        assert venerdi == giovedi + timedelta(days=1)
        assert sabato == venerdi + timedelta(days=1)


# ======================================================================
# TEST — Lunedì dell'Angelo
# ======================================================================


def test_calcola_lunedi_angelo_2027() -> None:
    """Lunedì dell'Angelo 2027 = 29 marzo."""
    assert calcola_lunedi_angelo(2027) == date(2027, 3, 29)


def test_calcola_lunedi_angelo_e_lunedi() -> None:
    """Il Lunedì dell'Angelo cade sempre di lunedì (weekday() == 0)."""
    for anno in range(2024, 2034):
        assert calcola_lunedi_angelo(anno).weekday() == 0


# ======================================================================
# TEST — Ascensione
# ======================================================================


def test_calcola_ascensione_2027() -> None:
    """Ascensione 2027 = 6 maggio."""
    assert calcola_ascensione(2027) == date(2027, 5, 6)


def test_calcola_ascensione_e_giovedi() -> None:
    """L'Ascensione cade sempre di giovedì (weekday() == 3)."""
    for anno in range(2024, 2034):
        assert calcola_ascensione(anno).weekday() == 3


def test_calcola_ascensione_39_giorni_dopo() -> None:
    """L'Ascensione è esattamente 39 giorni dopo la Pasqua."""
    for anno in range(2024, 2034):
        differenza = calcola_ascensione(anno) - calcola_pasqua(anno)
        assert differenza.days == 39


# ======================================================================
# TEST — Pentecoste
# ======================================================================


def test_calcola_pentecoste_2027() -> None:
    """Pentecoste 2027 = 16 maggio."""
    assert calcola_pentecoste(2027) == date(2027, 5, 16)


def test_calcola_pentecoste_e_domenica() -> None:
    """La Pentecoste cade sempre di domenica (weekday() == 6)."""
    for anno in range(2024, 2034):
        assert calcola_pentecoste(anno).weekday() == 6


def test_calcola_pentecoste_49_giorni_dopo() -> None:
    """La Pentecoste è esattamente 49 giorni dopo la Pasqua."""
    for anno in range(2024, 2034):
        differenza = calcola_pentecoste(anno) - calcola_pasqua(anno)
        assert differenza.days == 49


# ======================================================================
# TEST — Santissima Trinità
# ======================================================================


def test_calcola_trinita_2027() -> None:
    """Santissima Trinità 2027 = 23 maggio."""
    assert calcola_trinita(2027) == date(2027, 5, 23)


def test_calcola_trinita_e_domenica() -> None:
    """La Trinità cade sempre di domenica."""
    for anno in range(2024, 2034):
        assert calcola_trinita(anno).weekday() == 6


def test_calcola_trinita_56_giorni_dopo() -> None:
    """La Trinità è esattamente 56 giorni dopo la Pasqua."""
    for anno in range(2024, 2034):
        differenza = calcola_trinita(anno) - calcola_pasqua(anno)
        assert differenza.days == 56


# ======================================================================
# TEST — Corpus Domini
# ======================================================================


def test_calcola_corpus_domini_2027() -> None:
    """Corpus Domini 2027 = 27 maggio."""
    assert calcola_corpus_domini(2027) == date(2027, 5, 27)


def test_calcola_corpus_domini_e_giovedi() -> None:
    """Il Corpus Domini cade sempre di giovedì (weekday() == 3)."""
    for anno in range(2024, 2034):
        assert calcola_corpus_domini(anno).weekday() == 3


def test_calcola_corpus_domini_60_giorni_dopo() -> None:
    """Il Corpus Domini è esattamente 60 giorni dopo la Pasqua."""
    for anno in range(2024, 2034):
        differenza = calcola_corpus_domini(anno) - calcola_pasqua(anno)
        assert differenza.days == 60


# ======================================================================
# TEST — Domeniche di Quaresima
# ======================================================================


def test_domeniche_quaresima_2027() -> None:
    """Le 5 domeniche di Quaresima 2027."""
    attese = [
        date(2027, 2, 14),
        date(2027, 2, 21),
        date(2027, 2, 28),
        date(2027, 3, 7),
        date(2027, 3, 14),
    ]
    assert calcola_domeniche_quaresima(2027) == attese


def test_domeniche_quaresima_sono_5() -> None:
    """Restituisce esattamente 5 domeniche."""
    for anno in range(2024, 2034):
        assert len(calcola_domeniche_quaresima(anno)) == 5


def test_domeniche_quaresima_sono_domeniche() -> None:
    """Tutte le domeniche di Quaresima cadono di domenica."""
    for anno in range(2024, 2034):
        for d in calcola_domeniche_quaresima(anno):
            assert d.weekday() == 6


def test_domeniche_quaresima_sono_consecutive() -> None:
    """Le domeniche sono consecutive (7 giorni di distanza)."""
    for anno in range(2024, 2034):
        domeniche = calcola_domeniche_quaresima(anno)
        for i in range(len(domeniche) - 1):
            differenza = domeniche[i + 1] - domeniche[i]
            assert differenza.days == 7


def test_domeniche_quaresima_dopo_le_ceneri() -> None:
    """La I domenica di Quaresima è dopo le Ceneri."""
    for anno in range(2024, 2034):
        ceneri = calcola_mercoledi_ceneri(anno)
        prima_domenica = calcola_domeniche_quaresima(anno)[0]
        assert prima_domenica > ceneri
        # Non più di 4 giorni dopo (le Ceneri sono mercoledì)
        assert (prima_domenica - ceneri).days <= 4


def test_domeniche_quaresima_prima_delle_palme() -> None:
    """La V domenica di Quaresima è prima delle Palme."""
    for anno in range(2024, 2034):
        quinta = calcola_domeniche_quaresima(anno)[-1]
        palme = calcola_domenica_palme(anno)
        assert quinta < palme
        assert (palme - quinta).days == 7


# ======================================================================
# TEST — Domeniche di Avvento
# ======================================================================


def test_domeniche_avvento_2027() -> None:
    """Le 4 domeniche di Avvento 2027."""
    attese = [
        date(2027, 11, 28),
        date(2027, 12, 5),
        date(2027, 12, 12),
        date(2027, 12, 19),
    ]
    assert calcola_domeniche_avvento(2027) == attese


def test_domeniche_avvento_sono_4() -> None:
    """Restituisce esattamente 4 domeniche."""
    for anno in range(2024, 2034):
        assert len(calcola_domeniche_avvento(anno)) == 4


def test_domeniche_avvento_sono_domeniche() -> None:
    """Tutte le domeniche di Avvento cadono di domenica."""
    for anno in range(2024, 2034):
        for d in calcola_domeniche_avvento(anno):
            assert d.weekday() == 6


def test_domeniche_avvento_sono_consecutive() -> None:
    """Le domeniche sono consecutive (7 giorni di distanza)."""
    for anno in range(2024, 2034):
        domeniche = calcola_domeniche_avvento(anno)
        for i in range(len(domeniche) - 1):
            differenza = domeniche[i + 1] - domeniche[i]
            assert differenza.days == 7


def test_domeniche_avvento_prima_di_natale() -> None:
    """L'ultima domenica di Avvento è prima di Natale (25 dicembre)."""
    for anno in range(2024, 2034):
        natale = date(anno, 12, 25)
        quarta = calcola_domeniche_avvento(anno)[-1]
        assert quarta < natale
        # Al massimo 7 giorni prima
        assert (natale - quarta).days <= 7


def test_domeniche_avvento_natale_di_domenica() -> None:
    """Se Natale cade di domenica, la IV domenica è 7 giorni prima."""
    # 2022: Natale era domenica
    domeniche = calcola_domeniche_avvento(2022)
    quarta = domeniche[-1]
    assert quarta == date(2022, 12, 18)  # 7 giorni prima del 25/12/2022
