from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def inject_r002_corruption():
    print("Starting R002 controlled corruption...")

    with test_engine.begin() as connection:

        # Create an isolated copy containing duplicate keys.
        connection.execute(
            text("""
                DROP TABLE IF EXISTS r002_test_stops;

                CREATE TEMP TABLE r002_test_stops AS
                SELECT stop_id, stop_name
                FROM stops
                LIMIT 2
            """)
        )

        # Duplicate the first stop deliberately.
        connection.execute(
            text("""
                INSERT INTO r002_test_stops (stop_id, stop_name)
                SELECT stop_id, stop_name
                FROM r002_test_stops
                LIMIT 1
            """)
        )

        result = connection.execute(
            text("""
                SELECT stop_id, COUNT(*) AS duplicate_count
                FROM r002_test_stops
                GROUP BY stop_id
                HAVING COUNT(*) > 1
            """)
        ).fetchone()

        if result is None:
            print("R002 test duplicate was not created.")
            return

        stop_id, duplicate_count = result

        print("Database: DTMS_TEST")
        print("Isolated test table: r002_test_stops")
        print("Duplicate stop_id:", stop_id)
        print("Duplicate count:", duplicate_count)
        print("\nR002 controlled duplicate created successfully.")
        print("Expected rule: R002")
        print("Expected severity: HIGH")
        print("Expected issue type: UNIQUENESS")


if __name__ == "__main__":
    inject_r002_corruption()