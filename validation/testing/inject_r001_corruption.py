from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def inject_r001_corruption():
    print("Starting R001 controlled corruption...")

    with test_engine.begin() as connection:

        result = connection.execute(
            text("""
                SELECT service_id, start_date
                FROM calendar
                LIMIT 1
            """)
        ).fetchone()

        if result is None:
            print("No calendar record found.")
            return

        service_id, original_start_date = result

        print("Database: DTMS_TEST")
        print("Service ID:", service_id)
        print("Original start_date:", original_start_date)

        connection.execute(
            text("""
                UPDATE calendar
                SET start_date = NULL
                WHERE service_id = :service_id
            """),
            {"service_id": service_id},
        )

        print("\nR001 corruption injected successfully.")
        print("Service ID:", service_id)
        print("Corrupted start_date: NULL")
        print("Expected rule: R001")
        print("Expected severity: HIGH")
        print("Expected issue type: COMPLETENESS")


if __name__ == "__main__":
    inject_r001_corruption()