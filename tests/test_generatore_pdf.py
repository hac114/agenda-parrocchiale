"""Test per il modulo generatore_pdf."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import cast

import pytest
from jinja2 import Environment

from dataclass_config import Config, Festa, Intenzione, Periodo
from generatore_agenda import GiornoAgenda, genera_agenda
from generatore_pdf import (
    assembla_html,
    configura_jinja,
    estrai_body,
    genera_pdf,
    genera_pdf_da_profilo,
    leggi_css,
    renderizza_copertina,
    renderizza_giorno,
    renderizza_registro_intenzioni,
)

# ======================================================================
# FIXTURE
# ======================================================================


@pytest.fixture
def config_minima() -> Config:
    """Config minima per test."""
    return Config(
        nome_parrocchia="Test Parrocchia",
        citta="Roma",
        anno=2027,
        festivi_fissi=[
            Festa(nome="Natale", mese=12, giorno=25),
        ],
        periodi=[
            Periodo(
                dal=date(2027, 1, 1),
                al=date(2027, 12, 31),
                orari_feriali=["7:00", "18:00"],
                orari_festivi=["8:30", "11:30", "18:00"],
            ),
        ],
    )


@pytest.fixture
def env_jinja() -> Environment:
    """Environment Jinja2 configurato."""
    return cast(Environment, configura_jinja())


# ======================================================================
# TEST — configura_jinja
# ======================================================================


def test_configura_jinja_restituisce_environment() -> None:
    """configura_jinja restituisce un Environment valido."""
    env = configura_jinja()
    assert isinstance(env, Environment)


def test_configura_jinja_carica_template() -> None:
    """L'Environment può caricare i template esistenti."""
    env = configura_jinja()
    assert env.get_template("copertina.html") is not None
    assert env.get_template("agenda.html") is not None
    assert env.get_template("registro_intenzioni.html") is not None


# ======================================================================
# TEST — renderizza_copertina
# ======================================================================


def test_renderizza_copertina_contiene_dati(config_minima: Config, env_jinja: Environment) -> None:
    """La copertina contiene nome, città, anno."""
    html = renderizza_copertina(config_minima, env_jinja)
    assert "Test Parrocchia" in html
    assert "Roma" in html
    assert "2027" in html


def test_renderizza_copertina_e_html(config_minima: Config, env_jinja: Environment) -> None:
    """La copertina è HTML valido."""
    html = renderizza_copertina(config_minima, env_jinja)
    assert "<html" in html
    assert "<body>" in html
    assert "pagina-copertina" in html


# ======================================================================
# TEST — renderizza_giorno
# ======================================================================


def test_renderizza_giorno_contiene_data(config_minima: Config, env_jinja: Environment) -> None:
    """Il giorno contiene la data in italiano."""
    giorno = GiornoAgenda(
        data=date(2027, 12, 25),
        tipo="festivo",
        nome="Natale",
        orari=["8:30", "11:30", "18:00"],
    )
    html = renderizza_giorno(giorno, config_minima, env_jinja)
    assert "25 dicembre 2027" in html
    assert "Sabato" in html
    assert "Natale" in html


def test_renderizza_giorno_contiene_orari(config_minima: Config, env_jinja: Environment) -> None:
    """Il giorno contiene gli orari delle Messe."""
    giorno = GiornoAgenda(
        data=date(2027, 6, 15),
        tipo="feriale",
        orari=["7:00", "10:00", "18:00"],
    )
    html = renderizza_giorno(giorno, config_minima, env_jinja)
    assert "7:00" in html
    assert "10:00" in html
    assert "18:00" in html


def test_renderizza_giorno_senza_festivita(config_minima: Config, env_jinja: Environment) -> None:
    """Un giorno senza festività non mostra la sezione festività."""
    giorno = GiornoAgenda(
        data=date(2027, 6, 15),
        tipo="feriale",
        nome=None,
        orari=["7:00"],
    )
    html = renderizza_giorno(giorno, config_minima, env_jinja)
    assert 'class="festivita"' not in html


def test_renderizza_giorno_con_intenzioni(config_minima: Config, env_jinja: Environment) -> None:
    """Il giorno con intenzioni mostra la sezione."""
    giorno = GiornoAgenda(
        data=date(2027, 6, 15),
        tipo="feriale",
        orari=["7:00"],
        intenzioni=[
            Intenzione(numero=1, data_consegna=date(2027, 6, 10), testo="Per la pace"),
        ],
    )
    html = renderizza_giorno(giorno, config_minima, env_jinja)
    assert "Per la pace" in html


# ======================================================================
# TEST — renderizza_registro_intenzioni
# ======================================================================


def test_renderizza_registro_vuoto(config_minima: Config, env_jinja: Environment) -> None:
    """Il registro vuoto mostra il messaggio."""
    html = renderizza_registro_intenzioni(config_minima, env_jinja)
    assert "Nessuna intenzione registrata" in html


def test_renderizza_registro_con_intenzioni(env_jinja: Environment) -> None:
    """Il registro con intenzioni mostra la tabella."""
    config = Config(
        nome_parrocchia="Test",
        citta="Roma",
        anno=2027,
        intenzioni=[
            Intenzione(
                numero=1,
                data_consegna=date(2027, 1, 15),
                testo="Per la pace",
                data_applicazione=date(2027, 1, 20),
                note="Test",
            ),
        ],
    )
    html = renderizza_registro_intenzioni(config, env_jinja)
    assert "Per la pace" in html


# ======================================================================
# TEST — leggi_css
# ======================================================================


def test_leggi_css_restituisce_stringa() -> None:
    """leggi_css legge il file CSS."""
    css = leggi_css()
    assert isinstance(css, str)
    assert len(css) > 100
    assert "@page" in css


# ======================================================================
# TEST — estrai_body
# ======================================================================


def test_estrai_body_base() -> None:
    """estrai_body estrae il contenuto del body."""
    html = "<html><body>Contenuto</body></html>"
    assert estrai_body(html) == "Contenuto"


def test_estrai_body_senza_body() -> None:
    """estrai_body restituisce l'HTML se manca body."""
    html = "<html>Non ha body</html>"
    assert estrai_body(html) == html


# ======================================================================
# TEST — assembla_html
# ======================================================================


def test_assembla_html_produce_html_completo(config_minima: Config, env_jinja: Environment) -> None:
    """assembla_html produce un HTML completo."""
    calendario = genera_agenda(config_minima)
    html = assembla_html(config_minima, calendario, env_jinja)

    assert "<!DOCTYPE html>" in html
    assert "<html" in html
    assert "<style>" in html
    assert "Test Parrocchia" in html
    assert "Registro Intenzioni" in html


def test_assembla_html_contiene_tutti_i_giorni(
    config_minima: Config, env_jinja: Environment
) -> None:
    """L'HTML contiene una pagina per ogni giorno."""
    calendario = genera_agenda(config_minima)
    html = assembla_html(config_minima, calendario, env_jinja)

    assert html.count('class="pagina-giorno"') == len(calendario.giorni)


# ======================================================================
# TEST — genera_pdf
# ======================================================================


def test_genera_pdf_crea_file(config_minima: Config, tmp_path: Path) -> None:
    """genera_pdf crea un file PDF."""
    calendario = genera_agenda(config_minima)
    percorso_output = tmp_path / "test_agenda.pdf"

    risultato = genera_pdf(config_minima, calendario, percorso_output=percorso_output)

    assert risultato == percorso_output
    assert percorso_output.exists()
    assert percorso_output.stat().st_size > 1000


def test_genera_pdf_file_valido(config_minima: Config, tmp_path: Path) -> None:
    """Il PDF generato inizia con la firma %PDF."""
    calendario = genera_agenda(config_minima)
    percorso_output = tmp_path / "test_agenda.pdf"

    genera_pdf(config_minima, calendario, percorso_output=percorso_output)

    with open(percorso_output, "rb") as f:
        intestazione = f.read(4)
    assert intestazione == b"%PDF"


def test_genera_pdf_da_profilo_crea_file() -> None:
    """genera_pdf_da_profilo crea un PDF per il profilo reale."""
    percorso = genera_pdf_da_profilo("san_pietro_in_silki")

    assert percorso.exists()
    assert percorso.suffix == ".pdf"
    assert percorso.stat().st_size > 10_000
