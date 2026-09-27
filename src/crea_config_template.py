"""
Generatore del file config.xlsx per il progetto Agenda Parrocchiale.

Crea un file Excel con 4 fogli (Impostazioni, Intenzioni, Matrimoni, Note),
celle gialle compilabili, formule, formattazione e protezione senza password.

Include backup automatico e possibilità di ripristino.

Uso:
    # Genera template + profilo
    python src/crea_config_template.py --profilo san_pietro_in_silki

    # Salta la conferma se il file esiste (con backup silenzioso)
    python src/crea_config_template.py --profilo san_pietro_in_silki --force

    # Elenca i backup disponibili
    python src/crea_config_template.py --profilo san_pietro_in_silki --lista-backup

    # Ripristina l'ultimo backup
    python src/crea_config_template.py --profilo san_pietro_in_silki --ripristina

    # Ripristina un backup specifico
    python src/crea_config_template.py --profilo san_pietro_in_silki --ripristina 2026-09-26_11-30
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import cast

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from fogli_excel import (
    crea_foglio_impostazioni,
    crea_foglio_intenzioni,
    crea_foglio_matrimoni,
    crea_foglio_note,
)
from lettura_config import leggi_yaml
from util import configura_logging, mostra_riepilogo_warning

# ----------------------------------------------------------------------
# COSTANTI GLOBALI
# ----------------------------------------------------------------------

ROOT_PROGETTO = Path(__file__).resolve().parent.parent
CARTELLA_CONFIGS = ROOT_PROGETTO / "configs"
NOME_FILE_CONFIG = "config.xlsx"
NOME_CARTELLA_BACKUP = ".backup"

# ----------------------------------------------------------------------
# BACKUP E RIPRISTINO
# ----------------------------------------------------------------------


def cartella_backup(profilo_dir: Path) -> Path:
    """Restituisce il percorso della cartella .backup del profilo."""
    return profilo_dir / NOME_CARTELLA_BACKUP


def crea_backup(profilo_dir: Path) -> Path | None:
    """Crea un backup timestampato del config.xlsx esistente.

    Returns:
        Il percorso del backup creato, o None se non c'era nulla da salvare.
    """
    file_config = profilo_dir / NOME_FILE_CONFIG
    if not file_config.exists():
        return None

    backup_dir = cartella_backup(profilo_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    percorso_backup = backup_dir / f"config_{timestamp}.xlsx"

    shutil.copy2(file_config, percorso_backup)
    return percorso_backup


def lista_backup(profilo_dir: Path) -> list[Path]:
    """Restituisce la lista dei backup disponibili, ordinati dal più recente."""
    backup_dir = cartella_backup(profilo_dir)
    if not backup_dir.exists():
        return []

    backups = sorted(
        backup_dir.glob("config_*.xlsx"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return backups


def ripristina_backup(profilo_dir: Path, timestamp: str | None = None) -> Path | None:
    """Ripristina un backup come config.xlsx.

    Args:
        profilo_dir: cartella del profilo
        timestamp: stringa timestamp (senza prefisso "config_" né estensione).
                   Se None, ripristina il backup più recente.

    Returns:
        Il percorso del file ripristinato, o None se non c'era nulla.
    """
    backups = lista_backup(profilo_dir)
    if not backups:
        return None

    if timestamp:
        # Cerca il backup che contiene il timestamp specificato
        candidati = [b for b in backups if timestamp in b.name]
        if not candidati:
            print(f"❌ Nessun backup trovato per timestamp: {timestamp}")
            return None
        backup_scelto = candidati[0]
    else:
        backup_scelto = backups[0]

    # Backup del file attuale PRIMA di sovrascrivere (per non perdere nulla)
    crea_backup(profilo_dir)

    # Copia il backup scelto come config.xlsx attivo
    destinazione = profilo_dir / NOME_FILE_CONFIG
    shutil.copy2(backup_scelto, destinazione)
    return destinazione


# ----------------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ----------------------------------------------------------------------


def crea_config(
    destinazione: Path,
    anno: int = 2027,
    nome_parrocchia: str = "Nome Parrocchia",
    citta: str = "Città",
) -> Path:
    wb = Workbook()
    # Il Workbook appena creato ha sempre un foglio attivo.
    # Cast esplicito per mypy (wb.active è tipizzato come Optional).
    foglio_default = cast(Worksheet, wb.active)
    wb.remove(foglio_default)

    crea_foglio_impostazioni(wb, anno, nome_parrocchia, citta)
    crea_foglio_intenzioni(wb)
    crea_foglio_matrimoni(wb)
    crea_foglio_note(wb)

    destinazione.mkdir(parents=True, exist_ok=True)
    percorso_file = destinazione / NOME_FILE_CONFIG
    wb.save(percorso_file)
    return percorso_file


def chiedi_conferma_sovrascrittura(profilo_dir: Path) -> bool:
    """Chiede conferma all'utente se il file esiste già."""
    file_config = profilo_dir / NOME_FILE_CONFIG
    if not file_config.exists():
        return True

    print(f"\n⚠️  Il file {file_config} esiste già.")
    print("    Se continui, verrà creato un backup e il file sarà sovrascritto.")
    risposta = input("    Vuoi procedere? [y/N]: ").strip().lower()
    return risposta in ("y", "yes", "s", "si", "sì")


def main() -> None:
    # Configura il logging e ottieni il collector dei warning
    collector = configura_logging()

    parser = argparse.ArgumentParser(
        description="Genera il template config.xlsx con backup automatico.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--profilo",
        type=str,
        default=None,
        help="Nome del profilo (es. san_pietro_in_silki). Se omesso, genera solo il template.",
    )
    parser.add_argument(
        "--anno",
        type=int,
        default=datetime.now().year,
        help="Anno dell'agenda (default: anno corrente).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Salta la conferma interattiva se il file esiste (crea comunque il backup).",
    )
    parser.add_argument(
        "--lista-backup",
        action="store_true",
        help="Elenca i backup disponibili per il profilo specificato.",
    )
    parser.add_argument(
        "--ripristina",
        nargs="?",
        const="",
        default=None,
        metavar="TIMESTAMP",
        help="Ripristina un backup (l'ultimo se TIMESTAMP è omesso).",
    )
    args = parser.parse_args()

    # --- Gestione comandi backup ---
    if args.profilo and (args.lista_backup or args.ripristina is not None):
        profilo_dir = CARTELLA_CONFIGS / args.profilo
        if not profilo_dir.exists():
            print(f"❌ Profilo non trovato: {profilo_dir}")
            sys.exit(1)

        if args.lista_backup:
            backups = lista_backup(profilo_dir)
            if not backups:
                print(f"ℹ️  Nessun backup disponibile per {args.profilo}.")
                return
            print(f"\n📦 Backup disponibili per {args.profilo} ({len(backups)}):\n")
            for i, b in enumerate(backups, start=1):
                data_mod = datetime.fromtimestamp(b.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                print(f"  {i}. {b.name}   ({data_mod})")
            print()
            return

        if args.ripristina is not None:
            timestamp = args.ripristina if args.ripristina else None
            risultato = ripristina_backup(profilo_dir, timestamp)
            if risultato:
                print(f"✅ Ripristinato: {risultato}")
            else:
                print("❌ Ripristino non riuscito (nessun backup trovato).")
            return

    # --- Generazione normale ---
    # 1. Template vuoto (sempre, senza chiedere conferma)
    template_dir = CARTELLA_CONFIGS / "_template"
    percorso_template = crea_config(
        template_dir,
        anno=args.anno,
        nome_parrocchia="Nome Parrocchia",
        citta="Città",
    )
    print(f"✅ Template generato: {percorso_template}")

    # 2. Profilo specifico
    if args.profilo:
        profilo_dir = CARTELLA_CONFIGS / args.profilo

        # Conferma se il file esiste già
        if not args.force:
            if not chiedi_conferma_sovrascrittura(profilo_dir):
                print("⏹️  Operazione annullata.")
                return

        # Backup automatico se il file esiste
        backup = crea_backup(profilo_dir)
        if backup:
            print(f"📦 Backup creato: {backup.relative_to(ROOT_PROGETTO)}")

        # Leggi i dati del profilo dalle regole.yaml
        percorso_regole = profilo_dir / "regole.yaml"
        if not percorso_regole.exists():
            print(f"❌ File {percorso_regole} non trovato.")
            sys.exit(1)

        dati_yaml = leggi_yaml(percorso_regole)
        nome_parrocchia = dati_yaml.get("nome_parrocchia", "Nome Parrocchia")
        citta = dati_yaml.get("citta", "Città")

        # Genera il nuovo file
        percorso_profilo = crea_config(
            profilo_dir,
            anno=args.anno,
            nome_parrocchia=nome_parrocchia,
            citta=citta,
        )
        print(f"✅ Profilo generato: {percorso_profilo}")

    # --- Riepilogo warning finale ---
    # (Per ora il collector è sempre vuoto perché nessuna funzione di questo
    #  script emette warning. Ma il pattern è coerente con gli altri script.)
    if not mostra_riepilogo_warning(collector):
        print("⏹️  Operazione annullata dall'utente.")
        sys.exit(1)
