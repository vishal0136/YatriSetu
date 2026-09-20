from validation.rules.validate_database import test_engine
from sqlalchemy import text

with test_engine.connect() as conn:
    result = conn.execute(
        text("""
            SELECT
                route_id,
                COUNT(*) AS trip_count,
                COUNT(DISTINCT shape_id) AS distinct_shapes
            FROM trips
            WHERE shape_id IS NOT NULL
            GROUP BY route_id
            HAVING COUNT(DISTINCT shape_id) > 1
            ORDER BY distinct_shapes DESC, route_id
        """)
    )

    print("ROUTES WITH MULTIPLE SHAPES:")
    rows = result.fetchall()
    print("Total routes:", len(rows))

    for row in rows:
        print(row)
