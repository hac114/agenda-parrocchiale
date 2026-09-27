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


# ======================================================================
# TRIDUO PASQUALE
# ======================================================================


def calcola_giovedi_santo(anno: int) -> date:
    """Giovedì Santo: 3 giorni prima della Pasqua.

    Args:
        anno: anno di riferimento

    Returns:
        Data del Giovedì Santo.

    Examples:
        >>> calcola_giovedi_santo(2027)
        datetime.date(2027, 3, 25)
    """
    return calcola_pasqua(anno) - timedelta(days=3)


def calcola_venerdi_santo(anno: int) -> date:
    """Venerdì Santo: 2 giorni prima della Pasqua.

    Args:
        anno: anno di riferimento

    Returns:
        Data del Venerdì Santo.

    Examples:
        >>> calcola_venerdi_santo(2027)
        datetime.date(2027, 3, 26)
    """
    return calcola_pasqua(anno) - timedelta(days=2)


def calcola_sabato_santo(anno: int) -> date:
    """Sabato Santo: 1 giorno prima della Pasqua.

    Args:
        anno: anno di riferimento

    Returns:
        Data del Sabato Santo.

    Examples:
        >>> calcola_sabato_santo(2027)
        datetime.date(2027, 3, 27)
    """
    return calcola_pasqua(anno) - timedelta(days=1)


# ======================================================================
# FESTE DOPO PASQUA
# ======================================================================


def calcola_lunedi_angelo(anno: int) -> date:
    """Lunedì dell'Angelo: 1 giorno dopo la Pasqua.

    Args:
        anno: anno di riferimento

    Returns:
        Data del Lunedì dell'Angelo.

    Examples:
        >>> calcola_lunedi_angelo(2027)
        datetime.date(2027, 3, 29)
    """
    return calcola_pasqua(anno) + timedelta(days=1)


def calcola_ascensione(anno: int) -> date:
    """Ascensione: 39 giorni dopo la Pasqua (giovedì).

    Args:
        anno: anno di riferimento

    Returns:
        Data dell'Ascensione.

    Examples:
        >>> calcola_ascensione(2027)
        datetime.date(2027, 5, 6)
    """
    return calcola_pasqua(anno) + timedelta(days=39)


def calcola_pentecoste(anno: int) -> date:
    """Pentecoste: 49 giorni dopo la Pasqua (domenica).

    Args:
        anno: anno di riferimento

    Returns:
        Data della Pentecoste.

    Examples:
        >>> calcola_pentecoste(2027)
        datetime.date(2027, 5, 16)
    """
    return calcola_pasqua(anno) + timedelta(days=49)


def calcola_trinita(anno: int) -> date:
    """Santissima Trinità: 56 giorni dopo la Pasqua (domenica).

    Args:
        anno: anno di riferimento

    Returns:
        Data della Santissima Trinità.

    Examples:
        >>> calcola_trinita(2027)
        datetime.date(2027, 5, 23)
    """
    return calcola_pasqua(anno) + timedelta(days=56)


def calcola_corpus_domini(anno: int) -> date:
    """Corpus Domini: 60 giorni dopo la Pasqua (giovedì).

    Args:
        anno: anno di riferimento

    Returns:
        Data del Corpus Domini.

    Examples:
        >>> calcola_corpus_domini(2027)
        datetime.date(2027, 5, 27)
    """
    return calcola_pasqua(anno) + timedelta(days=60)


# ======================================================================
# DOMENICHE DI QUARESIMA
# ======================================================================


def calcola_domeniche_quaresima(anno: int) -> list[date]:
    """Calcola le 5 domeniche di Quaresima (I, II, III, IV, V).

    La Quaresima inizia il Mercoledì delle Ceneri. Le prime 5 domeniche
    dopo le Ceneri sono chiamate "domeniche di Quaresima".
    La VI domenica è la Domenica delle Palme (calcolata a parte).

    Args:
        anno: anno di riferimento

    Returns:
        Lista di 5 date, in ordine cronologico:
        [I domenica, II domenica, III domenica, IV domenica, V domenica].

    Examples:
        >>> calcola_domeniche_quaresima(2027)
        [date(2027, 2, 14), date(2027, 2, 21), date(2027, 2, 28),
         date(2027, 3, 7), date(2027, 3, 14)]
    """
    ceneri = calcola_mercoledi_ceneri(anno)

    # Trova la prima domenica dopo le Ceneri
    # ceneri.weekday() = 2 (mercoledì)
    # Giorni da aggiungere per arrivare alla prossima domenica (weekday = 6):
    #   mercoledì → domenica = +4
    #   giovedì → domenica = +3
    #   ... ecc. (ma le Ceneri sono sempre mercoledì)
    giorni_a_domenica = (6 - ceneri.weekday()) % 7
    prima_domenica = ceneri + timedelta(days=giorni_a_domenica)

    # Le 5 domeniche sono consecutive (7 giorni di distanza)
    return [prima_domenica + timedelta(weeks=i) for i in range(5)]


# ======================================================================
# DOMENICHE DI AVVENTO
# ======================================================================


def calcola_domeniche_avvento(anno: int) -> list[date]:
    """Calcola le 4 domeniche di Avvento.

    Sono le 4 domeniche che precedono il Natale (25 dicembre).
    La IV domenica di Avvento è l'ultima domenica prima di Natale.

    Args:
        anno: anno di riferimento

    Returns:
        Lista di 4 date, in ordine cronologico:
        [I domenica, II domenica, III domenica, IV domenica].

    Examples:
        >>> calcola_domeniche_avvento(2027)
        [date(2027, 11, 28), date(2027, 12, 5),
         date(2027, 12, 12), date(2027, 12, 19)]
    """
    natale = date(anno, 12, 25)

    # L'ultima domenica PRIMA di Natale
    # Se Natale è domenica (weekday 6), l'ultima domenica di Avvento
    # è 7 giorni prima (non lo stesso giorno)
    giorni_a_domenica = (natale.weekday() - 6) % 7
    if giorni_a_domenica == 0:
        giorni_a_domenica = 7
    quarta_domenica = natale - timedelta(days=giorni_a_domenica)

    # Le 4 domeniche sono consecutive: la IV è l'ultima, I è 3 settimane prima
    prima_domenica = quarta_domenica - timedelta(weeks=3)
    return [prima_domenica + timedelta(weeks=i) for i in range(4)]


# ======================================================================
# NOVE MERCOLEDÌ DI SAN SALVATORE
# ======================================================================


def calcola_nove_mercoledi(anno: int) -> list[date]:
    """Calcola i 9 mercoledì che precedono il Triduo di San Salvatore.

    Regola (interpretazione del santuario):
    - Il 9° mercoledì è il mercoledì immediatamente PRIMA del 14 marzo.
    - Il 1° mercoledì è 8 settimane prima del 9° (= 9° - 56 giorni).
    - Tutti i mercoledì sono consecutivi (7 giorni di distanza).

    Note:
        - Il Triduo è fisso dal 14 al 16 marzo (non dipende dal giorno).
        - Se il 14 marzo cade di mercoledì, il 9° mercoledì è il 7 marzo
          (il mercoledì precedente, perché la regola dice "che precedono").

    Args:
        anno: anno di riferimento

    Returns:
        Lista di 9 date, in ordine cronologico:
        [1° mercoledì, 2° mercoledì, ..., 9° mercoledì].

    Examples:
        >>> calcola_nove_mercoledi(2027)
        [date(2027, 1, 13), date(2027, 1, 20), date(2027, 1, 27),
         date(2027, 2, 3), date(2027, 2, 10), date(2027, 2, 17),
         date(2027, 2, 24), date(2027, 3, 3), date(2027, 3, 10)]
    """
    triduo_inizio = date(anno, 3, 14)

    # Trova il mercoledì immediatamente prima del 14 marzo
    # weekday: lunedì=0, martedì=1, ..., domenica=6
    # Mercoledì: weekday = 2
    # Se il 14 marzo è mercoledì, vogliamo il mercoledì precedente (7 giorni prima)
    giorni_indietro = (triduo_inizio.weekday() - 2) % 7
    if giorni_indietro == 0:
        # Il 14 marzo è mercoledì → usa il mercoledì precedente
        giorni_indietro = 7

    nono_mercoledi = triduo_inizio - timedelta(days=giorni_indietro)

    # Il 1° mercoledì è 8 settimane prima del 9°
    primo_mercoledi = nono_mercoledi - timedelta(weeks=8)

    # Genera i 9 mercoledì consecutivi
    return [primo_mercoledi + timedelta(weeks=i) for i in range(9)]


# ======================================================================
# FESTA DEL VOTO
# ======================================================================


def calcola_ultima_domenica_maggio(anno: int) -> date:
    """Calcola l'ultima domenica di maggio dell'anno dato.

    Args:
        anno: anno di riferimento

    Returns:
        Data dell'ultima domenica di maggio.
    """
    # 31 maggio
    fine_maggio = date(anno, 5, 31)
    # Torna indietro fino a domenica (weekday = 6)
    giorni_indietro = (fine_maggio.weekday() - 6) % 7
    return fine_maggio - timedelta(days=giorni_indietro)


def calcola_prima_domenica_giugno(anno: int) -> date:
    """Calcola la prima domenica di giugno dell'anno dato.

    Args:
        anno: anno di riferimento

    Returns:
        Data della prima domenica di giugno.
    """
    # 1 giugno
    inizio_giugno = date(anno, 6, 1)
    # Avanza fino a domenica (weekday = 6)
    giorni_avanti = (6 - inizio_giugno.weekday()) % 7
    return inizio_giugno + timedelta(days=giorni_avanti)


def calcola_festa_voto(anno: int) -> date:
    """Calcola la data della Festa del Voto.

    Regola (interpretazione del santuario):
    - Normalmente: ultima domenica di maggio.
    - Se coincide con la domenica del Corpus Domini (la domenica
      immediatamente successiva al giovedì del Corpus Domini),
      slitta alla prima domenica di giugno.

    Args:
        anno: anno di riferimento

    Returns:
        Data della Festa del Voto.

    Examples:
        >>> calcola_festa_voto(2027)
        datetime.date(2027, 6, 6)   # slitta perché coincide con la domenica del Corpus Domini
    """
    ultima_domenica_maggio = calcola_ultima_domenica_maggio(anno)

    # Corpus Domini (giovedì) + 3 giorni = domenica del Corpus Domini
    corpus_domini = calcola_corpus_domini(anno)
    domenica_corpus_domini = corpus_domini + timedelta(days=3)

    # Se la Festa del Voto coincide con la domenica del Corpus Domini, slitta
    if ultima_domenica_maggio == domenica_corpus_domini:
        logger.info(
            "Festa del Voto %d: slitta a giugno (coincide con la domenica "
            "del Corpus Domini del %s)",
            anno,
            domenica_corpus_domini,
        )
        return calcola_prima_domenica_giugno(anno)

    return ultima_domenica_maggio


# ======================================================================
# API PUBBLICA
# ======================================================================


def calcola_tutte_date_mobili(anno: int) -> dict[str, date | list[date]]:
    """Calcola tutte le date mobili dell'anno liturgico.

    Restituisce un dizionario con tutte le date mobili (dipendenti dalla
    Pasqua) e le liste di date mobili (domeniche di Quaresima, Avvento,
    nove mercoledì di San Salvatore, ecc.).

    Args:
        anno: anno di riferimento

    Returns:
        Dizionario con chiavi snake_case. Ogni valore è:
        - una `date` per le feste singole
        - una `list[date]` per le feste multi-giorno o le liste di date

    Examples:
        >>> date_mobili = calcola_tutte_date_mobili(2027)
        >>> date_mobili["pasqua"]
        datetime.date(2027, 3, 28)
    """
    return {
        # --- Feste singole ---
        "pasqua": calcola_pasqua(anno),
        "mercoledi_ceneri": calcola_mercoledi_ceneri(anno),
        "domenica_palme": calcola_domenica_palme(anno),
        "giovedi_santo": calcola_giovedi_santo(anno),
        "venerdi_santo": calcola_venerdi_santo(anno),
        "sabato_santo": calcola_sabato_santo(anno),
        "lunedi_angelo": calcola_lunedi_angelo(anno),
        "ascensione": calcola_ascensione(anno),
        "pentecoste": calcola_pentecoste(anno),
        "trinita": calcola_trinita(anno),
        "corpus_domini": calcola_corpus_domini(anno),
        "festa_voto": calcola_festa_voto(anno),
        # --- Liste di date ---
        "domeniche_quaresima": calcola_domeniche_quaresima(anno),
        "domeniche_avvento": calcola_domeniche_avvento(anno),
        "nove_mercoledi": calcola_nove_mercoledi(anno),
    }
