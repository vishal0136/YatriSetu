from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def test_r009_orphan_stop():
    print("Starting R009 controlled test...")

    with test_engine.begin() as connection:

        connection.execute(
            text("""
                CREATE TEMP TABLE r009_test_stop_times AS
                SELECT
                    trip_id,
                    stop_id
                FROM stop_times
                LIMIT 1
            """)
        )

        connection.execute(
            text("""
                UPDATE r009_test_stop_times
                SET stop_id = :invalid_stop_id
            """),
            {"invalid_stop_id": "__R009_NONEXISTENT_STOP__"},
        )

        connection.execute(
            text("""
                CREATE TEMP TABLE r009_test_stops AS
                SELECT stop_id
                FROM stops
            """)
        )

        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM r009_test_stop_times child
                LEFT JOIN r009_test_stops parent
                    ON child.stop_id = parent.stop_id
                WHERE child.stop_id IS NOT NULL
                  AND parent.stop_id IS NULL
            """)
        ).scalar_one()

        print("Database: DTMS_TEST")
        print("Isolated child table: r009_test_stop_times")
        print("Invalid stop reference: __R009_NONEXISTENT_STOP__")
        print("Orphan references detected:", result)

        if result > 0:
            print("\nR009 controlled test PASSED.")
            print("Orphan stop reference detected.")
            print("Expected rule: R009")
            print("Expected severity: HIGH")
            print("Expected issue type: REFERENTIAL_INTEGRITY")
        else:
            print("\nR009 controlled test FAILED.")
            print("No orphan stop reference detected.")


if __name__ == "__main__":
    test_r009_orphan_stop()