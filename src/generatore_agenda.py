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
from datetime import date, timedelta

from calcolo_liturgico import calcola_corpus_domini, calcola_tutte_date_mobili
from config import carica_config
from dataclass_config import Config, Intenzione, Matrimonio, Periodo, Ricorrenza
from util import formatta_data_italiana

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
    intervallo contiene la data.

    Gestione periodi a cavallo d'anno:
    Se un periodo ha `dal` > `al` (es. 01/10/2027 → 30/04/2028),
    significa che attraversa il capodanno. In quel caso:
    - Se data >= dal (dopo l'inizio) → matcha
    - Se data <= al (prima della fine) → matcha

    Args:
        data: data da verificare
        config: Config con la lista periodi

    Returns:
        Il Periodo attivo, o None se nessuno matcha (con warning).
    """
    for periodo in config.periodi:
        if _data_in_periodo(data, periodo):
            return periodo

    logger.warning(
        "Nessun periodo trovato per la data %s. Possibile buco nella configurazione.",
        data,
    )
    return None


def _data_in_periodo(data: date, periodo: Periodo) -> bool:
    """Verifica se una data è compresa in un periodo.

    Il confronto avviene su MESE e GIORNO, non sull'anno: così i periodi
    "ciclici" (es. inverno 01/10 → 30/04) funzionano per qualsiasi anno.

    Gestisce anche i periodi a cavallo d'anno:
    - Periodo normale (dal <= al in mese/giorno), es. 01/05 → 31/05
    - Periodo a cavallo d'anno (dal > al), es. 01/10 → 30/04

    Args:
        data: data da verificare
        periodo: il Periodo

    Returns:
        True se la data è nel periodo.
    """
    # Estrai mese/giorno dalla data e dal periodo
    m_data, g_data = data.month, data.day
    m_dal, g_dal = periodo.dal.month, periodo.dal.day
    m_al, g_al = periodo.al.month, periodo.al.day

    # Caso 1: periodo normale (dal <= al in mese/giorno)
    # Es. 01/05 → 31/05: (5,1) <= (5,31) → normale
    if (m_dal, g_dal) <= (m_al, g_al):
        return bool((m_dal, g_dal) <= (m_data, g_data) <= (m_al, g_al))

    # Caso 2: periodo a cavallo d'anno (dal > al in mese/giorno)
    # Es. 01/10 → 30/04: (10,1) > (4,30) → a cavallo
    # Vale per: data >= dal (ottobre-dicembre) OPPURE data <= al (gennaio-aprile)
    return bool((m_data, g_data) >= (m_dal, g_dal) or (m_data, g_data) <= (m_al, g_al))


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


def _ricorrenza_per_data(data: date, config: Config) -> Ricorrenza | None:
    """Trova la ricorrenza propria attiva in una data.

    Una ricorrenza è attiva se data è compresa tra data_inizio e data_fine
    (o solo data_inizio se data_fine è None).

    Args:
        data: data da verificare
        config: Config con ricorrenze_proprie

    Returns:
        La Ricorrenza attiva, o None se nessuna matcha.
    """
    for ricorrenza in config.ricorrenze_proprie:
        inizio = ricorrenza.data_inizio
        fine = ricorrenza.data_fine or ricorrenza.data_inizio
        if inizio <= data <= fine:
            return ricorrenza
    return None


def festivita_del_giorno(
    data: date,
    config: Config,
    date_mobili: dict[str, date | list[date]],
) -> dict:
    """Determina nome, particolare e tipo_override per un giorno.

    Priorità:
    1. Se è una ricorrenza propria (es. San Salvatore) → particolare=True
    2. Se è una celebrazione mobile (es. Palme, Ascensione) → nome dalla lista
    3. Altrimenti → nome=None, particolare=False

    Args:
        data: data del giorno
        config: Config con ricorrenze_proprie
        date_mobili: dizionario da calcola_tutte_date_mobili()

    Returns:
        Dizionario con chiavi:
        - nome: str | None — nome della festività
        - particolare: bool — True se è una celebrazione particolare
        - tipo_override: str | None — per ora sempre None
    """
    # 1. Ricorrenze proprie
    ricorrenza = _ricorrenza_per_data(data, config)
    if ricorrenza is not None:
        return {
            "nome": ricorrenza.nome,
            "particolare": True,
            "tipo_override": None,
        }

    # 2. Celebrazioni mobili (singole, non liste)
    chiavi_singole = [
        "pasqua",
        "mercoledi_ceneri",
        "domenica_palme",
        "giovedi_santo",
        "venerdi_santo",
        "sabato_santo",
        "lunedi_angelo",
        "ascensione",
        "pentecoste",
        "trinita",
        "corpus_domini",
        "festa_voto",
    ]

    for chiave in chiavi_singole:
        valore = date_mobili.get(chiave)
        if isinstance(valore, date) and data == valore:
            nome = _nome_celebrazione_mobile(chiave)
            return {
                "nome": nome,
                "particolare": False,
                "tipo_override": None,
            }

    # 3. Nessuna festività specifica
    return {
        "nome": None,
        "particolare": False,
        "tipo_override": None,
    }


def _nome_celebrazione_mobile(chiave: str) -> str:
    """Mappa una chiave di date_mobili al nome leggibile.

    Args:
        chiave: chiave del dizionario date_mobili

    Returns:
        Nome leggibile della celebrazione.
    """
    mapping = {
        "pasqua": "Pasqua",
        "mercoledi_ceneri": "Mercoledì delle Ceneri",
        "domenica_palme": "Domenica delle Palme",
        "giovedi_santo": "Giovedì Santo",
        "venerdi_santo": "Venerdì Santo",
        "sabato_santo": "Sabato Santo",
        "lunedi_angelo": "Lunedì dell'Angelo",
        "ascensione": "Ascensione",
        "pentecoste": "Pentecoste",
        "trinita": "Santissima Trinità",
        "corpus_domini": "Corpus Domini",
        "festa_voto": "Festa del Voto",
    }
    return mapping.get(chiave, chiave)


# ======================================================================
# COLLEGAMENTO DATI CONFIG → GIORNI
# ======================================================================


def intenzioni_del_giorno(data: date, config: Config) -> list[Intenzione]:
    """Restituisce le intenzioni applicate in una data.

    Cerca tra config.intenzioni quelle con data_applicazione == data.

    Args:
        data: data del giorno
        config: Config con la lista intenzioni

    Returns:
        Lista di Intenzione applicate in quel giorno.
    """
    return [i for i in config.intenzioni if i.data_applicazione == data]


def matrimoni_del_giorno(data: date, config: Config) -> list[Matrimonio]:
    """Restituisce i matrimoni previsti in una data.

    Cerca tra config.matrimoni_prenotati quelli con data == data.

    Args:
        data: data del giorno
        config: Config con la lista matrimoni_prenotati

    Returns:
        Lista di Matrimonio previsti in quel giorno.
    """
    return [m for m in config.matrimoni_prenotati if m.data == data]


def note_del_giorno(data: date, config: Config) -> list[dict]:
    """Restituisce le note attive in una data.

    Una nota è attiva se dal <= data <= al.

    Args:
        data: data del giorno
        config: Config con la lista note_annuali

    Returns:
        Lista di note attive in quel giorno.
    """
    note_attive: list[dict] = []
    for nota in config.note_annuali:
        dal = nota["dal"]
        al = nota["al"]
        if dal <= data <= al:
            note_attive.append(nota)
    return note_attive


# ======================================================================
# API PUBBLICA
# ======================================================================


def genera_agenda(config: Config) -> CalendarioAgenda:
    """Genera il calendario completo dell'agenda.

    Itera su tutti i giorni dell'anno (1 gennaio → 31 dicembre) e per
    ciascuno determina tipo, nome, orari, eccezioni e collega i dati
    (intenzioni, matrimoni, note).

    Args:
        config: Config caricata (con anno, periodi, festivi, ricorrenze, ecc.)

    Returns:
        CalendarioAgenda completo con tutti i giorni dell'anno.
    """
    anno = config.anno
    logger.info("Generazione agenda per l'anno %d", anno)

    # Calcola le date mobili una sola volta
    date_mobili = calcola_tutte_date_mobili(anno)

    # Itera su tutti i giorni dell'anno
    inizio = date(anno, 1, 1)
    fine = date(anno, 12, 31)

    giorni: list[GiornoAgenda] = []
    corrente = inizio
    while corrente <= fine:
        giorno = _crea_giorno_agenda(corrente, config, date_mobili)
        giorni.append(giorno)
        corrente += timedelta(days=1)

    logger.info("Generati %d giorni", len(giorni))
    return CalendarioAgenda(anno=anno, config=config, giorni=giorni)


def _crea_giorno_agenda(
    data: date,
    config: Config,
    date_mobili: dict[str, date | list[date]],
) -> GiornoAgenda:
    """Crea un GiornoAgenda completo per una data.

    Args:
        data: data del giorno
        config: Config
        date_mobili: date mobili calcolate

    Returns:
        GiornoAgenda completo.
    """
    # 1. Tipo e nome dai festivi fissi (base)
    tipo, nome_festivo = determina_tipo_giorno(data, config)

    # 2. Festività (ricorrenze proprie + celebrazioni mobili)
    info_festivita = festivita_del_giorno(data, config, date_mobili)

    # 3. Merge nome: festivo fisso vince, altrimenti ricorrenza/mobile
    nome_finale = nome_festivo or info_festivita["nome"]

    # 4. Orari base (da periodo attivo, in base a tipo)
    orari = orari_per_giorno(data, tipo, config)

    # 5. Applica eccezioni (orari ridotti, salta se domenica)
    orari = applica_eccezioni_orari(data, orari, config)

    # 6. Applica divieti pomeridiani (Assunta, San Nicola, Corpus Domini)
    orari = applica_divieti_pomeridiani(data, orari, config)

    # 7. Collega dati
    intenzioni = intenzioni_del_giorno(data, config)
    matrimoni = matrimoni_del_giorno(data, config)
    note = note_del_giorno(data, config)

    return GiornoAgenda(
        data=data,
        tipo=tipo,
        nome=nome_finale,
        particolare=info_festivita["particolare"],
        orari=orari,
        intenzioni=intenzioni,
        matrimoni=matrimoni,
        note=note,
    )


def genera_agenda_da_profilo(profilo: str) -> CalendarioAgenda:
    """Wrapper: carica la Config da un profilo e genera l'agenda.

    Args:
        profilo: nome del profilo (es. "san_pietro_in_silki")

    Returns:
        CalendarioAgenda completo.

    Raises:
        FileNotFoundError: se il profilo o i file non esistono
        ValueError: se i file sono malformati
    """
    config = carica_config(profilo)
    return genera_agenda(config)


def matrimoni_futuri(config: Config) -> list[dict]:
    """Restituisce i matrimoni prenotati per gli anni successivi.

    Filtra `config.matrimoni_prenotati` tenendo solo quelli con anno
    strettamente maggiore dell'anno dell'agenda (config.anno).

    Ogni matrimonio è restituito come dict con i campi:
    - data: date
    - data_formattata: str (formato italiano, es. "15 giugno 2028")
    - ora: str
    - nome_sposi: str

    Args:
        config: Config con anno e matrimoni_prenotati

    Returns:
        Lista di dict ordinati per data crescente.
    """
    anno_agenda = config.anno
    futuri: list[dict] = []

    for m in config.matrimoni_prenotati:
        if m.data is None:
            continue
        if m.data.year > anno_agenda:
            futuri.append(
                {
                    "data": m.data,
                    "data_formattata": formatta_data_italiana(m.data),
                    "ora": m.ora,
                    "nome_sposi": m.nome_sposi,
                }
            )

    # Ordina per data crescente
    futuri.sort(key=lambda x: x["data"])

    return futuri
