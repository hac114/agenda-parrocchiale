"""
Dataclass condivise del progetto Agenda Parrocchiale.

Contiene le strutture dati usate per rappresentare:
- Periodo: un periodo dell'anno con i suoi orari di Messa
- Festa: una festa a data fissa o mobile
- Ricorrenza: una ricorrenza propria della parrocchia
- Intenzione: un'intenzione di Messa dal registro
- Matrimonio: una prenotazione di matrimonio
- Config: struttura finale unificata (YAML + Excel)

Queste dataclass sono usate da:
- lettura_excel.py (per costruire gli oggetti dai fogli)
- config.py (unisci_config, carica_config)
- generatore_agenda.py, generatore_pdf.py (per consumare i dati)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

# ======================================================================
# DATACLASS
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
