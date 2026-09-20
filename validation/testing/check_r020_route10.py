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
            WHERE route_id = '10'
            GROUP BY route_id
        """)
    )

    print("ROUTE 10 PROFILE:")
    print(result.fetchone())

    result = conn.execute(
        text("""
            SELECT trip_id, route_id, shape_id
            FROM trips
            WHERE route_id = '10'
            LIMIT 20
        """)
    )

    print("\nROUTE 10 TRIPS:")
    for row in result:
        print(row)
