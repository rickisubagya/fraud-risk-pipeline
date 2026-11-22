import logging
from datetime import date

from sqlalchemy import text

from src.config import get_engine

logger = logging.getLogger(__name__)

MAX_AGE_DAYS = 3
MAX_DAILY_CHANGE_PCT = 5.0

LATEST_TWO_SQL = text("""
    SELECT rate_date, rate
    FROM fx_rates
    WHERE base_currency = 'USD' AND quote_currency = 'IDR'
    ORDER BY rate_date DESC
    LIMIT 2
""")


def check_fx_quality(today=None):
    today = today or date.today()
    with get_engine().connect() as conn:
        rows = conn.execute(LATEST_TWO_SQL).fetchall()

    if not rows:
        raise ValueError("Quality check failed: fx_rates has no USD/IDR rows")

    latest_date, latest_rate = rows[0]

    age_days = (today - latest_date).days
    if age_days > MAX_AGE_DAYS:
        raise ValueError(f"Quality check failed: latest rate is {age_days} days old")

    if len(rows) == 2:
        previous_rate = rows[1][1]
        change_pct = abs(latest_rate - previous_rate) / previous_rate * 100
        if change_pct > MAX_DAILY_CHANGE_PCT:
            raise ValueError(
                f"Quality check failed: rate changed {change_pct:.2f}% in one step"
            )

    logger.info("Quality check passed: %s rate %s", latest_date, latest_rate)