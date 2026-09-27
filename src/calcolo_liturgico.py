"""
Calcolo del calendario liturgico per un anno.

Contiene funzioni per calcolare:
- La Pasqua (algoritmo di Gauss/Meeus)
- Le feste mobili che dipendono dalla Pasqua
- Le domeniche di Quaresima e Avvento
- Le ricorrenze proprie del santuario (9 mercoledì di San Salvatore, ecc.)

Uso tipico:
    from calcolo_liturgico import calcola_pasqua, calcola_domenica_palme

    pasqua = calcola_pasqua(2027)          # date(2027, 3, 28)
    palme = calcola_domenica_palme(2027)   # date(2027, 3, 21)

Tutte le funzioni sono pure: prendono un anno (int) e restituiscono date.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

# ======================================================================
# PASQUA
# ======================================================================


def calcola_pasqua(anno: int) -> date:
    """Calcola la data della Pasqua con l'algoritmo di Gauss/Meeus.

    L'algoritmo funziona per gli anni 1583-4099 nel calendario gregoriano.

    Args:
        anno: anno per cui calcolare la Pasqua (es. 2027)

    Returns:
        Data della domenica di Pasqua.

    Examples:
        >>> calcola_pasqua(2027)
        datetime.date(2027, 3, 28)
        >>> calcola_pasqua(2028)
        datetime.date(2028, 4, 16)
    """
    # Algoritmo di Meeus/Jones/Butcher
    a = anno % 19
    b = anno // 100
    c = anno % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mese = (h + l - 7 * m + 114) // 31
    giorno = ((h + l - 7 * m + 114) % 31) + 1

    return date(anno, mese, giorno)


# ======================================================================
# FESTE MOBILI (dipendono dalla Pasqua)
# ======================================================================


def calcola_mercoledi_ceneri(anno: int) -> date:
    """Mercoledì delle Ceneri: 46 giorni prima della Pasqua.

    Args:
        anno: anno di riferimento

    Returns:
        Data del Mercoledì delle Ceneri.

    Examples:
        >>> calcola_mercoledi_ceneri(2027)
        datetime.date(2027, 2, 10)
    """
    return calcola_pasqua(anno) - timedelta(days=46)


def calcola_domenica_palme(anno: int) -> date:
    """Domenica delle Palme: 7 giorni prima della Pasqua.

    Args:
        anno: anno di riferimento

    Returns:
        Data della Domenica delle Palme.

    Examples:
        >>> calcola_domenica_palme(2027)
        datetime.date(2027, 3, 21)
    """
    return calcola_pasqua(anno) - timedelta(days=7)
