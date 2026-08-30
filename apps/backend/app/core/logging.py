import logging
import logging.handlers
import sys
import os
from pathlib import Path
from app.config import settings

def setup_logging():
    logger = logging.getLogger("resolva")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console Handler seguro (evita crash quando executado como GUI no Windows)
    if sys.stdout is not None:
        try:
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        except Exception:
            pass

    # File Handler com diretório garantido
    try:
        log_path = Path(settings.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.handlers.RotatingFileHandler(
            str(log_path), maxBytes=5*1024*1024, backupCount=5, encoding="utf-8"
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception as e:
        # Fallback silencioso para console se arquivo falhar
        pass

    return logger

logger = setup_logging()

