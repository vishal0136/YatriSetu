from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def test_r003_duplicate_records():
    print("Starting R003 controlled test...")

    with test_engine.begin() as connection:

        # Create an isolated temporary table with the same
        # columns used by the R003 stops check.
        connection.execute(
            text("""
                CREATE TEMP TABLE r003_test_stops AS
                SELECT
                    stop_id,
                    stop_code,
                    stop_name,
                    stop_lat,
                    stop_lon
                FROM stops
                LIMIT 1
            """)
        )

        # Insert an exact duplicate of the existing record.
        connection.execute(
            text("""
                INSERT INTO r003_test_stops (
                    stop_id,
                    stop_code,
                    stop_name,
                    stop_lat,
                    stop_lon
                )
                SELECT
                    stop_id,
                    stop_code,
                    stop_name,
                    stop_lat,
                    stop_lon
                FROM r003_test_stops
            """)
        )

        # Execute the same duplicate-record logic used by R003.
        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM (
                    SELECT
                        stop_id,
                        stop_code,
                        stop_name,
                        stop_lat,
                        stop_lon
                    FROM r003_test_stops
                    GROUP BY
                        stop_id,
                        stop_code,
                        stop_name,
                        stop_lat,
                        stop_lon
                    HAVING COUNT(*) > 1
                ) duplicates
            """)
        ).scalar_one()

        print("Database: DTMS_TEST")
        print("Isolated table: r003_test_stops")
        print("Duplicate groups detected:", result)

        if result > 0:
            print("\nR003 controlled test PASSED.")
            print("Duplicate complete record detected.")
            print("Expected rule: R003")
            print("Expected severity: MEDIUM")
            print("Expected issue type: UNIQUENESS")
        else:
            print("\nR003 controlled test FAILED.")
            print("No duplicate complete record detected.")


if __name__ == "__main__":
    test_r003_duplicate_records()