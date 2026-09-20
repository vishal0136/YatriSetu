from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def repair_r014_corruption():
    print("Starting R014 controlled repair...")

    with test_engine.begin() as connection:

        result = connection.execute(
            text("""
                SELECT trip_id, stop_sequence
                FROM stop_times
                WHERE trip_id = :trip_id
                  AND stop_sequence = :corrupted_sequence
            """),
            {
                "trip_id": "1_06_05",
                "corrupted_sequence": -1,
            },
        ).fetchone()

        if result is None:
            print("Corrupted R014 record was not found.")
            return

        trip_id, corrupted_sequence = result

        print("Database: DTMS_TEST")
        print("Trip ID:", trip_id)
        print("Current stop_sequence:", corrupted_sequence)

        connection.execute(
            text("""
                UPDATE stop_times
                SET stop_sequence = :original_sequence
                WHERE trip_id = :trip_id
                  AND stop_sequence = :corrupted_sequence
            """),
            {
                "trip_id": trip_id,
                "corrupted_sequence": -1,
                "original_sequence": 5,
            },
        )

        print("\nR014 repair completed successfully.")
        print("Restored stop_sequence: 5")


if __name__ == "__main__":
    repair_r014_corruption()