import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from validation.rules.validate_database import test_engine
from sqlalchemy import text

with test_engine.connect() as conn:

    result1 = conn.execute(
        text("""
            SELECT trip_id, route_id, shape_id
            FROM trips
            WHERE trip_id = '10_07_45'
        """)
    )

    print("TARGET TRIP:")
    print(result1.fetchone())

    result2 = conn.execute(
        text("""
            SELECT trip_id, route_id, shape_id
            FROM trips
            WHERE route_id = '1'
              AND shape_id = 'shp_3_2029'
            LIMIT 3
        """)
    )

    print("\nROUTE 1 SHAPE:")
    print(result2.fetchall())
