"""
Lettura dei 4 fogli Excel del file config.xlsx.

Contiene le funzioni che leggono i fogli:
- Impostazioni: dati generali + periodi
- Intenzioni: registro intenzioni di Messa
- Matrimoni: prenotazioni matrimoni
- Note: annotazioni libere

E la funzione di supporto `parse_orari` per interpretare le stringhe
multi-orario (es. "7:00,10:00,18:00").

Uso tipico:
    from openpyxl import load_workbook
    from lettura_excel import leggi_foglio_impostazioni

    wb = load_workbook("configs/san_pietro_in_silki/config.xlsx")
    dati = leggi_foglio_impostazioni(wb["Impostazioni"])
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime, time

from openpyxl.worksheet.worksheet import Worksheet

from dataclass_config import Intenzione, Matrimonio
from util import valore_come_stringa

logger = logging.getLogger(__name__)

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
                "orari_feriali": parse_orari(feriali_str),
                "orari_festivi": parse_orari(festivi_str),
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


# ======================================================================
# POSIZIONI FISSE NEL FOGLIO INTENZIONI
# ======================================================================

RIGA_INIZIO_INTENZIONI = 2  # prima riga dati (riga 1 = intestazioni)
COL_INT_NUMERO = 1
COL_INT_DATA_CONSEGNA = 2
COL_INT_TESTO = 3
COL_INT_OFFERTA = 4
COL_INT_DATA_APPLICAZIONE = 5
COL_INT_NOTE = 6


# ======================================================================
# LETTURA FOGLIO INTENZIONI
# ======================================================================


def leggi_foglio_intenzioni(ws: Worksheet) -> list[Intenzione]:
    """Legge il foglio Intenzioni e restituisce la lista di intenzioni.

    Una riga è considerata "valida" se la colonna Data consegna (B) contiene
    una data. Altrimenti viene ignorata silenziosamente (riga vuota).

    Args:
        ws: foglio di lavoro "Intenzioni"

    Returns:
        Lista di oggetti Intenzione, in ordine di riga.

    Note:
        - La numerazione in colonna A è ignorata: la ricalcoliamo noi in base
          all'ordine delle righe valide.
        - Se Data consegna è compilata ma Intenzione è vuota → warning + ignora.
        - Offerta vuota o non valida → None.
        - Data applicazione vuota → None (può essere compilata dopo).
    """
    intenzioni: list[Intenzione] = []
    numero_progressivo = 0

    ultima_riga = ws.max_row or RIGA_INIZIO_INTENZIONI
    for riga in range(RIGA_INIZIO_INTENZIONI, ultima_riga + 1):
        # ------------------------------------------------------------------
        # Controllo: la riga è compilata?
        # ------------------------------------------------------------------
        data_consegna_raw = ws.cell(row=riga, column=COL_INT_DATA_CONSEGNA).value

        # Riga completamente vuota (nessuna data consegna) → ignora silenziosamente
        if data_consegna_raw is None:
            continue

        # Verifica che sia una data valida
        if not isinstance(data_consegna_raw, date):
            logger.warning(
                "Intenzioni, riga %d: 'Data consegna' non è una data valida "
                "(trovato: %s). Riga ignorata.",
                riga,
                type(data_consegna_raw).__name__,
            )
            continue

        # ------------------------------------------------------------------
        # Testo intenzione (obbligatorio)
        # ------------------------------------------------------------------
        testo_str = valore_come_stringa(ws.cell(row=riga, column=COL_INT_TESTO)).strip()

        if not testo_str:
            logger.warning(
                "Intenzioni, riga %d: 'Data consegna' presente ma 'Intenzione' "
                "mancante. Riga ignorata.",
                riga,
            )
            continue

        # ------------------------------------------------------------------
        # Offerta (opzionale)
        # ------------------------------------------------------------------
        offerta_raw = ws.cell(row=riga, column=COL_INT_OFFERTA).value
        offerta: float | None = None

        if offerta_raw is not None:
            if isinstance(offerta_raw, (int, float)):
                offerta = float(offerta_raw)
            else:
                logger.warning(
                    "Intenzioni, riga %d: 'Offerta' non numerica (trovato: %s). "
                    "Impostata a None.",
                    riga,
                    type(offerta_raw).__name__,
                )

        # ------------------------------------------------------------------
        # Data applicazione (opzionale)
        # ------------------------------------------------------------------
        data_applicazione_raw = ws.cell(row=riga, column=COL_INT_DATA_APPLICAZIONE).value
        data_applicazione: date | None = None

        if data_applicazione_raw is not None:
            if isinstance(data_applicazione_raw, date):
                data_applicazione = data_applicazione_raw
            else:
                logger.warning(
                    "Intenzioni, riga %d: 'Data applicazione' non è una data valida "
                    "(trovato: %s). Impostata a None.",
                    riga,
                    type(data_applicazione_raw).__name__,
                )

        # ------------------------------------------------------------------
        # Note (opzionale)
        # ------------------------------------------------------------------
        note = valore_come_stringa(ws.cell(row=riga, column=COL_INT_NOTE)).strip()

        # ------------------------------------------------------------------
        # Crea oggetto Intenzione
        # ------------------------------------------------------------------
        numero_progressivo += 1

        intenzioni.append(
            Intenzione(
                numero=numero_progressivo,
                data_consegna=data_consegna_raw,
                testo=testo_str,
                offerta=offerta,
                data_applicazione=data_applicazione,
                note=note,
            )
        )

    return intenzioni


# ======================================================================
# POSIZIONI FISSE NEL FOGLIO MATRIMONI
# ======================================================================

RIGA_INIZIO_MATRIMONI = 2  # prima riga dati (riga 1 = intestazioni)
COL_MAT_DATA = 1
COL_MAT_ORA = 2
COL_MAT_NOME_SPOSI = 3
COL_MAT_CONTATTI = 4
COL_MAT_NOTE = 5


# ======================================================================
# LETTURA FOGLIO MATRIMONI
# ======================================================================


def leggi_foglio_matrimoni(ws: Worksheet) -> list[Matrimonio]:
    """Legge il foglio Matrimoni e restituisce la lista di prenotazioni.

    Una riga è considerata "valida" se la colonna Data (A) contiene una data
    e la colonna Ora (B) contiene un orario nel formato HH:MM.

    Args:
        ws: foglio di lavoro "Matrimoni"

    Returns:
        Lista di oggetti Matrimonio, in ordine di riga.

    Note:
        - Data mancante → riga ignorata silenziosamente (riga vuota).
        - Data non-data → warning + riga ignorata.
        - Nome sposi mancante → warning + riga ignorata.
        - Ora mancante o non valida → warning + riga ignorata.
        - Contatti e Note sono opzionali (stringa vuota se mancanti).
    """
    matrimoni: list[Matrimonio] = []

    ultima_riga = ws.max_row or RIGA_INIZIO_MATRIMONI
    for riga in range(RIGA_INIZIO_MATRIMONI, ultima_riga + 1):
        # ------------------------------------------------------------------
        # Data (obbligatoria, identifica la riga compilata)
        # ------------------------------------------------------------------
        data_raw = ws.cell(row=riga, column=COL_MAT_DATA).value

        # Riga completamente vuota → ignora silenziosamente
        if data_raw is None:
            continue

        if not isinstance(data_raw, date):
            logger.warning(
                "Matrimoni, riga %d: 'Data' non è una data valida " "(trovato: %s). Riga ignorata.",
                riga,
                type(data_raw).__name__,
            )
            continue

        # ------------------------------------------------------------------
        # Ora (obbligatoria, formato HH:MM)
        # ------------------------------------------------------------------
        # L'ora in Excel/LibreOffice può essere:
        # - una stringa "15:30"
        # - un oggetto datetime.time (se formattata come ora nativa)
        # - un oggetto datetime.datetime (raro)
        # Gestiamo tutti i casi.
        ora_raw = ws.cell(row=riga, column=COL_MAT_ORA).value
        ora_str = ""

        if ora_raw is None:
            logger.warning(
                "Matrimoni, riga %d: 'Ora' mancante. Riga ignorata.",
                riga,
            )
            continue

        if isinstance(ora_raw, str):
            ora_str = ora_raw.strip()
        elif isinstance(ora_raw, time):
            ora_str = ora_raw.strftime("%H:%M")
        elif isinstance(ora_raw, datetime):
            ora_str = ora_raw.strftime("%H:%M")
        else:
            logger.warning(
                "Matrimoni, riga %d: 'Ora' non valida (trovato: %s). Riga ignorata.",
                riga,
                type(ora_raw).__name__,
            )
            continue

        # Verifica formato HH:MM
        if not REGEX_ORARIO.match(ora_str):
            logger.warning(
                "Matrimoni, riga %d: 'Ora' non è nel formato HH:MM (trovato: '%s'). "
                "Riga ignorata.",
                riga,
                ora_str,
            )
            continue

        # ------------------------------------------------------------------
        # Nome sposi (obbligatorio)
        # ------------------------------------------------------------------
        nome_sposi = valore_come_stringa(ws.cell(row=riga, column=COL_MAT_NOME_SPOSI)).strip()

        if not nome_sposi:
            logger.warning(
                "Matrimoni, riga %d: 'Data' e 'Ora' presenti ma 'Nome sposi' "
                "mancante. Riga ignorata.",
                riga,
            )
            continue

        # ------------------------------------------------------------------
        # Contatti e Note (opzionali)
        # ------------------------------------------------------------------
        contatti = valore_come_stringa(ws.cell(row=riga, column=COL_MAT_CONTATTI)).strip()
        note = valore_come_stringa(ws.cell(row=riga, column=COL_MAT_NOTE)).strip()

        # ------------------------------------------------------------------
        # Crea oggetto Matrimonio
        # ------------------------------------------------------------------
        matrimoni.append(
            Matrimonio(
                data=data_raw,
                ora=ora_str,
                nome_sposi=nome_sposi,
                contatti=contatti,
                note=note,
            )
        )

    return matrimoni


# ======================================================================
# POSIZIONI FISSE NEL FOGLIO NOTE
# ======================================================================

RIGA_INIZIO_NOTE = 2  # prima riga dati (riga 1 = intestazioni)
COL_NOTE_DAL = 1
COL_NOTE_AL = 2
COL_NOTE_TESTO = 3


# ======================================================================
# LETTURA FOGLIO NOTE
# ======================================================================


def leggi_foglio_note(ws: Worksheet) -> list[dict]:
    """Legge il foglio Note e restituisce la lista di annotazioni.

    Una riga è considerata "valida" se la colonna Dal (A) contiene una data
    e la colonna Nota (C) contiene un testo.

    Comportamento Al:
    - Se Al (B) è vuoto → Al = Dal (nota di un solo giorno)
    - Se Al è compilato → deve essere una data, e deve essere >= Dal

    Args:
        ws: foglio di lavoro "Note"

    Returns:
        Lista di dict, ognuno con:
        - dal: date
        - al: date
        - nota: str

    Note:
        - Dal mancante → riga ignorata silenziosamente (riga vuota).
        - Dal non-data → warning + riga ignorata.
        - Nota mancante → warning + riga ignorata.
        - Al vuoto → Al = Dal.
        - Al non-data → warning + riga ignorata.
        - Al < Dal → warning + riga ignorata.
    """
    note: list[dict] = []

    ultima_riga = ws.max_row or RIGA_INIZIO_NOTE
    for riga in range(RIGA_INIZIO_NOTE, ultima_riga + 1):
        # ------------------------------------------------------------------
        # Dal (obbligatorio, identifica la riga compilata)
        # ------------------------------------------------------------------
        dal_raw = ws.cell(row=riga, column=COL_NOTE_DAL).value

        # Riga completamente vuota → ignora silenziosamente
        if dal_raw is None:
            continue

        if not isinstance(dal_raw, date):
            logger.warning(
                "Note, riga %d: 'Dal' non è una data valida (trovato: %s). " "Riga ignorata.",
                riga,
                type(dal_raw).__name__,
            )
            continue

        # ------------------------------------------------------------------
        # Al (opzionale, default = Dal)
        # ------------------------------------------------------------------
        al_raw = ws.cell(row=riga, column=COL_NOTE_AL).value
        al: date

        if al_raw is None:
            # Comportamento: Al = Dal (nota di un solo giorno)
            al = dal_raw
        elif isinstance(al_raw, date):
            al = al_raw
        else:
            logger.warning(
                "Note, riga %d: 'Al' non è una data valida (trovato: %s). " "Riga ignorata.",
                riga,
                type(al_raw).__name__,
            )
            continue

        # Verifica che Al >= Dal
        if al < dal_raw:
            logger.warning(
                "Note, riga %d: 'Al' (%s) è precedente a 'Dal' (%s). " "Riga ignorata.",
                riga,
                al.strftime("%d/%m/%Y"),
                dal_raw.strftime("%d/%m/%Y"),
            )
            continue

        # ------------------------------------------------------------------
        # Nota (obbligatoria)
        # ------------------------------------------------------------------
        nota = valore_come_stringa(ws.cell(row=riga, column=COL_NOTE_TESTO)).strip()

        if not nota:
            logger.warning(
                "Note, riga %d: 'Dal' presente ma 'Nota' mancante. Riga ignorata.",
                riga,
            )
            continue

        # ------------------------------------------------------------------
        # Crea dict per la nota
        # ------------------------------------------------------------------
        note.append(
            {
                "dal": dal_raw,
                "al": al,
                "nota": nota,
            }
        )

    return note
