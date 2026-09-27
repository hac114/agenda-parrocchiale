"""Test per il modulo generatore_agenda."""

from __future__ import annotations

from datetime import date

import pytest

from calcolo_liturgico import calcola_tutte_date_mobili
from config import carica_config
from dataclass_config import (
    Config,
    Festa,
    Intenzione,
    Matrimonio,
    Periodo,
    Ricorrenza,
)
from generatore_agenda import (
    applica_divieti_pomeridiani,
    applica_eccezioni_orari,
    determina_tipo_giorno,
    festivita_del_giorno,
    festivo_fisso,
    intenzioni_del_giorno,
    matrimoni_del_giorno,
    note_del_giorno,
    orari_per_giorno,
    trova_periodo,
)

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
# TEST — festivo_fisso
# ======================================================================


def test_festivo_fisso_trovato(config_minima: Config) -> None:
    """Trova il nome del festivo."""
    assert festivo_fisso(date(2027, 12, 25), config_minima) == "Natale"
    assert festivo_fisso(date(2027, 1, 6), config_minima) == "Epifania"


def test_festivo_fisso_non_trovato(config_minima: Config) -> None:
    """Ritorna None se non è un festivo."""
    assert festivo_fisso(date(2027, 1, 2), config_minima) is None
    assert festivo_fisso(date(2027, 6, 15), config_minima) is None


# ======================================================================
# TEST — determina_tipo_giorno
# ======================================================================


def test_tipo_giorno_festivo(config_minima: Config) -> None:
    """Un festivo fisso è tipo='festivo' con nome."""
    tipo, nome = determina_tipo_giorno(date(2027, 12, 25), config_minima)
    assert tipo == "festivo"
    assert nome == "Natale"


def test_tipo_giorno_domenica(config_minima: Config) -> None:
    """Una domenica non festiva è tipo='domenica' senza nome."""
    # 3 gennaio 2027 = domenica, non è un festivo fisso
    tipo, nome = determina_tipo_giorno(date(2027, 1, 3), config_minima)
    assert tipo == "domenica"
    assert nome is None


def test_tipo_giorno_feriale(config_minima: Config) -> None:
    """Un giorno feriale è tipo='feriale' senza nome."""
    # 4 gennaio 2027 = lunedì
    tipo, nome = determina_tipo_giorno(date(2027, 1, 4), config_minima)
    assert tipo == "feriale"
    assert nome is None


def test_tipo_giorno_festivo_che_cade_di_domenica(config_minima: Config) -> None:
    """Un festivo che cade di domenica è classificato 'festivo' (non 'domenica')."""
    # Natale 2022 cade di domenica → deve essere "festivo"
    assert date(2022, 12, 25).weekday() == 6  # sanity check

    tipo, nome = determina_tipo_giorno(date(2022, 12, 25), config_minima)
    assert tipo == "festivo"
    assert nome == "Natale"


def test_tipo_giorno_domenica_di_quaresima(config_minima: Config) -> None:
    """Una domenica di Quaresima è tipo='domenica' (non festivo)."""
    # 14 febbraio 2027 = I domenica di Quaresima (domenica, non festivo fisso)
    tipo, nome = determina_tipo_giorno(date(2027, 2, 14), config_minima)
    assert tipo == "domenica"
    assert nome is None


# ======================================================================
# TEST INTEGRATIVI (con Config reale)
# ======================================================================


def test_config_reale_natale() -> None:
    """Con la Config reale, Natale 2027 è festivo."""
    config = carica_config("san_pietro_in_silki")
    tipo, nome = determina_tipo_giorno(date(2027, 12, 25), config)
    assert tipo == "festivo"
    assert nome == "Natale"


def test_config_reale_san_salvatore_e_feriale() -> None:
    """San Salvatore (17 marzo) è feriale (è ricorrenza propria, non festivo fisso)."""
    config = carica_config("san_pietro_in_silki")
    # 17 marzo 2027 = mercoledì
    tipo, nome = determina_tipo_giorno(date(2027, 3, 17), config)
    assert tipo == "feriale"
    assert nome is None


# ======================================================================
# FIXTURE — Config con periodi
# ======================================================================


@pytest.fixture
def config_con_periodi() -> Config:
    """Config con 2 periodi per testare trova_periodo."""
    return Config(
        nome_parrocchia="Test",
        citta="Roma",
        periodi=[
            Periodo(
                dal=date(2027, 1, 1),
                al=date(2027, 3, 31),
                orari_feriali=["7:00", "10:00"],
                orari_festivi=["8:30", "11:30"],
            ),
            Periodo(
                dal=date(2027, 4, 1),
                al=date(2027, 12, 31),
                orari_feriali=["7:30", "11:00"],
                orari_festivi=["9:00", "12:00"],
            ),
        ],
    )


# ======================================================================
# TEST — trova_periodo
# ======================================================================


def test_trova_periodo_inverno(config_con_periodi: Config) -> None:
    """Trova il primo periodo per una data di gennaio."""
    p = trova_periodo(date(2027, 2, 15), config_con_periodi)
    assert p is not None
    assert p.dal == date(2027, 1, 1)
    assert p.al == date(2027, 3, 31)


def test_trova_periodo_estate(config_con_periodi: Config) -> None:
    """Trova il secondo periodo per una data di luglio."""
    p = trova_periodo(date(2027, 7, 15), config_con_periodi)
    assert p is not None
    assert p.dal == date(2027, 4, 1)
    assert p.al == date(2027, 12, 31)


def test_trova_periodo_confine(config_con_periodi: Config) -> None:
    """Le date di confine sono incluse."""
    p1 = trova_periodo(date(2027, 3, 31), config_con_periodi)
    assert p1 is not None
    assert p1.dal == date(2027, 1, 1)

    p2 = trova_periodo(date(2027, 4, 1), config_con_periodi)
    assert p2 is not None
    assert p2.dal == date(2027, 4, 1)


def test_trova_periodo_nessuno(config_minima: Config) -> None:
    """Nessun periodo trovato → None."""
    # config_minima non ha periodi
    p = trova_periodo(date(2027, 6, 15), config_minima)
    assert p is None


def test_trova_periodo_config_reale_2027() -> None:
    """Con la Config reale, trova il periodo giusto per diverse date."""
    config = carica_config("san_pietro_in_silki")

    # Ottobre 2027 = inverno
    p = trova_periodo(date(2027, 10, 15), config)
    assert p is not None
    assert p.dal == date(2027, 10, 1)

    # Maggio 2027 = mese mariano
    p = trova_periodo(date(2027, 5, 15), config)
    assert p is not None
    assert p.dal == date(2027, 5, 1)
    assert p.orari_feriali == ["6:15", "7:00", "8:30", "10:00", "11:30", "17:30", "18:30"]

    # Luglio 2027 = estate
    p = trova_periodo(date(2027, 7, 15), config)
    assert p is not None
    assert p.dal == date(2027, 7, 1)


# ======================================================================
# TEST — orari_per_giorno
# ======================================================================


def test_orari_per_giorno_feriale(config_con_periodi: Config) -> None:
    """Un giorno feriale usa gli orari feriali del periodo."""
    orari = orari_per_giorno(date(2027, 2, 15), "feriale", config_con_periodi)
    assert orari == ["7:00", "10:00"]


def test_orari_per_giorno_domenica(config_con_periodi: Config) -> None:
    """Una domenica usa gli orari festivi del periodo."""
    orari = orari_per_giorno(date(2027, 2, 15), "domenica", config_con_periodi)
    assert orari == ["8:30", "11:30"]


def test_orari_per_giorno_festivo(config_con_periodi: Config) -> None:
    """Un festivo usa gli orari festivi del periodo."""
    orari = orari_per_giorno(date(2027, 2, 15), "festivo", config_con_periodi)
    assert orari == ["8:30", "11:30"]


def test_orari_per_giorno_solennita(config_con_periodi: Config) -> None:
    """Una solennità usa gli orari festivi del periodo."""
    orari = orari_per_giorno(date(2027, 2, 15), "solennita", config_con_periodi)
    assert orari == ["8:30", "11:30"]


def test_orari_per_giorno_secondo_periodo(config_con_periodi: Config) -> None:
    """Se la data è nel secondo periodo, usa i suoi orari."""
    orari = orari_per_giorno(date(2027, 7, 15), "feriale", config_con_periodi)
    assert orari == ["7:30", "11:00"]


def test_orari_per_giorno_nessun_periodo(config_minima: Config) -> None:
    """Nessun periodo trovato → lista vuota."""
    # config_minima non ha periodi
    orari = orari_per_giorno(date(2027, 6, 15), "feriale", config_minima)
    assert orari == []


def test_orari_per_giorno_non_modifica_originale(config_con_periodi: Config) -> None:
    """La lista restituita è una copia, non l'originale."""
    orari = orari_per_giorno(date(2027, 2, 15), "feriale", config_con_periodi)
    orari.append("99:99")  # modifica la copia

    # Gli orari originali del periodo non sono cambiati
    assert config_con_periodi.periodi[0].orari_feriali == ["7:00", "10:00"]


# ======================================================================
# TEST INTEGRATIVI (con Config reale)
# ======================================================================


def test_orari_per_giorno_config_reale_inverno_feriale() -> None:
    """Inverno, feriale → 3 orari."""
    config = carica_config("san_pietro_in_silki")
    orari = orari_per_giorno(date(2027, 10, 15), "feriale", config)
    assert orari == ["7:00", "10:00", "18:00"]


def test_orari_per_giorno_config_reale_inverno_domenica() -> None:
    """Inverno, domenica → 4 orari."""
    config = carica_config("san_pietro_in_silki")
    orari = orari_per_giorno(date(2027, 10, 17), "domenica", config)
    assert orari == ["8:30", "10:00", "11:30", "18:00"]


def test_orari_per_giorno_config_reale_maggio() -> None:
    """Maggio → 7 orari (mese mariano)."""
    config = carica_config("san_pietro_in_silki")
    orari = orari_per_giorno(date(2027, 5, 15), "feriale", config)
    assert len(orari) == 7
    assert orari[0] == "6:15"
    assert orari[-1] == "18:30"


def test_orari_per_giorno_config_reale_estate_festivo() -> None:
    """Luglio, festivo → orari con 21:00."""
    config = carica_config("san_pietro_in_silki")
    orari = orari_per_giorno(date(2027, 7, 15), "festivo", config)
    assert "21:00" in orari


# ======================================================================
# FIXTURE — Config con eccezioni
# ======================================================================


@pytest.fixture
def config_con_eccezioni() -> Config:
    """Config con due eccezioni: Bernardino (salta se dom) + Stefano (orari ridotti)."""
    return Config(
        nome_parrocchia="Test",
        citta="Roma",
        eccezioni_festivi=[
            Festa(
                nome="Beato Bernardino",
                mese=9,
                giorno=28,
                salta_se_domenica=True,
            ),
            Festa(
                nome="Santo Stefano",
                mese=12,
                giorno=26,
                orari_ridotti=["10:00", "18:00"],
            ),
        ],
    )


# ======================================================================
# TEST — applica_eccezioni_orari
# ======================================================================


def test_eccezioni_orari_ridotti(config_con_eccezioni: Config) -> None:
    """Santo Stefano → orari ridotti."""
    orari = ["8:30", "10:00", "11:30", "18:00"]
    risultato = applica_eccezioni_orari(date(2027, 12, 26), orari, config_con_eccezioni)
    assert risultato == ["10:00", "18:00"]


def test_eccezioni_salta_se_domenica_ma_non_domenica(config_con_eccezioni: Config) -> None:
    """Bernardino in giorno feriale → nessuna modifica."""
    orari = ["8:30", "10:00", "11:30", "18:00"]
    # 28 settembre 2027 = martedì
    risultato = applica_eccezioni_orari(date(2027, 9, 28), orari, config_con_eccezioni)
    assert risultato == orari


def test_eccezioni_salta_se_domenica(config_con_eccezioni: Config) -> None:
    """Bernardino di domenica → lista vuota."""
    orari = ["8:30", "10:00", "11:30", "18:00"]
    # 28 settembre 2031 = domenica
    risultato = applica_eccezioni_orari(date(2031, 9, 28), orari, config_con_eccezioni)
    assert risultato == []


def test_eccezioni_data_non_coinvolta(config_con_eccezioni: Config) -> None:
    """Data senza eccezioni → orari invariati."""
    orari = ["8:30", "10:00", "11:30", "18:00"]
    risultato = applica_eccezioni_orari(date(2027, 12, 25), orari, config_con_eccezioni)
    assert risultato == orari


def test_eccezioni_lista_vuota(config_minima: Config) -> None:
    """Config senza eccezioni → orari invariati."""
    orari = ["8:30", "10:00", "11:30", "18:00"]
    risultato = applica_eccezioni_orari(date(2027, 6, 15), orari, config_minima)
    assert risultato == orari


def test_eccezioni_restituisce_copia(config_con_eccezioni: Config) -> None:
    """La lista restituita è una copia, non l'originale."""
    orari_originali = ["8:30", "10:00", "11:30", "18:00"]
    risultato = applica_eccezioni_orari(date(2027, 12, 26), orari_originali, config_con_eccezioni)
    risultato.append("99:99")
    assert orari_originali == ["8:30", "10:00", "11:30", "18:00"]


# ======================================================================
# TEST INTEGRATIVI (con Config reale)
# ======================================================================


def test_eccezioni_config_reale_santo_stefano() -> None:
    """Santo Stefano 2027 ha orari ridotti (10:00, 18:00)."""
    config = carica_config("san_pietro_in_silki")
    orari = ["8:30", "10:00", "11:30", "18:00"]
    risultato = applica_eccezioni_orari(date(2027, 12, 26), orari, config)
    assert risultato == ["10:00", "18:00"]


def test_eccezioni_config_reale_bernardino_domenica() -> None:
    """Beato Bernardino che cade di domenica (2031) → lista vuota."""
    config = carica_config("san_pietro_in_silki")
    orari = ["8:30", "10:00", "11:30", "18:00"]
    risultato = applica_eccezioni_orari(date(2031, 9, 28), orari, config)
    assert risultato == []


def test_eccezioni_config_reale_bernardino_martedi() -> None:
    """Beato Bernardino che cade di martedì (2027) → orari invariati."""
    config = carica_config("san_pietro_in_silki")
    orari = ["8:30", "10:00", "11:30", "18:00"]
    risultato = applica_eccezioni_orari(date(2027, 9, 28), orari, config)
    assert risultato == orari


# ======================================================================
# TEST — applica_divieti_pomeridiani
# ======================================================================


def test_divieto_assunta() -> None:
    """Assunta (15 agosto) rimuove orari pomeridiani."""
    config = carica_config("san_pietro_in_silki")
    orari = ["8:30", "10:00", "11:30", "18:00"]
    risultato = applica_divieti_pomeridiani(date(2027, 8, 15), orari, config)
    assert risultato == ["8:30", "10:00", "11:30"]


def test_divieto_san_nicola() -> None:
    """San Nicola (6 dicembre) rimuove orari pomeridiani."""
    config = carica_config("san_pietro_in_silki")
    orari = ["8:30", "10:00", "11:30", "18:00"]
    risultato = applica_divieti_pomeridiani(date(2027, 12, 6), orari, config)
    assert risultato == ["8:30", "10:00", "11:30"]


def test_divieto_corpus_domini_2027() -> None:
    """Corpus Domini 2027 (27 maggio) rimuove orari pomeridiani."""
    config = carica_config("san_pietro_in_silki")
    orari = ["8:30", "10:00", "11:30", "18:00"]
    risultato = applica_divieti_pomeridiani(date(2027, 5, 27), orari, config)
    assert risultato == ["8:30", "10:00", "11:30"]


def test_divieto_corpus_domini_2028() -> None:
    """Corpus Domini 2028 (15 giugno) rimuove orari pomeridiani."""
    config = carica_config("san_pietro_in_silki")
    orari = ["8:30", "10:00", "11:30", "19:00"]
    risultato = applica_divieti_pomeridiani(date(2028, 6, 15), orari, config)
    assert risultato == ["8:30", "10:00", "11:30"]


def test_no_divieto_natale() -> None:
    """Natale non ha divieto pomeridiano."""
    config = carica_config("san_pietro_in_silki")
    orari = ["8:30", "10:00", "11:30", "18:00"]
    risultato = applica_divieti_pomeridiani(date(2027, 12, 25), orari, config)
    assert risultato == orari


def test_no_divieto_giorno_feriale() -> None:
    """Un giorno feriale normale non ha divieto."""
    config = carica_config("san_pietro_in_silki")
    orari = ["7:00", "10:00", "18:00"]
    risultato = applica_divieti_pomeridiani(date(2027, 10, 15), orari, config)
    assert risultato == orari


def test_divieto_orario_mattina_invariato() -> None:
    """Un orario mattutino (7:00) non viene toccato."""
    config = carica_config("san_pietro_in_silki")
    orari = ["7:00", "10:00", "13:00"]
    risultato = applica_divieti_pomeridiani(date(2027, 8, 15), orari, config)
    assert risultato == ["7:00", "10:00", "13:00"]  # 13:00 < 14:00 → mattina


def test_divieto_13_ora_e_mattina() -> None:
    """L'orario 13:00 è considerato mattina (< 14:00)."""
    config = carica_config("san_pietro_in_silki")
    orari = ["13:00", "14:00", "18:00"]
    risultato = applica_divieti_pomeridiani(date(2027, 8, 15), orari, config)
    assert risultato == ["13:00"]


def test_divieto_restituisce_copia() -> None:
    """La lista restituita è una copia, non l'originale."""
    config = carica_config("san_pietro_in_silki")
    orari_originali = ["8:30", "10:00", "18:00"]
    risultato = applica_divieti_pomeridiani(date(2027, 8, 15), orari_originali, config)
    risultato.append("99:99")
    assert orari_originali == ["8:30", "10:00", "18:00"]


# ======================================================================
# FIXTURE — Config con ricorrenze proprie
# ======================================================================


@pytest.fixture
def config_con_ricorrenze() -> Config:
    """Config con 2 ricorrenze proprie."""
    return Config(
        nome_parrocchia="Test",
        citta="Roma",
        ricorrenze_proprie=[
            Ricorrenza(
                nome="Triduo di San Salvatore",
                data_inizio=date(2027, 3, 14),
                data_fine=date(2027, 3, 16),
                tipo="triduo",
            ),
            Ricorrenza(
                nome="San Salvatore da Horta",
                data_inizio=date(2027, 3, 17),
                data_fine=date(2027, 3, 18),
            ),
        ],
    )


# ======================================================================
# TEST — festivita_del_giorno
# ======================================================================


def test_festivita_ricorrenza_singola(config_con_ricorrenze: Config) -> None:
    """Una ricorrenza di un giorno è riconosciuta."""
    info = festivita_del_giorno(date(2027, 3, 17), config_con_ricorrenze, {})
    assert info["nome"] == "San Salvatore da Horta"
    assert info["particolare"] is True
    assert info["tipo_override"] is None


def test_festivita_ricorrenza_multigiorno(config_con_ricorrenze: Config) -> None:
    """Una ricorrenza multi-giorno copre tutti i giorni."""
    for giorno in [14, 15, 16]:
        info = festivita_del_giorno(date(2027, 3, giorno), config_con_ricorrenze, {})
        assert info["nome"] == "Triduo di San Salvatore"
        assert info["particolare"] is True


def test_festivita_celebrazione_mobile() -> None:
    """Una celebrazione mobile (Palme) è riconosciuta."""
    config = carica_config("san_pietro_in_silki")
    date_mobili = calcola_tutte_date_mobili(2027)

    # Palme 2027 = 21 marzo
    info = festivita_del_giorno(date(2027, 3, 21), config, date_mobili)
    assert info["nome"] == "Domenica delle Palme"
    assert info["particolare"] is False


def test_festivita_giorno_qualunque(config_minima: Config) -> None:
    """Un giorno qualunque non ha nome né particolare."""
    info = festivita_del_giorno(date(2027, 6, 15), config_minima, {})
    assert info["nome"] is None
    assert info["particolare"] is False


def test_festivita_priorita_ricorrenza(config_con_ricorrenze: Config) -> None:
    """Se una data è sia ricorrenza sia mobile, vince la ricorrenza."""
    # Configura date_mobili con una data fittizia che coincide con la ricorrenza
    date_mobili = {"pasqua": date(2027, 3, 17)}  # coincide con San Salvatore

    info = festivita_del_giorno(date(2027, 3, 17), config_con_ricorrenze, date_mobili)
    # La ricorrenza ha priorità
    assert info["nome"] == "San Salvatore da Horta"
    assert info["particolare"] is True


def test_festivita_mobili_config_reale_pasqua() -> None:
    """Pasqua 2027 (28 marzo) è riconosciuta come celebrazione mobile."""
    config = carica_config("san_pietro_in_silki")
    date_mobili = calcola_tutte_date_mobili(2027)

    info = festivita_del_giorno(date(2027, 3, 28), config, date_mobili)
    assert info["nome"] == "Pasqua"
    assert info["particolare"] is False


def test_festivita_mobili_config_reale_corpus_domini() -> None:
    """Corpus Domini 2027 (27 maggio) è riconosciuto."""
    config = carica_config("san_pietro_in_silki")
    date_mobili = calcola_tutte_date_mobili(2027)

    info = festivita_del_giorno(date(2027, 5, 27), config, date_mobili)
    assert info["nome"] == "Corpus Domini"
    assert info["particolare"] is False


def test_festivita_mobili_config_reale_festa_voto() -> None:
    """Festa del Voto 2027 (6 giugno, slittata) è riconosciuta."""
    config = carica_config("san_pietro_in_silki")
    date_mobili = calcola_tutte_date_mobili(2027)

    info = festivita_del_giorno(date(2027, 6, 6), config, date_mobili)
    assert info["nome"] == "Festa del Voto"


def test_festivita_config_reale_san_salvatore() -> None:
    """San Salvatore 2027 (17 marzo) è ricorrenza propria."""
    config = carica_config("san_pietro_in_silki")
    date_mobili = calcola_tutte_date_mobili(2027)

    info = festivita_del_giorno(date(2027, 3, 17), config, date_mobili)
    assert info["nome"] == "San Salvatore da Horta"
    assert info["particolare"] is True


def test_festivita_config_reale_triduo_san_salvatore() -> None:
    """Triduo San Salvatore 2027 (14-16 marzo)."""
    config = carica_config("san_pietro_in_silki")
    date_mobili = calcola_tutte_date_mobili(2027)

    for giorno in [14, 15, 16]:
        info = festivita_del_giorno(date(2027, 3, giorno), config, date_mobili)
        assert info["nome"] == "Triduo di San Salvatore"
        assert info["particolare"] is True


# ======================================================================
# FIXTURE — Config con dati compilati
# ======================================================================


@pytest.fixture
def config_con_dati() -> Config:
    """Config con intenzioni, matrimoni e note."""
    return Config(
        nome_parrocchia="Test",
        citta="Roma",
        intenzioni=[
            Intenzione(
                numero=1,
                data_consegna=date(2027, 1, 15),
                testo="Per la pace",
                data_applicazione=date(2027, 1, 20),
            ),
            Intenzione(
                numero=2,
                data_consegna=date(2027, 2, 1),
                testo="Per i defunti",
                data_applicazione=date(2027, 1, 20),  # stessa data
            ),
            Intenzione(
                numero=3,
                data_consegna=date(2027, 3, 1),
                testo="Per la salute",
                data_applicazione=date(2027, 3, 15),
            ),
        ],
        matrimoni_prenotati=[
            Matrimonio(
                data=date(2027, 6, 12),
                ora="15:30",
                nome_sposi="Maria Rossi e Luca Bianchi",
            ),
            Matrimonio(
                data=date(2027, 7, 10),
                ora="10:00",
                nome_sposi="Anna Verdi e Marco Neri",
            ),
        ],
        note_annuali=[
            {"dal": date(2027, 3, 14), "al": date(2027, 3, 16), "nota": "Triduo"},
            {"dal": date(2027, 5, 1), "al": date(2027, 5, 31), "nota": "Mese mariano"},
            {"dal": date(2027, 5, 30), "al": date(2027, 5, 30), "nota": "Corpus Domini"},
        ],
    )


# ======================================================================
# TEST — intenzioni_del_giorno
# ======================================================================


def test_intenzioni_del_giorno_una(config_con_dati: Config) -> None:
    """Trova 1 intenzione applicata in una data."""
    intenzioni = intenzioni_del_giorno(date(2027, 3, 15), config_con_dati)
    assert len(intenzioni) == 1
    assert intenzioni[0].testo == "Per la salute"


def test_intenzioni_del_giorno_due_stessa_data(config_con_dati: Config) -> None:
    """Trova 2 intenzioni applicate nella stessa data."""
    intenzioni = intenzioni_del_giorno(date(2027, 1, 20), config_con_dati)
    assert len(intenzioni) == 2
    testi = {i.testo for i in intenzioni}
    assert testi == {"Per la pace", "Per i defunti"}


def test_intenzioni_del_giorno_nessuna(config_con_dati: Config) -> None:
    """Nessuna intenzione applicata in una data."""
    intenzioni = intenzioni_del_giorno(date(2027, 12, 25), config_con_dati)
    assert intenzioni == []


def test_intenzioni_del_giorno_ignora_senza_applicazione() -> None:
    """Intenzioni senza data_applicazione non vengono mai restituite."""
    config = Config(
        nome_parrocchia="Test",
        citta="Roma",
        intenzioni=[
            Intenzione(
                numero=1,
                data_consegna=date(2027, 1, 15),
                testo="Senza applicazione",
                data_applicazione=None,
            ),
        ],
    )
    assert intenzioni_del_giorno(date(2027, 1, 15), config) == []


# ======================================================================
# TEST — matrimoni_del_giorno
# ======================================================================


def test_matrimoni_del_giorno_uno(config_con_dati: Config) -> None:
    """Trova un matrimonio in una data."""
    matrimoni = matrimoni_del_giorno(date(2027, 6, 12), config_con_dati)
    assert len(matrimoni) == 1
    assert matrimoni[0].nome_sposi == "Maria Rossi e Luca Bianchi"


def test_matrimoni_del_giorno_nessuno(config_con_dati: Config) -> None:
    """Nessun matrimonio in una data."""
    matrimoni = matrimoni_del_giorno(date(2027, 12, 25), config_con_dati)
    assert matrimoni == []


# ======================================================================
# TEST — note_del_giorno
# ======================================================================


def test_note_del_giorno_inizio_intervallo(config_con_dati: Config) -> None:
    """Trova la nota all'inizio dell'intervallo."""
    note = note_del_giorno(date(2027, 3, 14), config_con_dati)
    assert len(note) == 1
    assert note[0]["nota"] == "Triduo"


def test_note_del_giorno_meta_intervallo(config_con_dati: Config) -> None:
    """Trova la nota a metà dell'intervallo."""
    note = note_del_giorno(date(2027, 3, 15), config_con_dati)
    assert len(note) == 1
    assert note[0]["nota"] == "Triduo"


def test_note_del_giorno_fine_intervallo(config_con_dati: Config) -> None:
    """Trova la nota alla fine dell'intervallo."""
    note = note_del_giorno(date(2027, 3, 16), config_con_dati)
    assert len(note) == 1


def test_note_del_giorno_fuori_intervallo(config_con_dati: Config) -> None:
    """Nessuna nota fuori dall'intervallo."""
    note = note_del_giorno(date(2027, 3, 17), config_con_dati)
    assert note == []


def test_note_del_giorno_multiple(config_con_dati: Config) -> None:
    """Una data può avere più note attive."""
    # 30 maggio 2027 ricade sia in "Mese mariano" sia in "Corpus Domini"
    note = note_del_giorno(date(2027, 5, 30), config_con_dati)
    assert len(note) == 2
    testi = {n["nota"] for n in note}
    assert testi == {"Mese mariano", "Corpus Domini"}
