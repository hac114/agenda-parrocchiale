"""
Generatore dell'agenda completa a partire da Config + calcolo liturgico.

Unisce:
- I dati di configurazione (Config, da YAML + Excel)
- Le date mobili dell'anno (calcolo_liturgico)

Per produrre un CalendarioAgenda: 365/366 GiornoAgenda, ognuno con
tipo, orari, festività, intenzioni, matrimoni, note.

Uso tipico:
    from generatore_agenda import genera_agenda_da_profilo

    calendario = genera_agenda_da_profilo("san_pietro_in_silki")
    for giorno in calendario.giorni:
        print(giorno.data, giorno.tipo, giorno.orari)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date

from dataclass_config import Config, Intenzione, Matrimonio

logger = logging.getLogger(__name__)

# ======================================================================
# DATACLASS
# ======================================================================


@dataclass
class GiornoAgenda:
    """Rappresenta un singolo giorno dell'agenda.

    Attributes:
        data: la data del giorno
        tipo: "feriale" | "domenica" | "festivo" | "solennita"
        nome: nome della festività (es. "Natale"), None se feriale/domenica
        particolare: True se è una "celebrazione particolare" del santuario
        orari: lista di orari delle Messe (es. ["7:00", "10:00", "18:00"])
        intenzioni: lista di intenzioni di Messa applicate in questo giorno
        matrimoni: lista di matrimoni previsti in questo giorno
        note: lista di note (dict con "dal", "al", "nota")
    """

    data: date
    tipo: str
    nome: str | None = None
    particolare: bool = False
    orari: list[str] = field(default_factory=list)
    intenzioni: list[Intenzione] = field(default_factory=list)
    matrimoni: list[Matrimonio] = field(default_factory=list)
    note: list[dict] = field(default_factory=list)


@dataclass
class CalendarioAgenda:
    """Contenitore del calendario completo.

    Attributes:
        anno: anno di riferimento
        config: la Config usata per generare il calendario
        giorni: lista di GiornoAgenda in ordine cronologico
    """

    anno: int
    config: Config
    giorni: list[GiornoAgenda] = field(default_factory=list)


# ======================================================================
# HELPER INTERNI
# ======================================================================


def _festivo_fisso(data: date, config: Config) -> str | None:
    """Restituisce il nome del festivo fisso se la data corrisponde, altrimenti None.

    Args:
        data: data da controllare
        config: Config con la lista festivi_fissi

    Returns:
        Nome del festivo fisso, o None se non è un festivo.
    """
    for festa in config.festivi_fissi:
        if festa.mese == data.month and festa.giorno == data.day:
            return str(festa.nome)
    return None


def _determina_tipo_giorno(data: date, config: Config) -> tuple[str, str | None]:
    """Determina tipo e nome del giorno.

    Logica:
    1. Se è un festivo fisso (da config.festivi_fissi) → "festivo"
    2. Se è domenica → "domenica"
    3. Altrimenti → "feriale"

    Args:
        data: data da classificare
        config: Config con festivi_fissi

    Returns:
        Tupla (tipo, nome):
        - tipo: "festivo" | "domenica" | "feriale"
        - nome: nome della festa (solo per "festivo"), altrimenti None
    """
    # 1. Festivo fisso?
    nome_festivo = _festivo_fisso(data, config)
    if nome_festivo is not None:
        return "festivo", nome_festivo

    # 2. Domenica?
    if data.weekday() == 6:
        return "domenica", None

    # 3. Feriale
    return "feriale", None
