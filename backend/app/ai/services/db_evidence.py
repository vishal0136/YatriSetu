import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL

load_dotenv()


def create_test_engine() -> Engine:
    """Create an engine explicitly connected to DTMS_TEST."""

    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    test_db_name = os.getenv("TEST_DB_NAME", "DTMS_TEST")

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=db_user,
        password=db_password,
        host=db_host,
        port=int(db_port),
        database=test_db_name,
    )

    return create_engine(database_url)


def get_stop_evidence(
    stop_id: str,
    db_engine: Engine | None = None,
) -> dict | None:
    """
    Read-only evidence retrieval for a stop.

    This function performs SELECT only.
    It does not modify the database.
    """

    if db_engine is None:
        db_engine = create_test_engine()

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
            {"stop_id": stop_id},
        ).mappings().first()

    if row is None:
        return None

    return dict(row)


if __name__ == "__main__":
    evidence = get_stop_evidence("1")

    print("=== DB EVIDENCE SERVICE ===")
    print("Database: DTMS_TEST")
    print("Operation: READ ONLY")
    print("Evidence:", evidence)
