import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.extract.fetch_fx_rate import fetch_fx_rate
from src.load.load_fx_rate import save_fx_rate, validate
from src.notify import ping_heartbeat, send_telegram

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
    return data


if __name__ == "__main__":
    try:
        result = run()
    except Exception as error:
        logger.exception("Pipeline failed")
        send_telegram(
            f"Pipeline FAILED ({type(error).__name__}). Check logs/pipeline.log"
        )
        ping_heartbeat("/fail")
        raise
    else:
        send_telegram(
            f"Pipeline OK: 1 USD = {result['rate']} IDR on {result['date']}"
        )
        ping_heartbeat()