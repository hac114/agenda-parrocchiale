"""
Generatore del PDF dell'agenda completa.

Usa:
- Jinja2 per il rendering dei template HTML
- WeasyPrint per la conversione HTML → PDF

Output: un unico PDF A4 con:
1. Copertina
2. Pagine giorno (1 pagina = 1 giorno)
3. Registro intenzioni
4. Spazio matrimoni anno successivo

Uso tipico:
    from generatore_pdf import genera_pdf_da_profilo

    percorso = genera_pdf_da_profilo("san_pietro_in_silki")
    print(f"PDF generato: {percorso}")
"""

from __future__ import annotations

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from dataclass_config import Config
from generatore_agenda import CalendarioAgenda, GiornoAgenda
from util import formatta_data_italiana, nome_giorno_italiano

logger = logging.getLogger(__name__)

# ======================================================================
# COSTANTI
# ======================================================================

# Radice del progetto
ROOT_PROGETTO = Path(__file__).resolve().parent.parent
CARTELLA_TEMPLATES = ROOT_PROGETTO / "templates"
CARTELLA_OUTPUT = ROOT_PROGETTO / "output"

# ======================================================================
# CONFIGURAZIONE JINJA2
# ======================================================================


def configura_jinja() -> Environment:
    """Configura l'ambiente Jinja2 per il rendering dei template.

    Returns:
        Environment configurato con il FileSystemLoader puntato
        alla cartella templates/.
    """
    env: Environment = Environment(
        loader=FileSystemLoader(str(CARTELLA_TEMPLATES)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env


# ======================================================================
# RENDERING TEMPLATE
# ======================================================================


def renderizza_copertina(config: Config, env: Environment) -> str:
    """Renderizza il template della copertina.

    Args:
        config: Config con nome parrocchia, città, anno
        env: Environment Jinja2 configurato

    Returns:
        HTML della copertina.
    """
    template = env.get_template("copertina.html")
    return template.render(
        nome_parrocchia=config.nome_parrocchia,
        citta=config.citta,
        anno=config.anno,
    )


def renderizza_intenzioni_libere(config: Config, env: Environment) -> str:
    """Renderizza una singola pagina 'Intenzioni libere'.

    Args:
        config: Config con anno
        env: Environment Jinja2 configurato

    Returns:
        HTML della pagina intenzioni libere.
    """
    template = env.get_template("intenzioni_libere.html")
    return template.render(anno=config.anno)


def _prepara_righe_messe(orari: list[str], config: Config) -> list[dict]:
    """Prepara le righe della tabella messe con eventuali righe extra.

    Args:
        orari: lista di orari (es. ["7:00", "10:00", "18:00"])
        config: Config con il layout (righe_default + righe_extra)

    Returns:
        Lista di dict con "orario" e "righe_extra".
    """
    righe = []
    for orario in orari:
        righe_extra = config.layout.righe_extra.get(orario, config.layout.righe_default)
        righe.append(
            {
                "orario": orario,
                "righe_extra": righe_extra,
            }
        )
    return righe


def renderizza_giorno(
    giorno: GiornoAgenda,
    config: Config,
    env: Environment,
) -> str:
    """Renderizza il template di un giorno.

    Args:
        giorno: GiornoAgenda con data, tipo, nome, orari, ecc.
        config: Config (per eventuali dati aggiuntivi futuri)
        env: Environment Jinja2 configurato

    Returns:
        HTML del giorno.
    """
    template = env.get_template("agenda.html")
    righe_messe = _prepara_righe_messe(giorno.orari, config)
    return template.render(
        data_formattata=formatta_data_italiana(giorno.data),
        giorno_settimana=nome_giorno_italiano(giorno.data),
        nome_festivita=giorno.nome,
        nota_liturgica=giorno.nota_liturgica,
        righe_messe=righe_messe,
        matrimoni=giorno.matrimoni,
        note=giorno.note,
        anno=config.anno,
    )


def renderizza_registro_intenzioni(config: Config, env: Environment) -> str:
    """Renderizza il template del registro intenzioni.

    Args:
        config: Config con la lista delle intenzioni
        env: Environment Jinja2 configurato

    Returns:
        HTML del registro intenzioni.
    """
    template = env.get_template("registro_intenzioni.html")
    return template.render(
        intenzioni=config.intenzioni,
        nome_parrocchia=config.nome_parrocchia,
        anno=config.anno,
    )


# ======================================================================
# GENERAZIONE PDF
# ======================================================================


def leggi_css() -> str:
    """Legge il CSS da templates/style.css.

    Returns:
        Contenuto del file CSS.

    Raises:
        FileNotFoundError: se il file CSS non esiste.
    """
    percorso_css = CARTELLA_TEMPLATES / "style.css"
    if not percorso_css.exists():
        raise FileNotFoundError(f"File CSS non trovato: {percorso_css}")
    return percorso_css.read_text(encoding="utf-8")


def assembla_html(config: Config, calendario: CalendarioAgenda, env: Environment) -> str:
    """Assembla l'HTML completo dell'agenda.

    Ordine:
    1. Copertina
    2. Pagine giorno (una per giorno)
    3. Registro intenzioni

    Args:
        config: Config
        calendario: CalendarioAgenda con tutti i giorni
        env: Environment Jinja2

    Returns:
        HTML completo come stringa.
    """
    # CSS inline
    css = leggi_css()

    # Copertina
    html_copertina = renderizza_copertina(config, env)

    # Estrai il body della copertina (senza <head>)
    copertina_body = estrai_body(html_copertina)

    # 10 pagine "Intenzioni libere" (subito dopo la copertina)
    pagine_intenzioni_libere: list[str] = []
    for _ in range(10):
        html_il = renderizza_intenzioni_libere(config, env)
        pagine_intenzioni_libere.append(estrai_body(html_il))

    # Pagine giorno
    pagine_giorni: list[str] = []
    for giorno in calendario.giorni:
        html_giorno = renderizza_giorno(giorno, config, env)
        pagine_giorni.append(estrai_body(html_giorno))

    # Registro intenzioni
    html_registro = renderizza_registro_intenzioni(config, env)
    registro_body = estrai_body(html_registro)

    # Matrimoni futuri
    html_matrimoni = renderizza_matrimoni_annuali(config, env)
    matrimoni_body = estrai_body(html_matrimoni)

    # Assembla tutto in un unico documento
    html_completo = f"""<!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>Agenda {config.nome_parrocchia} {config.anno}</title>
        <style>
    {css}
        </style>
    </head>
    <body>
    {copertina_body}
    {"".join(pagine_intenzioni_libere)}
    {"".join(pagine_giorni)}
    {registro_body}
    {matrimoni_body}
    </body>
    </html>
    """
    return html_completo


def estrai_body(html: str) -> str:
    """Estrae il contenuto del <body> da un HTML completo.

    Args:
        html: HTML completo con <body>.

    Returns:
        Solo il contenuto del <body>.
    """
    inizio = html.find("<body>")
    fine = html.find("</body>")
    if inizio == -1 or fine == -1:
        return html
    return html[inizio + len("<body>") : fine]


def genera_pdf(
    config: Config,
    calendario: CalendarioAgenda,
    percorso_output: Path | None = None,
) -> Path:
    """Genera il PDF dell'agenda.

    Args:
        config: Config completa
        calendario: CalendarioAgenda con tutti i giorni
        percorso_output: percorso del PDF. Se None, usa
                         output/Agenda_<anno>.pdf

    Returns:
        Percorso del PDF generato.
    """
    from weasyprint import HTML  # import ritardato (richiede lib di sistema)

    # Percorso di default
    if percorso_output is None:
        CARTELLA_OUTPUT.mkdir(parents=True, exist_ok=True)
        percorso_output = CARTELLA_OUTPUT / f"Agenda_{config.anno}.pdf"

    # Configura Jinja2
    env = configura_jinja()

    # Assembla HTML
    logger.info("Assemblaggio HTML per l'anno %d...", config.anno)
    html = assembla_html(config, calendario, env)

    # Genera PDF
    logger.info("Generazione PDF in %s...", percorso_output)
    HTML(string=html, base_url=str(CARTELLA_TEMPLATES)).write_pdf(str(percorso_output))

    logger.info("PDF generato: %s", percorso_output)
    return percorso_output


def genera_pdf_da_profilo(profilo: str) -> Path:
    """Wrapper: carica il profilo, genera l'agenda e produce il PDF.

    Args:
        profilo: nome del profilo (es. "san_pietro_in_silki")

    Returns:
        Percorso del PDF generato.
    """
    from config import carica_config
    from generatore_agenda import genera_agenda

    config = carica_config(profilo)
    calendario = genera_agenda(config)
    return genera_pdf(config, calendario)


def renderizza_matrimoni_annuali(config: Config, env: Environment) -> str:
    """Renderizza le tabelle annuali dei matrimoni (un'area per anno).

    Per l'anno dell'agenda vengono sempre generate le righe (una per
    sabato valido, escluso maggio), anche se non ci sono matrimoni
    prenotati, in modo che i frati possano aggiungerli a mano sul
    cartaceo. Per gli anni successivi vengono generate tabelle solo
    se esistono matrimoni prenotati in quell'anno.

    Args:
        config: Config con anno e matrimoni_prenotati
        env: Environment Jinja2 configurato

    Returns:
        HTML della sezione matrimoni annuali.
    """
    from generatore_agenda import matrimoni_per_anno

    # Anno dell'agenda sempre; anni futuri solo se hanno matrimoni prenotati
    anni: list[int] = [config.anno, config.anno + 1]
    anni_con_matrimoni_set: set[int] = set()
    for m in config.matrimoni_prenotati:
        if m.data is None:
            continue
        if m.data.year > config.anno + 1:
            anni_con_matrimoni_set.add(m.data.year)
    anni.extend(sorted(anni_con_matrimoni_set))

    tabelle = matrimoni_per_anno(config, anni)

    template = env.get_template("matrimoni_annuali.html")
    return template.render(
        tabelle=tabelle,
        nome_parrocchia=config.nome_parrocchia,
    )
