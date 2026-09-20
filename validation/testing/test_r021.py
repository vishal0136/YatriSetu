from validation.rules.validate_database import test_engine
from sqlalchemy import text

with test_engine.connect() as conn:
    with conn.begin():
        conn.execute(text("""
            CREATE TEMP TABLE r021_test_stops (
                stop_id TEXT,
                stop_name TEXT,
                stop_lat DOUBLE PRECISION,
                stop_lon DOUBLE PRECISION
            );

            INSERT INTO r021_test_stops
                (stop_id, stop_name, stop_lat, stop_lon)
            VALUES
                ('R021_001', 'Test Duplicate Stop', 28.700001, 77.100001),
                ('R021_002', 'Test Duplicate Stop', 28.700002, 77.100002);
        """))

        result = conn.execute(text("""
            SELECT COUNT(*)
            FROM (
                SELECT
                    stop_name,
                    ROUND(stop_lat::numeric, 5),
                    ROUND(stop_lon::numeric, 5),
                    COUNT(*) AS occurrences
                FROM r021_test_stops
                GROUP BY
                    stop_name,
                    ROUND(stop_lat::numeric, 5),
                    ROUND(stop_lon::numeric, 5)
                HAVING COUNT(*) > 1
            ) duplicates
        """))

        count = result.scalar_one()

        print("R021 duplicate groups detected:", count)

        if count == 1:
            print("R021 controlled test PASSED.")
        else:
            print("R021 controlled test FAILED.")
