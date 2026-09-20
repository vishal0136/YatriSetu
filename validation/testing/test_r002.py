from validation.rules.validate_database import test_engine
from sqlalchemy import text

with test_engine.connect() as conn:
    with conn.begin():
        conn.execute(text("""
            DROP TABLE IF EXISTS r002_test_stops;

            CREATE TEMP TABLE r002_test_stops (
                stop_id TEXT,
                stop_name TEXT
            );

            INSERT INTO r002_test_stops (stop_id, stop_name)
            VALUES
                ('TEST_R002_001', 'Test Stop A'),
                ('TEST_R002_001', 'Test Stop A');
        """))

        result = conn.execute(text("""
            SELECT COUNT(*)
            FROM (
                SELECT stop_id
                FROM r002_test_stops
                GROUP BY stop_id
                HAVING COUNT(*) > 1
            ) duplicates
        """))

        count = result.scalar_one()

        print("R002 duplicate groups detected:", count)

        if count == 1:
            print("R002 controlled test PASSED.")
        else:
            print("R002 controlled test FAILED.")
