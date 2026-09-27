"""
Modulo per la lettura e l'unificazione delle configurazioni.

Legge:
- regole.yaml (dati stabili: feste, divieti, ricorrenze)
- config.xlsx (dati annuali: periodi, intenzioni, matrimoni, note)

E li unifica in un'unica struttura `Config` usabile dal resto del progetto.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml
from openpyxl.worksheet.worksheet import Worksheet

from util import valore_come_stringa

logger = logging.getLogger(__name__)

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


# ======================================================================
# PARSING ORARI
# ======================================================================

# Regex per riconoscere un orario valido nel formato H:MM o HH:MM
# Esempi accettati: "7:00", "07:00", "18:30", "6:15"
REGEX_ORARIO = re.compile(r"^\d{1,2}:\d{2}$")


def parse_orari(stringa: str) -> list[str]:
    """Estrae la lista di orari da una stringa multi-orario.

    Separa su virgola, punto e virgola o spazi. Tiene solo i valori
    che rispettano il formato HH:MM (o H:MM).

    Args:
        stringa: stringa tipo "7:00,10:00,18:00" oppure "7:00;10:00" o "7:00 10:00"

    Returns:
        Lista di orari validi (es. ["7:00", "10:00", "18:00"]).
        Se la stringa è vuota, restituisce lista vuota.

    Examples:
        >>> parse_orari("7:00,10:00,18:00")
        ['7:00', '10:00', '18:00']
        >>> parse_orari("7:00;10:00")
        ['7:00', '10:00']
        >>> parse_orari("")
        []
        >>> parse_orari("pippo")
        ['pippo'] genera warning nel log
    """
    if not stringa:
        return []

    # Divide su virgola, punto e virgola o spazi (uno o più)
    parti = re.split(r"[,;\s]+", stringa.strip())

    orari_validi: list[str] = []
    for parte in parti:
        if not parte:  # Salta stringhe vuote (es. "7:00,,18:00")
            continue
        if REGEX_ORARIO.match(parte):
            orari_validi.append(parte)
        else:
            logger.warning(
                "Valore '%s' non è un orario valido (formato atteso HH:MM). Ignorato.",
                parte,
            )

    return orari_validi


# ======================================================================
# POSIZIONI FISSE NEL FOGLIO IMPOSTAZIONI
# ======================================================================

# Celle dei dati generali
CELLA_ANNO = "B5"
CELLA_NOME_PARROCCHIA = "B6"
CELLA_CITTA = "B7"

# Prima riga dei periodi e indici di colonna
RIGA_INIZIO_PERIODI = 13
COL_DAL = 1
COL_AL = 2
COL_FERIALI = 3
COL_FESTIVI = 4


# ======================================================================
# LETTURA FOGLIO IMPOSTAZIONI
# ======================================================================


def leggi_foglio_impostazioni(ws: Worksheet) -> dict:
    """Legge il foglio Impostazioni e restituisce i dati estratti.

    Args:
        ws: foglio di lavoro "Impostazioni"

    Returns:
        Dizionario con:
        - anno: int
        - nome_parrocchia: str
        - citta: str
        - periodi: list[dict] (ognuno con dal, al, orari_feriali, orari_festivi)

    Raises:
        ValueError: se le celle obbligatorie (anno, nome, città) sono vuote
    """
    # ------------------------------------------------------------------
    # DATI GENERALI
    # ------------------------------------------------------------------
    anno = ws[CELLA_ANNO].value
    if not isinstance(anno, int):
        raise ValueError(
            f"Impostazioni: cella {CELLA_ANNO} (Anno) deve essere un numero intero, "
            f"trovato: {type(anno).__name__}"
        )

    nome_parrocchia = ws[CELLA_NOME_PARROCCHIA].value
    if not nome_parrocchia or not isinstance(nome_parrocchia, str):
        raise ValueError(f"Impostazioni: cella {CELLA_NOME_PARROCCHIA} (Nome parrocchia) è vuota")

    citta = ws[CELLA_CITTA].value
    if not citta or not isinstance(citta, str):
        raise ValueError(f"Impostazioni: cella {CELLA_CITTA} (Città) è vuota")

    # ------------------------------------------------------------------
    # PERIODI
    # ------------------------------------------------------------------
    periodi: list[dict] = []

    # Itera dalla prima riga periodi fino all'ultima riga con contenuto
    ultima_riga = ws.max_row or RIGA_INIZIO_PERIODI
    for riga in range(RIGA_INIZIO_PERIODI, ultima_riga + 1):
        dal = ws.cell(row=riga, column=COL_DAL).value
        al = ws.cell(row=riga, column=COL_AL).value

        # Riga completamente vuota → ignora silenziosamente
        if dal is None and al is None:
            continue

        # Riga parziale: uno dei due manca → warning e ignora
        if dal is None or al is None:
            logger.warning(
                "Impostazioni, riga %d: 'Dal' o 'Al' mancante. Riga ignorata.",
                riga,
            )
            continue

        # Verifica che siano date native
        if not isinstance(dal, date) or not isinstance(al, date):
            logger.warning(
                "Impostazioni, riga %d: 'Dal' o 'Al' non sono date valide "
                "(trovato %s, %s). Riga ignorata.",
                riga,
                type(dal).__name__,
                type(al).__name__,
            )
            continue

        # Leggi orari
        feriali_str = valore_come_stringa(ws.cell(row=riga, column=COL_FERIALI))
        festivi_str = valore_come_stringa(ws.cell(row=riga, column=COL_FESTIVI))

        periodi.append(
            {
                "dal": dal,
                "al": al,
                "orari_feriali": parse_orari(str(feriali_str)),
                "orari_festivi": parse_orari(str(festivi_str)),
            }
        )

    if not periodi:
        logger.warning("Impostazioni: nessun periodo valido trovato nel foglio.")

    return {
        "anno": anno,
        "nome_parrocchia": nome_parrocchia,
        "citta": citta,
        "periodi": periodi,
    }
