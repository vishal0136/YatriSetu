from sqlalchemy import text
from sqlalchemy.engine import Engine

from scripts.db_connection import engine


def get_stop_evidence(
    stop_id: str,
    db_engine: Engine = engine,
) -> dict | None:

    query = text("""
        SELECT
            stop_id,
            stop_code,
            stop_name,
            stop_lat,
            stop_lon
        FROM stops
        WHERE stop_id = :stop_id
    """)

    with db_engine.connect() as connection:
        row = connection.execute(
            query,
            {"stop_id": stop_id}
        ).mappings().first()

    if row is None:
        return None

    return dict(row)


if __name__ == "__main__":
    evidence = get_stop_evidence("1")

    print("DB Evidence Service")
    print("Evidence:", evidence)
