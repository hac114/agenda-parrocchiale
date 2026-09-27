"""
Utility condivise del progetto Agenda Parrocchiale.

Contiene:
- Configurazione del logging standard
- Eventuali funzioni di utilità generale

Il logging è configurato una sola volta all'avvio dello script principale
(chiamando `configura_logging()`), poi ogni modulo usa:

    import logging
    logger = logging.getLogger(__name__)
"""

from __future__ import annotations

import logging

# ======================================================================
# COSTANTI
# ======================================================================

# Formato del logger (tecnico, con nome modulo e livello)
FORMATO_LOG = "[%(levelname)s] %(name)s: %(message)s"

# Data/ora nel formato del log
FORMATO_DATA = "%Y-%m-%d %H:%M:%S"

# ======================================================================
# CONFIGURAZIONE LOGGING
# ======================================================================


def configura_logging(livello: int = logging.INFO) -> None:
    """Configura il logging per tutto il progetto.

    Da chiamare UNA SOLA VOLTA all'avvio dello script principale.
    Dopo la chiamata, ogni modulo può usare:
        logger = logging.getLogger(__name__)

    Args:
        livello: livello minimo di log (default: INFO).
                 - logging.DEBUG → mostra anche debug
                 - logging.INFO → mostra info, warning, error, critical
                 - logging.WARNING → mostra solo warning e superiori
    """
    logging.basicConfig(
        level=livello,
        format=FORMATO_LOG,
        datefmt=FORMATO_DATA,
    )
