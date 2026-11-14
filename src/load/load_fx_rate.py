from sqlalchemy import text

from src.config import get_engine
from src.extract.fetch_fx_rate import fetch_fx_rate

UPSERT_SQL = text("""
    INSERT INTO fx_rates (rate_date, base_currency, quote_currency, rate)
    VALUES (:rate_date, :base, :quote, :rate)
    ON CONFLICT (rate_date, base_currency, quote_currency)
    DO UPDATE SET rate = EXCLUDED.rate, fetched_at = now()
""")


def validate(data):
    required = {"date", "base", "quote", "rate"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Missing fields in API response: {missing}")
    if data["rate"] <= 0:
        raise ValueError(f"Invalid rate: {data['rate']}")


def main():
    data = fetch_fx_rate()
    validate(data)
    with get_engine().begin() as conn:
        conn.execute(
            UPSERT_SQL,
            {
                "rate_date": data["date"],
                "base": data["base"],
                "quote": data["quote"],
                "rate": data["rate"],
            },
        )
    print("Saved:", data)


if __name__ == "__main__":
    main()