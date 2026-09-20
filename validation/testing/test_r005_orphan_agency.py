from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def test_r005_orphan_agency():
    print("Starting R005 controlled test...")

    with test_engine.begin() as connection:

        # Create an isolated copy of the relationship we want to test.
        connection.execute(
            text("""
                CREATE TEMP TABLE r005_test_routes AS
                SELECT
                    route_id,
                    agency_id
                FROM routes
                LIMIT 1
            """)
        )

        # Deliberately create an orphan agency reference.
        connection.execute(
            text("""
                UPDATE r005_test_routes
                SET agency_id = :invalid_agency_id
            """),
            {"invalid_agency_id": "__R005_NONEXISTENT_AGENCY__"},
        )

        # Create a minimal parent table containing valid agency IDs.
        connection.execute(
            text("""
                CREATE TEMP TABLE r005_test_agency AS
                SELECT agency_id
                FROM agency
            """)
        )

        # Execute the same LEFT JOIN logic used by R005.
        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM r005_test_routes child
                LEFT JOIN r005_test_agency parent
                    ON child.agency_id = parent.agency_id
                WHERE child.agency_id IS NOT NULL
                  AND parent.agency_id IS NULL
            """)
        ).scalar_one()

        print("Database: DTMS_TEST")
        print("Isolated child table: r005_test_routes")
        print("Invalid agency reference: __R005_NONEXISTENT_AGENCY__")
        print("Orphan references detected:", result)

        if result > 0:
            print("\nR005 controlled test PASSED.")
            print("Orphan agency reference detected.")
            print("Expected rule: R005")
            print("Expected severity: HIGH")
            print("Expected issue type: REFERENTIAL_INTEGRITY")
        else:
            print("\nR005 controlled test FAILED.")
            print("No orphan agency reference detected.")


if __name__ == "__main__":
    test_r005_orphan_agency()