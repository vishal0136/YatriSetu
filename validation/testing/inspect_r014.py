from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


with test_engine.connect() as connection:
    rows = connection.execute(
        text("""
            SELECT trip_id, stop_sequence
            FROM stop_times
            WHERE trip_id = :trip_id
            ORDER BY stop_sequence
            LIMIT 10
        """),
        {"trip_id": "1_06_05"},
    ).fetchall()

    print("Database: DTMS_TEST")
    print("Trip ID: 1_06_05")
    print("\nStop sequences:")

    for row in rows:
        print(row)