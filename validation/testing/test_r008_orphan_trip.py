from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def test_r008_orphan_trip():
    print("Starting R008 controlled test...")

    with test_engine.begin() as connection:

        connection.execute(
            text("""
                CREATE TEMP TABLE r008_test_stop_times AS
                SELECT
                    trip_id,
                    stop_id
                FROM stop_times
                LIMIT 1
            """)
        )

        connection.execute(
            text("""
                UPDATE r008_test_stop_times
                SET trip_id = :invalid_trip_id
            """),
            {"invalid_trip_id": "__R008_NONEXISTENT_TRIP__"},
        )

        connection.execute(
            text("""
                CREATE TEMP TABLE r008_test_trips AS
                SELECT trip_id
                FROM trips
            """)
        )

        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM r008_test_stop_times child
                LEFT JOIN r008_test_trips parent
                    ON child.trip_id = parent.trip_id
                WHERE child.trip_id IS NOT NULL
                  AND parent.trip_id IS NULL
            """)
        ).scalar_one()

        print("Database: DTMS_TEST")
        print("Isolated child table: r008_test_stop_times")
        print("Invalid trip reference: __R008_NONEXISTENT_TRIP__")
        print("Orphan references detected:", result)

        if result > 0:
            print("\nR008 controlled test PASSED.")
            print("Orphan trip reference detected.")
            print("Expected rule: R008")
            print("Expected severity: HIGH")
            print("Expected issue type: REFERENTIAL_INTEGRITY")
        else:
            print("\nR008 controlled test FAILED.")
            print("No orphan trip reference detected.")


if __name__ == "__main__":
    test_r008_orphan_trip()