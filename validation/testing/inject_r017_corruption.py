from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def inject_r017_corruption():
    print("Starting R017 controlled corruption...")

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
            print("Target calendar record was not found.")
            return

        service_id, original_start, original_end = result

        print("Database: DTMS_TEST")
        print("Service ID:", service_id)
        print("Original start_date:", original_start)
        print("Original end_date:", original_end)

        connection.execute(
            text("""
                UPDATE calendar
                SET start_date = :new_start,
                    end_date = :new_end
                WHERE service_id = :service_id
            """),
            {
                "service_id": service_id,
                "new_start": original_end,
                "new_end": original_start,
            },
        )

        print("\nR017 corruption injected successfully.")
        print("Service ID:", service_id)
        print("Test start_date:", original_end)
        print("Test end_date:", original_start)
        print("Expected condition: start_date > end_date")
        print("Expected rule: R017")
        print("Expected severity: MEDIUM")
        print("Expected issue type: SERVICE")


if __name__ == "__main__":
    inject_r017_corruption()