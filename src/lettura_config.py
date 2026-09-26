"""
Modulo per la lettura e l'unificazione delle configurazioni.

Legge:
- regole.yaml (dati stabili: feste, divieti, ricorrenze)
- config.xlsx (dati annuali: periodi, intenzioni, matrimoni, note)

E li unifica in un'unica struttura `Config` usabile dal resto del progetto.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

# ======================================================================
# DATACLASS — Strutture dati
# ======================================================================


@dataclass
class Periodo:
    """Un periodo dell'anno con i suoi orari di Messa.

    Attributes:
        dal: data di inizio del periodo
        al: data di fine del periodo
        orari_feriali: lista di orari (es. ["7:00", "10:00", "18:00"])
        orari_festivi: lista di orari (es. ["8:30", "10:00", "11:30", "18:00"])
    """

    dal: date
    al: date
    orari_feriali: list[str] = field(default_factory=list)
    orari_festivi: list[str] = field(default_factory=list)


@dataclass
class Festa:
    """Una festa a data fissa o mobile.

    Attributes:
        nome: nome della festa (es. "San Francesco")
        mese: mese (1-12), None per feste mobili
        giorno: giorno (1-31), None per feste mobili
        tipo: "fissa" | "mobile" | "speciale"
        salta_se_domenica: se True, la festa non si celebra se cade di domenica
        orari_ridotti: orari alternativi (opzionale), es. ["10:00", "18:00"]
    """

    nome: str
    mese: int | None = None
    giorno: int | None = None
    tipo: str = "fissa"
    salta_se_domenica: bool = False
    orari_ridotti: list[str] | None = None


@dataclass
class Ricorrenza:
    """Una ricorrenza propria della parrocchia (es. Triduo di San Salvatore).

    Attributes:
        nome: nome della ricorrenza
        data_inizio: data di inizio
        data_fine: data di fine (opzionale, per ricorrenze multi-giorno)
        tipo: "semplice" | "triduo" | "novena" | "ottavario"
        compilazione: "manuale" se va compilata a mano in agenda
        nota: nota informativa opzionale
    """

    nome: str
    data_inizio: date
    data_fine: date | None = None
    tipo: str = "semplice"
    compilazione: str = "auto"
    nota: str = ""


@dataclass
class Intenzione:
    """Un'intenzione di Messa dal registro.

    Attributes:
        numero: numero progressivo (dalla colonna A del foglio)
        data_consegna: quando è stata consegnata
        testo: testo dell'intenzione
        offerta: importo offerto (opzionale)
        data_applicazione: quando è stata applicata
        note: note aggiuntive
    """

    numero: int | None
    data_consegna: date | None
    testo: str
    offerta: float | None = None
    data_applicazione: date | None = None
    note: str = ""


@dataclass
class Matrimonio:
    """Una prenotazione di matrimonio.

    Attributes:
        data: data del matrimonio
        ora: orario (formato "HH:MM")
        nome_sposi: nomi degli sposi
        contatti: telefono/email di contatto
        note: note aggiuntive
    """

    data: date | None
    ora: str
    nome_sposi: str
    contatti: str = ""
    note: str = ""


@dataclass
class Config:
    """Struttura finale unificata.

    Contiene tutti i dati necessari al generatore di agenda,
    unendo le informazioni da YAML (stabili) e Excel (annuali).
    """

    # --- Da YAML (regole stabili) ---
    nome_parrocchia: str
    citta: str
    festivi_fissi: list[Festa] = field(default_factory=list)
    eccezioni_festivi: list[Festa] = field(default_factory=list)
    divieti_pomeridiani_fissi: list[Festa] = field(default_factory=list)
    divieti_pomeridiani_mobili: list[dict] = field(default_factory=list)
    ricorrenze_proprie: list[Ricorrenza] = field(default_factory=list)
    celebrazioni_mobili: list[str] = field(default_factory=list)
    giorni_accorpati: list[dict] = field(default_factory=list)
    nove_mercoledi: dict = field(default_factory=dict)
    matrimoni_config: dict = field(default_factory=dict)
    intenzioni_config: dict = field(default_factory=dict)

    # --- Da Excel (dati annuali) ---
    anno: int = 0
    periodi: list[Periodo] = field(default_factory=list)
    intenzioni: list[Intenzione] = field(default_factory=list)
    matrimoni_prenotati: list[Matrimonio] = field(default_factory=list)
    note_annuali: list[dict] = field(default_factory=list)


# ======================================================================
# LETTURA YAML
# ======================================================================


def leggi_yaml(percorso: Path) -> dict:
    """Legge un file YAML e restituisce il contenuto come dizionario.

    Args:
        percorso: percorso del file YAML da leggere

    Returns:
        Dizionario con il contenuto del file.
        Se il file è vuoto, restituisce un dizionario vuoto.

    Raises:
        FileNotFoundError: se il file non esiste
        ValueError: se il file non è uno YAML valido
    """
    if not percorso.exists():
        raise FileNotFoundError(f"File YAML non trovato: {percorso}")

    if not percorso.is_file():
        raise ValueError(f"Il percorso non è un file: {percorso}")

    try:
        with open(percorso, encoding="utf-8") as f:
            dati = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"YAML malformato in {percorso}: {e}") from e

    # yaml.safe_load restituisce None se il file è vuoto
    if dati is None:
        return {}

    # Ci aspettiamo un dizionario alla radice
    if not isinstance(dati, dict):
        raise ValueError(
            f"Il file YAML deve contenere un dizionario alla radice, "
            f"trovato invece: {type(dati).__name__}"
        )

    return dati
