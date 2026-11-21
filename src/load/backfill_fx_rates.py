import argparse
import logging
from datetime import date, timedelta

from src.extract.fetch_fx_rate import fetch_fx_rate
from src.load.load_fx_rate import save_fx_rate, validate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def daterange(start, end):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def main(start, end):
    for day in daterange(start, end):
        data = fetch_fx_rate(day.isoformat())
        validate(data)
        save_fx_rate(data)
        logger.info(
            "Requested %s, stored date %s, rate %s", day, data["date"], data["rate"]
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Backfill USD/IDR exchange rates")
    parser.add_argument("--start", type=date.fromisoformat, required=True)
    parser.add_argument("--end", type=date.fromisoformat, default=date.today())
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.start, args.end)