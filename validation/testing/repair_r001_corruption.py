from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def repair_r001_corruption():
    print("Starting R001 controlled repair...")

    with test_engine.begin() as connection:

        result = connection.execute(
            text("""
                SELECT service_id, start_date
                FROM calendar
                WHERE service_id = :service_id
            """),
            {"service_id": "1"},
        ).fetchone()

        if result is None:
            print("Service ID 1 was not found.")
            return

        service_id, current_start_date = result

        print("Database: DTMS_TEST")
        print("Service ID:", service_id)
        print("Current start_date:", current_start_date)

        connection.execute(
            text("""
                UPDATE calendar
                SET start_date = :start_date
                WHERE service_id = :service_id
            """),
            {
                "service_id": service_id,
                "start_date": "2025-01-01",
            },
        )

        print("\nR001 repair completed successfully.")
        print("Restored start_date: 2025-01-01")


if __name__ == "__main__":
    repair_r001_corruption()