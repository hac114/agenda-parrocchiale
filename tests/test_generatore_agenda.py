"""Test per il modulo generatore_agenda."""

from __future__ import annotations

from datetime import date

import pytest

from config import carica_config
from dataclass_config import Config, Festa, Periodo
from generatore_agenda import (
    applica_eccezioni_orari,
    determina_tipo_giorno,
    festivo_fisso,
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
