from validation.rules.validate_database import test_engine
from sqlalchemy import text

with test_engine.connect() as conn:
    result = conn.execute(
        text("""
            SELECT trip_id, direction_id
            FROM trips
            WHERE trip_id = '10_07_45'
        """)
    )

    print("R023 TARGET:")
    print(result.fetchone())
