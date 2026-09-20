from validation.rules.validate_database import test_engine
from sqlalchemy import text

with test_engine.connect() as conn:
    result = conn.execute(
        text("""
            SELECT
                route_id,
                shape_id,
                COUNT(*) AS trip_count
            FROM trips
            WHERE route_id = '10'
            GROUP BY route_id, shape_id
            ORDER BY shape_id
        """)
    )

    print("ROUTE 10 SHAPE DISTRIBUTION:")
    for row in result:
        print(row)
