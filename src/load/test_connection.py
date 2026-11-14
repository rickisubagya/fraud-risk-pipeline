from sqlalchemy import text

from src.config import get_engine

with get_engine().connect() as conn:
    print(conn.execute(text("SELECT version();")).scalar())