"""
Stili, colori, font e funzioni di formattazione per il progetto
Agenda Parrocchiale.

Questo modulo centralizza tutto ciò che riguarda l'aspetto grafico
dei file Excel generati. Modificando una costante qui, cambia il
risultato in tutti i fogli.

Contiene:
- Costanti (colori, font, bordi, riempimenti)
- Funzioni di stile per singole celle (titolo, etichetta, compilabile, nota)
- Funzione utility per l'auto-fit delle colonne
"""

from __future__ import annotations

from openpyxl.styles import Alignment, Border, Font, PatternFill, Protection, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

# ======================================================================
# COLORI
# ======================================================================

GIALLO_COMPILABILE = "FFF9C4"  # giallo chiaro: celle modificabili
GRIGIO_INTESTAZIONE = "D9D9D9"  # grigio: intestazioni tabella
GRIGIO_ETICHETTA = "F2F2F2"  # grigio chiaro: etichette fisse
BLU_TITOLO = "1F4E79"  # blu scuro: titoli principali
BIANCO = "FFFFFF"  # bianco: testo su sfondo blu

# ======================================================================
# FONT
# ======================================================================

FONT_TITOLO = Font(bold=True, size=14, color=BIANCO)
FONT_INTESTAZIONE = Font(bold=True, size=11)
FONT_ETICHETTA = Font(bold=True, size=10)
FONT_NORMALE = Font(size=10)
FONT_NOTA = Font(italic=True, size=9, color="808080")

# ======================================================================
# BORDI
# ======================================================================

BORDO_SOTTILE = Border(
    left=Side(style="thin", color="BFBFBF"),
    right=Side(style="thin", color="BFBFBF"),
    top=Side(style="thin", color="BFBFBF"),
    bottom=Side(style="thin", color="BFBFBF"),
)

# ======================================================================
# RIEMPIMENTI
# ======================================================================

FILL_GIALLO = PatternFill("solid", fgColor=GIALLO_COMPILABILE)
FILL_INTESTAZIONE = PatternFill("solid", fgColor=GRIGIO_INTESTAZIONE)
FILL_ETICHETTA = PatternFill("solid", fgColor=GRIGIO_ETICHETTA)
FILL_TITOLO = PatternFill("solid", fgColor=BLU_TITOLO)

# ======================================================================
# FUNZIONI DI STILE CELLE
# ======================================================================


def stile_titolo(ws: Worksheet, cella: str, testo: str, larghezza_merge: int = 6) -> None:
    """Scrive un titolo in una cella, lo formatta e lo unisce su più colonne.

    Args:
        ws: foglio di lavoro
        cella: indirizzo della cella (es. "A1")
        testo: testo del titolo
        larghezza_merge: quante colonne unire (default 6)
    """
    ws[cella] = testo
    ws[cella].font = FONT_TITOLO
    ws[cella].fill = FILL_TITOLO
    ws[cella].alignment = Alignment(horizontal="left", vertical="center")
    colonna_iniziale = ws[cella].column
    colonna_finale = colonna_iniziale + larghezza_merge - 1
    ws.merge_cells(
        start_row=ws[cella].row,
        start_column=colonna_iniziale,
        end_row=ws[cella].row,
        end_column=colonna_finale,
    )
    ws.row_dimensions[ws[cella].row].height = 22


def stile_etichetta(ws: Worksheet, cella: str, testo: str) -> None:
    """Etichetta non compilabile (sfondo grigio, testo in grassetto)."""
    ws[cella] = testo
    ws[cella].font = FONT_ETICHETTA
    ws[cella].fill = FILL_ETICHETTA
    ws[cella].border = BORDO_SOTTILE
    ws[cella].alignment = Alignment(horizontal="left", vertical="center")


def stile_compilabile(
    ws: Worksheet,
    cella: str,
    valore=None,
    formato: str | None = None,
) -> None:
    """Cella gialla compilabile dall'utente.

    Args:
        ws: foglio di lavoro
        cella: indirizzo della cella (es. "B5")
        valore: valore opzionale da scrivere
        formato: formato numerico opzionale (es. "0", "DD/MM/YYYY")
    """
    if valore is not None:
        ws[cella] = valore
    ws[cella].fill = FILL_GIALLO
    ws[cella].border = BORDO_SOTTILE
    ws[cella].font = FONT_NORMALE
    ws[cella].alignment = Alignment(horizontal="left", vertical="center")
    if formato:
        ws[cella].number_format = formato


def stile_nota(ws: Worksheet, cella: str, testo: str) -> None:
    """Nota informativa in corsivo, grigio chiaro."""
    ws[cella] = testo
    ws[cella].font = FONT_NOTA
    ws[cella].alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)


# ======================================================================
# FUNZIONI UTILITY
# ======================================================================


def auto_adatta_colonne(ws: Worksheet, padding: int = 2) -> None:
    """Imposta la larghezza di ogni colonna in base al contenuto più lungo.

    Args:
        ws: foglio di lavoro
        padding: caratteri extra di margine
    """
    for indice, colonna in enumerate(ws.columns, start=1):
        lunghezza_max = 0
        for cella in colonna:
            valore = cella.value
            if valore is None:
                continue
            if isinstance(valore, (str, int, float)):
                lunghezza = len(str(valore))
            else:
                # Date, formule, oggetti openpyxl → stima conservativa
                lunghezza = 10
            if lunghezza > lunghezza_max:
                lunghezza_max = lunghezza
        larghezza = min(max(lunghezza_max + padding, 8), 60)
        ws.column_dimensions[get_column_letter(indice)].width = larghezza


# ======================================================================
# PROTEZIONE
# ======================================================================


def proteggi_foglio(ws: Worksheet, celle_sbloccate: list[str] | None = None) -> None:
    """Protegge il foglio bloccando tutte le celle.

    Args:
        ws: foglio di lavoro
        celle_sbloccate: lista di intervalli da lasciare sbloccati
                         (es. ["B2:F401", "A2:A101"]).
                         Se None, blocca tutto.
    """
    # Blocca tutte le celle
    for row in ws.iter_rows():
        for cell in row:
            cell.protection = Protection(locked=True)

    # Sblocca le celle indicate
    if celle_sbloccate:
        for intervallo in celle_sbloccate:
            for row in ws[intervallo]:
                for cell in row:
                    cell.protection = Protection(locked=False)

    ws.protection.sheet = True
    ws.protection.enable()
