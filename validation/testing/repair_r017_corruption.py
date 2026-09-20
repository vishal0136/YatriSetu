from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def repair_r017_corruption():
    print("Starting R017 controlled repair...")

    with test_engine.begin() as connection:

        result = connection.execute(
            text("""
                SELECT service_id, start_date, end_date
                FROM calendar
                WHERE service_id = :service_id
            """),
            {"service_id": "1"},
        ).fetchone()

        if result is None:
            print("Corrupted R017 record was not found.")
            return

        service_id, current_start, current_end = result

        print("Database: DTMS_TEST")
        print("Service ID:", service_id)
        print("Current start_date:", current_start)
        print("Current end_date:", current_end)

        connection.execute(
            text("""
                UPDATE calendar
                SET start_date = :original_start,
                    end_date = :original_end
                WHERE service_id = :service_id
            """),
            {
                "service_id": service_id,
                "original_start": "2025-01-01",
                "original_end": "2040-01-01",
            },
        )

        print("\nR017 repair completed successfully.")
        print("Restored start_date: 2025-01-01")
        print("Restored end_date: 2040-01-01")


if __name__ == "__main__":
    repair_r017_corruption()