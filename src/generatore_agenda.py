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

from calcolo_liturgico import calcola_corpus_domini
from dataclass_config import Config, Intenzione, Matrimonio, Periodo

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


def festivo_fisso(data: date, config: Config) -> str | None:
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


def determina_tipo_giorno(data: date, config: Config) -> tuple[str, str | None]:
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
    nome_festivo = festivo_fisso(data, config)
    if nome_festivo is not None:
        return "festivo", nome_festivo

    # 2. Domenica?
    if data.weekday() == 6:
        return "domenica", None

    # 3. Feriale
    return "feriale", None


def trova_periodo(data: date, config: Config) -> Periodo | None:
    """Trova il periodo stagionale attivo per una data.

    Scorre config.periodi e restituisce il primo periodo il cui
    intervallo [dal, al] contiene la data.

    Args:
        data: data da verificare
        config: Config con la lista periodi

    Returns:
        Il Periodo attivo, o None se nessuno matcha (con warning).
    """
    for periodo in config.periodi:
        if periodo.dal <= data <= periodo.al:
            return periodo

    logger.warning(
        "Nessun periodo trovato per la data %s. Possibile buco nella configurazione.",
        data,
    )
    return None


def orari_per_giorno(data: date, tipo: str, config: Config) -> list[str]:
    """Restituisce gli orari delle Messe per un giorno.

    Regola:
    - Giorno feriale → orari_feriali del periodo attivo
    - Domenica, festivo, solennità → orari_festivi del periodo attivo

    Args:
        data: data del giorno
        tipo: tipo del giorno ("feriale" | "domenica" | "festivo" | "solennita")
        config: Config con i periodi

    Returns:
        Lista di orari. Lista vuota se nessun periodo trovato.
    """
    periodo = trova_periodo(data, config)
    if periodo is None:
        return []

    if tipo == "feriale":
        return list(periodo.orari_feriali)
    # Domenica, festivo, solennità → orari festivi
    return list(periodo.orari_festivi)


def applica_eccezioni_orari(data: date, orari: list[str], config: Config) -> list[str]:
    """Applica le eccezioni agli orari di un festivo.

    Le eccezioni gestite (da config.eccezioni_festivi):
    - salta_se_domenica=True → se cade di domenica, festa non celebrata (lista vuota)
    - orari_ridotti=[...] → sostituiscono gli orari normali

    Args:
        data: data del giorno
        orari: orari "normali" del giorno (già calcolati)
        config: Config con eccezioni_festivi

    Returns:
        Lista di orari dopo l'applicazione delle eccezioni.
    """
    for eccezione in config.eccezioni_festivi:
        # Corrisponde alla data?
        if eccezione.mese != data.month or eccezione.giorno != data.day:
            continue

        # Caso 1: salta se domenica
        if eccezione.salta_se_domenica and data.weekday() == 6:
            logger.info(
                "Festa '%s' del %s cade di domenica → non celebrata.",
                eccezione.nome,
                data,
            )
            return []

        # Caso 2: orari ridotti
        if eccezione.orari_ridotti:
            logger.info(
                "Festa '%s' del %s ha orari ridotti: %s",
                eccezione.nome,
                data,
                eccezione.orari_ridotti,
            )
            return list(eccezione.orari_ridotti)

    return orari


def _e_divieto_pomeridiano(data: date, config: Config) -> bool:
    """Verifica se la data ha un divieto pomeridiano.

    Controlla:
    1. Divieti fissi (config.divieti_pomeridiani_fissi)
    2. Divieti mobili (Corpus Domini, calcolato per l'anno della data)

    Args:
        data: data da verificare
        config: Config con i divieti

    Returns:
        True se la data ha un divieto pomeridiano.
    """
    # 1. Divieti fissi
    for divieto in config.divieti_pomeridiani_fissi:
        if divieto.mese == data.month and divieto.giorno == data.day:
            return True

    # 2. Divieti mobili (Corpus Domini per l'anno della data)
    for divieto in config.divieti_pomeridiani_mobili:
        tipo = divieto.get("tipo")
        if tipo == "corpus_domini":
            corpus_domini = calcola_corpus_domini(data.year)
            if data == corpus_domini:
                return True

    return False


def applica_divieti_pomeridiani(data: date, orari: list[str], config: Config) -> list[str]:
    """Rimuove le Messe pomeridiane nei giorni con divieto.

    Nei giorni con divieto pomeridiano (Assunta, San Nicola, Corpus Domini)
    le Messe si celebrano solo al mattino (orari < 14:00).

    Args:
        data: data del giorno
        orari: orari "normali" del giorno (già calcolati)
        config: Config con i divieti

    Returns:
        Lista di orari dopo l'applicazione dei divieti.
    """
    if not _e_divieto_pomeridiano(data, config):
        return orari

    orari_mattina: list[str] = []
    for orario in orari:
        # Parsa "HH:MM" e controlla se è mattina (ore < 14)
        try:
            ore = int(orario.split(":")[0])
        except (ValueError, IndexError):
            # Orario malformato → tieni così com'è (warning)
            logger.warning(
                "Orario malformato '%s' per %s: mantenuto senza filtraggio.",
                orario,
                data,
            )
            orari_mattina.append(orario)
            continue

        if ore < 14:
            orari_mattina.append(orario)
        else:
            logger.info(
                "Divieto pomeridiano per %s: rimuovo orario '%s'.",
                data,
                orario,
            )

    return orari_mattina
