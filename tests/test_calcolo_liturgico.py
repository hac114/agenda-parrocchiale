"""Test per il modulo calcolo_liturgico."""

from __future__ import annotations

from datetime import date, timedelta

from calcolo_liturgico import (
    calcola_ascensione,
    calcola_corpus_domini,
    calcola_domenica_palme,
    calcola_domeniche_avvento,
    calcola_domeniche_quaresima,
    calcola_festa_voto,
    calcola_giovedi_santo,
    calcola_lunedi_angelo,
    calcola_mercoledi_ceneri,
    calcola_nove_mercoledi,
    calcola_pasqua,
    calcola_pentecoste,
    calcola_prima_domenica_giugno,
    calcola_sabato_santo,
    calcola_trinita,
    calcola_tutte_date_mobili,
    calcola_ultima_domenica_maggio,
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


# ======================================================================
# TEST — Nove mercoledì di San Salvatore
# ======================================================================


def test_nove_mercoledi_2027() -> None:
    """I 9 mercoledì di San Salvatore 2027."""
    attesi = [
        date(2027, 1, 13),
        date(2027, 1, 20),
        date(2027, 1, 27),
        date(2027, 2, 3),
        date(2027, 2, 10),
        date(2027, 2, 17),
        date(2027, 2, 24),
        date(2027, 3, 3),
        date(2027, 3, 10),
    ]
    assert calcola_nove_mercoledi(2027) == attesi


def test_nove_mercoledi_sono_9() -> None:
    """Restituisce esattamente 9 date."""
    for anno in range(2024, 2034):
        assert len(calcola_nove_mercoledi(anno)) == 9


def test_nove_mercoledi_sono_mercoledi() -> None:
    """Tutte le date cadono di mercoledì (weekday() == 2)."""
    for anno in range(2024, 2034):
        for d in calcola_nove_mercoledi(anno):
            assert d.weekday() == 2


def test_nove_mercoledi_sono_consecutivi() -> None:
    """Tutti i mercoledì sono consecutivi (7 giorni di distanza)."""
    for anno in range(2024, 2034):
        mercoledi = calcola_nove_mercoledi(anno)
        for i in range(len(mercoledi) - 1):
            differenza = mercoledi[i + 1] - mercoledi[i]
            assert differenza.days == 7


def test_nove_mercoledi_prima_del_triduo() -> None:
    """Il 9° mercoledì è prima del 14 marzo (Triduo)."""
    for anno in range(2024, 2034):
        triduo_inizio = date(anno, 3, 14)
        nono = calcola_nove_mercoledi(anno)[-1]
        assert nono < triduo_inizio
        # Al massimo 7 giorni prima
        assert (triduo_inizio - nono).days <= 7


def test_nove_mercoledi_2028() -> None:
    """I 9 mercoledì di San Salvatore 2028 (14 marzo = martedì)."""
    mercoledi = calcola_nove_mercoledi(2028)
    # 14 marzo 2028 = martedì, quindi il 9° mercoledì è l'8 marzo
    assert mercoledi[-1] == date(2028, 3, 8)
    # Il 1° è 8 settimane prima
    assert mercoledi[0] == date(2028, 1, 12)


def test_nove_mercoledi_14_marzo_mercoledi() -> None:
    """Se il 14 marzo è mercoledì, il 9° è il mercoledì precedente (7 marzo).

    Caso speciale: 2029 (14 marzo è mercoledì).
    """
    # Verifica che 14 marzo 2029 sia effettivamente mercoledì
    assert date(2029, 3, 14).weekday() == 2

    mercoledi = calcola_nove_mercoledi(2029)
    # Il 9° deve essere il 7 marzo (non il 14)
    assert mercoledi[-1] == date(2029, 3, 7)


# ======================================================================
# TEST — Ultima domenica di maggio
# ======================================================================


def test_ultima_domenica_maggio_2027() -> None:
    """Ultima domenica di maggio 2027 = 30 maggio."""
    assert calcola_ultima_domenica_maggio(2027) == date(2027, 5, 30)


def test_ultima_domenica_maggio_e_domenica() -> None:
    """Cade sempre di domenica."""
    for anno in range(2024, 2034):
        assert calcola_ultima_domenica_maggio(anno).weekday() == 6


def test_ultima_domenica_maggio_e_a_maggio() -> None:
    """È sempre nel mese di maggio."""
    for anno in range(2024, 2034):
        d = calcola_ultima_domenica_maggio(anno)
        assert d.month == 5
        # Non più di 6 giorni prima del 31 maggio
        assert (date(anno, 5, 31) - d).days <= 6


# ======================================================================
# TEST — Prima domenica di giugno
# ======================================================================


def test_prima_domenica_giugno_2027() -> None:
    """Prima domenica di giugno 2027 = 6 giugno."""
    assert calcola_prima_domenica_giugno(2027) == date(2027, 6, 6)


def test_prima_domenica_giugno_e_domenica() -> None:
    """Cade sempre di domenica."""
    for anno in range(2024, 2034):
        assert calcola_prima_domenica_giugno(anno).weekday() == 6


def test_prima_domenica_giugno_e_a_giugno() -> None:
    """È sempre nel mese di giugno, entro i primi 7 giorni."""
    for anno in range(2024, 2034):
        d = calcola_prima_domenica_giugno(anno)
        assert d.month == 6
        assert d.day <= 7


# ======================================================================
# TEST — Festa del Voto
# ======================================================================


def test_festa_voto_2027_slitta() -> None:
    """Festa del Voto 2027 slitta a giugno (coincide con domenica Corpus Domini)."""
    # Nel 2027: Corpus Domini 27/05 (giovedì), domenica 30/05
    # Ultima domenica maggio = 30/05 → coincide → slitta
    assert calcola_festa_voto(2027) == date(2027, 6, 6)


def test_festa_voto_2026_non_slitta() -> None:
    """Festa del Voto 2026 resta a maggio."""
    # 2026: Corpus Domini 04/06 (giovedì), domenica 07/06
    # Ultima domenica maggio = 31/05 → non coincide → non slitta
    assert calcola_festa_voto(2026) == date(2026, 5, 31)


def test_festa_voto_e_sempre_domenica() -> None:
    """Cade sempre di domenica (sia che slitti sia che no)."""
    for anno in range(2024, 2034):
        assert calcola_festa_voto(anno).weekday() == 6


def test_festa_voto_a_maggio_o_giugno() -> None:
    """Cade in maggio (non slitta) o giugno (slitta)."""
    for anno in range(2024, 2034):
        d = calcola_festa_voto(anno)
        assert d.month in (5, 6)


def test_festa_voto_logica_slittamento() -> None:
    """Verifica che la logica di slittamento sia coerente per tutti gli anni."""
    for anno in range(2024, 2034):
        ultima = calcola_ultima_domenica_maggio(anno)
        corpus = calcola_corpus_domini(anno)
        domenica_corpus = corpus + timedelta(days=3)
        voto = calcola_festa_voto(anno)

        if ultima == domenica_corpus:
            # Deve slittare
            assert voto == calcola_prima_domenica_giugno(anno)
        else:
            # Non deve slittare
            assert voto == ultima


# ======================================================================
# TEST — calcola_tutte_date_mobili
# ======================================================================


def test_tutte_date_mobili_contiene_tutte_le_chiavi() -> None:
    """Il dizionario contiene tutte le chiavi attese."""
    date_mobili = calcola_tutte_date_mobili(2027)

    chiavi_attese = {
        # Singole
        "pasqua",
        "mercoledi_ceneri",
        "domenica_palme",
        "giovedi_santo",
        "venerdi_santo",
        "sabato_santo",
        "lunedi_angelo",
        "ascensione",
        "pentecoste",
        "trinita",
        "corpus_domini",
        "festa_voto",
        # Liste
        "domeniche_quaresima",
        "domeniche_avvento",
        "nove_mercoledi",
    }
    assert set(date_mobili.keys()) == chiavi_attese


def test_tutte_date_mobili_2027_pasqua() -> None:
    """Pasqua 2027 = 28 marzo."""
    assert calcola_tutte_date_mobili(2027)["pasqua"] == date(2027, 3, 28)


def test_tutte_date_mobili_2027_corpus_domini() -> None:
    """Corpus Domini 2027 = 27 maggio."""
    assert calcola_tutte_date_mobili(2027)["corpus_domini"] == date(2027, 5, 27)


def test_tutte_date_mobili_2027_festa_voto() -> None:
    """Festa del Voto 2027 = 6 giugno (slitta)."""
    assert calcola_tutte_date_mobili(2027)["festa_voto"] == date(2027, 6, 6)


def test_tutte_date_mobili_liste_hanno_giusta_lunghezza() -> None:
    """Le liste hanno la lunghezza attesa."""
    date_mobili = calcola_tutte_date_mobili(2027)

    quaresima = date_mobili["domeniche_quaresima"]
    avvento = date_mobili["domeniche_avvento"]
    nove = date_mobili["nove_mercoledi"]

    assert isinstance(quaresima, list)
    assert isinstance(avvento, list)
    assert isinstance(nove, list)

    assert len(quaresima) == 5
    assert len(avvento) == 4
    assert len(nove) == 9


def test_tutte_date_mobili_tipi_corretti() -> None:
    """Le singole sono date, le liste sono liste di date."""
    date_mobili = calcola_tutte_date_mobili(2027)

    # Singole
    for chiave in [
        "pasqua",
        "mercoledi_ceneri",
        "domenica_palme",
        "giovedi_santo",
        "venerdi_santo",
        "sabato_santo",
        "lunedi_angelo",
        "ascensione",
        "pentecoste",
        "trinita",
        "corpus_domini",
        "festa_voto",
    ]:
        assert isinstance(date_mobili[chiave], date), f"{chiave} non è una date"

    # Liste
    for chiave in ["domeniche_quaresima", "domeniche_avvento", "nove_mercoledi"]:
        valore = date_mobili[chiave]
        assert isinstance(valore, list), f"{chiave} non è una lista"
        for d in valore:
            assert isinstance(d, date), f"{chiave} contiene un elemento non-date"


def test_tutte_date_mobili_tutte_le_date_sono_dell_anno() -> None:
    """Tutte le date mobili sono nell'anno (o al massimo a fine anno)."""
    for anno in range(2024, 2034):
        date_mobili = calcola_tutte_date_mobili(anno)
        for chiave, valore in date_mobili.items():
            if isinstance(valore, list):
                for d in valore:
                    assert d.year == anno, f"{chiave} contiene data di anno diverso"
            else:
                assert valore.year == anno, f"{chiave} è di anno diverso"


def test_tutte_date_mobili_ordine_cronologico() -> None:
    """Le liste sono in ordine cronologico crescente."""
    for anno in range(2024, 2034):
        date_mobili = calcola_tutte_date_mobili(anno)
        for chiave in ["domeniche_quaresima", "domeniche_avvento", "nove_mercoledi"]:
            valore = date_mobili[chiave]
            assert isinstance(valore, list)
            for i in range(len(valore) - 1):
                assert valore[i] < valore[i + 1], f"{chiave} non è ordinata"


def test_tutte_date_mobili_pasqua_e_sempre_domenica() -> None:
    """La Pasqua è sempre di domenica."""
    for anno in range(2024, 2034):
        assert calcola_tutte_date_mobili(anno)["pasqua"].weekday() == 6  # type: ignore[union-attr]
