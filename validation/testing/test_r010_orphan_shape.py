from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def test_r010_orphan_shape():
    print("Starting R010 controlled test...")

    with test_engine.begin() as connection:

        # Create an isolated copy of the trip shape relationship.
        connection.execute(
            text("""
                CREATE TEMP TABLE r010_test_trips AS
                SELECT
                    trip_id,
                    shape_id
                FROM trips
                WHERE shape_id IS NOT NULL
                LIMIT 1
            """)
        )

        # Deliberately create an orphan shape reference.
        connection.execute(
            text("""
                UPDATE r010_test_trips
                SET shape_id = :invalid_shape_id
            """),
            {"invalid_shape_id": "__R010_NONEXISTENT_SHAPE__"},
        )

        # Execute the same DISTINCT shape_id logic used by R010.
        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM r010_test_trips t
                LEFT JOIN (
                    SELECT DISTINCT shape_id
                    FROM shapes
                ) s
                    ON t.shape_id = s.shape_id
                WHERE t.shape_id IS NOT NULL
                  AND s.shape_id IS NULL
            """)
        ).scalar_one()

        print("Database: DTMS_TEST")
        print("Isolated child table: r010_test_trips")
        print("Invalid shape reference: __R010_NONEXISTENT_SHAPE__")
        print("Orphan references detected:", result)

        if result > 0:
            print("\nR010 controlled test PASSED.")
            print("Orphan shape reference detected.")
            print("Expected rule: R010")
            print("Expected severity: HIGH")
            print("Expected issue type: REFERENTIAL_INTEGRITY")
        else:
            print("\nR010 controlled test FAILED.")
            print("No orphan shape reference detected.")


if __name__ == "__main__":
    test_r010_orphan_shape()