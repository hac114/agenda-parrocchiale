"""
Utility condivise del progetto Agenda Parrocchiale.

Contiene:
- Configurazione del logging standard
- Sistema di raccolta warning per riepilogo finale
- Funzioni di utilità generale (helper per celle Excel)

Il logging è configurato una sola volta all'avvio dello script principale
(chiamando `configura_logging()`), poi ogni modulo usa:

    import logging
    logger = logging.getLogger(__name__)

Il WarningCollector raccoglie tutti i warning emessi durante l'esecuzione.
Alla fine dello script, `mostra_riepilogo_warning()` può essere chiamato per
mostrare il riepilogo e chiedere conferma all'utente.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

# ======================================================================
# COSTANTI
# ======================================================================

# Formato del logger (tecnico, con nome modulo e livello)
FORMATO_LOG = "[%(levelname)s] %(name)s: %(message)s"

# Data/ora nel formato del log
FORMATO_DATA = "%Y-%m-%d %H:%M:%S"


# ======================================================================
# WARNING COLLECTOR
# ======================================================================


class WarningCollector(logging.Handler):
    """Handler di logging che raccoglie i warning per il riepilogo finale.

    Funziona come un normale handler (stampa subito i warning sulla console),
    ma tiene anche traccia di tutti i warning emessi, per poterli mostrare
    in un riepilogo alla fine dello script.

    Attributes:
        warnings: lista dei messaggi di warning raccolti.
    """

    def __init__(self) -> None:
        super().__init__(level=logging.WARNING)
        self.warnings: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Registra il warning nella lista interna."""
        self.warnings.append(self.format(record))

    def ha_warning(self) -> bool:
        """Restituisce True se ci sono warning raccolti."""
        return len(self.warnings) > 0

    def conta_warning(self) -> int:
        """Restituisce il numero di warning raccolti."""
        return len(self.warnings)

    def svuota(self) -> None:
        """Svuota la lista dei warning raccolti."""
        self.warnings.clear()


# ======================================================================
# CONFIGURAZIONE LOGGING
# ======================================================================


def configura_logging(livello: int = logging.INFO) -> WarningCollector:
    """Configura il logging per tutto il progetto e restituisce il collector.

    Da chiamare UNA SOLA VOLTA all'avvio dello script principale.
    Dopo la chiamata, ogni modulo può usare:
        logger = logging.getLogger(__name__)

    Args:
        livello: livello minimo di log (default: INFO).
                 - logging.DEBUG → mostra anche debug
                 - logging.INFO → mostra info, warning, error, critical
                 - logging.WARNING → mostra solo warning e superiori

    Returns:
        Un'istanza di WarningCollector con tutti i warning raccolti.
        Va passata a `mostra_riepilogo_warning()` alla fine dello script.
    """
    # Configura il logger root
    logging.basicConfig(
        level=livello,
        format=FORMATO_LOG,
        datefmt=FORMATO_DATA,
    )

    # Aggiungi il collector al logger root
    collector = WarningCollector()
    collector.setFormatter(logging.Formatter(FORMATO_LOG))
    logging.getLogger().addHandler(collector)

    return collector


def mostra_riepilogo_warning(collector: WarningCollector) -> bool:
    """Mostra il riepilogo dei warning e chiede conferma all'utente.

    Args:
        collector: il WarningCollector con i warning raccolti.

    Returns:
        True se l'utente conferma di voler procedere,
        False se preferisce interrompere.
    """
    if not collector.ha_warning():
        return True

    num = collector.conta_warning()
    print()
    print("=" * 70)
    print(f"⚠️  ATTENZIONE: {num} problemi rilevati durante la lettura")
    print("=" * 70)
    print()
    for warning in collector.warnings:
        print(f"  {warning}")
    print()

    risposta = input("Vuoi comunque procedere? [y/N]: ").strip().lower()
    return risposta in ("y", "yes", "s", "si", "sì")


# ======================================================================
# HELPER PER CELLE EXCEL
# ======================================================================


def valore_come_stringa(cella: Any) -> str:
    """Estrae il valore di una cella openpyxl come stringa.

    Gestisce il caso di cella vuota (None) restituendo stringa vuota.
    Utile per normalizzare valori di celle che potrebbero contenere
    stringhe, numeri, date o None.

    Args:
        cella: cella openpyxl (con attributo .value)

    Returns:
        Stringa vuota se la cella è vuota, altrimenti str(valore).
    """
    valore = cella.value
    if valore is None:
        return ""
    return str(valore)


# ======================================================================
# NORMALIZZAZIONE DATE
# ======================================================================


def normalizza_data(valore: Any) -> date | None:
    """Normalizza un valore di cella Excel a date (senza ora).

    Excel restituisce date come datetime.datetime (con ore/minuti/secondi
    a 00:00:00). Questa funzione estrae solo la parte data.

    Args:
        valore: valore della cella (può essere date, datetime, str, None)

    Returns:
        La data come `date`, o None se il valore non è una data valida.
    """
    if isinstance(valore, datetime):
        return valore.date()
    if isinstance(valore, date):
        return valore
    return None


# ======================================================================
# FORMATTAZIONE DATE ITALIANE
# ======================================================================

MESI_ITALIANI = [
    "gennaio",
    "febbraio",
    "marzo",
    "aprile",
    "maggio",
    "giugno",
    "luglio",
    "agosto",
    "settembre",
    "ottobre",
    "novembre",
    "dicembre",
]

GIORNI_ITALIANI = [
    "Lunedì",
    "Martedì",
    "Mercoledì",
    "Giovedì",
    "Venerdì",
    "Sabato",
    "Domenica",
]


def formatta_data_italiana(data: date) -> str:
    """Formatta una data in italiano: '17 marzo 2027'.

    Args:
        data: data da formattare

    Returns:
        Stringa in formato 'gg mese aaaa'.
    """
    return f"{data.day} {MESI_ITALIANI[data.month - 1]} {data.year}"


def nome_giorno_italiano(data: date) -> str:
    """Restituisce il nome italiano del giorno della settimana.

    Args:
        data: data di riferimento

    Returns:
        Nome del giorno (es. 'Mercoledì').
    """
    return GIORNI_ITALIANI[data.weekday()]
