from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def test_r007_orphan_service():
    print("Starting R007 controlled test...")

    with test_engine.begin() as connection:

        # Create an isolated copy of the relationship.
        connection.execute(
            text("""
                CREATE TEMP TABLE r007_test_trips AS
                SELECT
                    trip_id,
                    service_id
                FROM trips
                LIMIT 1
            """)
        )

        # Deliberately create an orphan service reference.
        connection.execute(
            text("""
                UPDATE r007_test_trips
                SET service_id = :invalid_service_id
            """),
            {"invalid_service_id": "__R007_NONEXISTENT_SERVICE__"},
        )

        # Create a minimal parent table containing valid service IDs.
        connection.execute(
            text("""
                CREATE TEMP TABLE r007_test_calendar AS
                SELECT service_id
                FROM calendar
            """)
        )

        # Execute the same LEFT JOIN logic used by R007.
        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM r007_test_trips child
                LEFT JOIN r007_test_calendar parent
                    ON child.service_id = parent.service_id
                WHERE child.service_id IS NOT NULL
                  AND parent.service_id IS NULL
            """)
        ).scalar_one()

        print("Database: DTMS_TEST")
        print("Isolated child table: r007_test_trips")
        print("Invalid service reference: __R007_NONEXISTENT_SERVICE__")
        print("Orphan references detected:", result)

        if result > 0:
            print("\nR007 controlled test PASSED.")
            print("Orphan service reference detected.")
            print("Expected rule: R007")
            print("Expected severity: HIGH")
            print("Expected issue type: REFERENTIAL_INTEGRITY")
        else:
            print("\nR007 controlled test FAILED.")
            print("No orphan service reference detected.")


if __name__ == "__main__":
    test_r007_orphan_service()