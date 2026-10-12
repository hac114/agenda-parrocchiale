"""
Script di sviluppo: genera un PDF di prova con 4 giorni rappresentativi.

Utile per mostrare a un utente il nuovo layout della pagina giorno
PRIMA di applicarlo a tutta l'agenda.

Output: output/Mockup_Layout.pdf (4 pagine)

Uso:
    python scripts/genera_mockup.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

# Aggiungi src al path
ROOT_PROGETTO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_PROGETTO / "src"))

from jinja2 import Environment, FileSystemLoader, select_autoescape  # noqa: E402

from calcolo_liturgico import calcola_tutte_date_mobili  # noqa: E402
from config import carica_config  # noqa: E402
from generatore_agenda import (  # noqa: E402
    applica_divieti_pomeridiani,
    applica_eccezioni_orari,
    determina_tipo_giorno,
    festivita_del_giorno,
    matrimoni_del_giorno,
    orari_per_giorno,
    trova_periodo,
)
from util import formatta_data_italiana, nome_giorno_italiano  # noqa: E402

# ======================================================================
# CONFIGURAZIONE
# ======================================================================

CARTELLA_TEMPLATES = ROOT_PROGETTO / "templates"
CARTELLA_OUTPUT = ROOT_PROGETTO / "output"

# Giorni rappresentativi da mostrare nel mockup
GIORNI_MOCKUP = [
    date(2027, 1, 3),  # Domenica normale (4 Messe)
    date(2027, 1, 4),  # Feriale normale (3 Messe)
    date(2027, 3, 17),  # San Salvatore (solennità)
    date(2027, 5, 15),  # Maggio (7 Messe)
]

# Configurazione righe extra (dal YAML in futuro)
RIGHE_EXTRA_DEFAULT = {
    "18:00": 3,
    "19:00": 3,
    "21:00": 3,
}


# ======================================================================
# FUNZIONI
# ======================================================================


def prepara_righe_messe(orari: list[str]) -> list[dict]:
    """Prepara le righe della tabella messe con eventuali righe extra.

    Args:
        orari: lista di orari (es. ["7:00", "10:00", "18:00"])

    Returns:
        Lista di dict con "orario" e "righe_extra".
    """
    righe = []
    for orario in orari:
        righe.append(
            {
                "orario": orario,
                "righe_extra": RIGHE_EXTRA_DEFAULT.get(orario, 1),
            }
        )
    return righe


def genera_mockup() -> Path:
    """Genera il PDF di mockup con i 4 giorni rappresentativi.

    Returns:
        Percorso del PDF generato.
    """
    from weasyprint import HTML

    # Carica la config
    config = carica_config("san_pietro_in_silki")
    date_mobili = calcola_tutte_date_mobili(config.anno)

    # Configura Jinja2
    env = Environment(
        loader=FileSystemLoader(str(CARTELLA_TEMPLATES)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("agenda_mockup.html")

    # Leggi il CSS
    css = (CARTELLA_TEMPLATES / "style_mockup.css").read_text(encoding="utf-8")

    # Genera HTML per ogni giorno
    html_pagine: list[str] = []
    for giorno_data in GIORNI_MOCKUP:
        # Tipo e nome
        tipo, nome_festivo = determina_tipo_giorno(giorno_data, config)
        info_festivita = festivita_del_giorno(giorno_data, config, date_mobili)
        nome = nome_festivo or info_festivita["nome"]

        # Orari
        orari = orari_per_giorno(giorno_data, tipo, config)
        orari = applica_eccezioni_orari(giorno_data, orari, config)
        orari = applica_divieti_pomeridiani(giorno_data, orari, config)

        # Righe per la tabella
        righe_messe = prepara_righe_messe(orari)

        # Renderizza
        html = template.render(
            data_formattata=formatta_data_italiana(giorno_data),
            giorno_settimana=nome_giorno_italiano(giorno_data),
            nome_festivita=nome,
            righe_messe=righe_messe,
        )
        html_pagine.append(_estrai_body(html))

    # Assembla
    html_completo = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Mockup Layout Agenda</title>
    <style>
{css}
    </style>
</head>
<body>
{"".join(html_pagine)}
</body>
</html>
"""

    # Genera PDF
    CARTELLA_OUTPUT.mkdir(parents=True, exist_ok=True)
    percorso_output = CARTELLA_OUTPUT / "Mockup_Layout.pdf"
    HTML(string=html_completo, base_url=str(CARTELLA_TEMPLATES)).write_pdf(str(percorso_output))

    return percorso_output


def _estrai_body(html: str) -> str:
    """Estrae il contenuto del body."""
    inizio = html.find("<body>")
    fine = html.find("</body>")
    if inizio == -1 or fine == -1:
        return html
    return html[inizio + len("<body>") : fine]


# ======================================================================
# MAIN
# ======================================================================


def main() -> None:
    """Genera il mockup e stampa il percorso."""
    print("Generazione mockup in corso...")
    percorso = genera_mockup()
    print(f"✅ Mockup generato: {percorso}")
    print(f"   Pagine: {len(GIORNI_MOCKUP)}")


if __name__ == "__main__":
    main()
