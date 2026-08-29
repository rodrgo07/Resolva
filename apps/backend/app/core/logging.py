import logging
import logging.handlers
from app.config import settings

def setup_logging():
    logger = logging.getLogger("resolva")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler
    fh = logging.handlers.RotatingFileHandler(
        settings.LOG_FILE, maxBytes=5*1024*1024, backupCount=5
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

logger = setup_logging()
