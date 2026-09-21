from typing import Any

from sqlalchemy import text

from scripts.db_connection import create_test_engine


def get_random_stop() -> dict[str, Any] | None:
    """
    Retrieve one random stop from the controlled DTMS_TEST database.

    READ-ONLY:
    This service performs SELECT only and cannot modify database records.
    """

    engine = create_test_engine()

    query = text("""
        SELECT
            stop_id,
            stop_code,
            stop_name,
            stop_lat,
            stop_lon
        FROM stops
        ORDER BY RANDOM()
        LIMIT 1;
    """)

    with engine.connect() as connection:
        row = connection.execute(query).mappings().first()

    return dict(row) if row else None