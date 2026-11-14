import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.extract.fetch_fx_rate import fetch_fx_rate
from src.load.load_fx_rate import save_fx_rate, validate

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            LOG_DIR / "pipeline.log",
            maxBytes=1_000_000,
            backupCount=5,
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger(__name__)


def run():
    logger.info("Pipeline started")
    data = fetch_fx_rate()
    logger.info("Extracted: %s", data)
    validate(data)
    logger.info("Validation passed")
    save_fx_rate(data)
    logger.info("Pipeline finished")


if __name__ == "__main__":
    try:
        run()
    except Exception:
        logger.exception("Pipeline failed")
        raise