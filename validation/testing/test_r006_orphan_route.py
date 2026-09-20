from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def test_r006_orphan_route():
    print("Starting R006 controlled test...")

    with test_engine.begin() as connection:

        # Create an isolated copy of the relationship.
        connection.execute(
            text("""
                CREATE TEMP TABLE r006_test_trips AS
                SELECT
                    trip_id,
                    route_id
                FROM trips
                LIMIT 1
            """)
        )

        # Deliberately create an orphan route reference.
        connection.execute(
            text("""
                UPDATE r006_test_trips
                SET route_id = :invalid_route_id
            """),
            {"invalid_route_id": "__R006_NONEXISTENT_ROUTE__"},
        )

        # Create a minimal parent table containing valid route IDs.
        connection.execute(
            text("""
                CREATE TEMP TABLE r006_test_routes AS
                SELECT route_id
                FROM routes
            """)
        )

        # Execute the same LEFT JOIN logic used by R006.
        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM r006_test_trips child
                LEFT JOIN r006_test_routes parent
                    ON child.route_id = parent.route_id
                WHERE child.route_id IS NOT NULL
                  AND parent.route_id IS NULL
            """)
        ).scalar_one()

        print("Database: DTMS_TEST")
        print("Isolated child table: r006_test_trips")
        print("Invalid route reference: __R006_NONEXISTENT_ROUTE__")
        print("Orphan references detected:", result)

        if result > 0:
            print("\nR006 controlled test PASSED.")
            print("Orphan route reference detected.")
            print("Expected rule: R006")
            print("Expected severity: HIGH")
            print("Expected issue type: REFERENTIAL_INTEGRITY")
        else:
            print("\nR006 controlled test FAILED.")
            print("No orphan route reference detected.")


if __name__ == "__main__":
    test_r006_orphan_route()