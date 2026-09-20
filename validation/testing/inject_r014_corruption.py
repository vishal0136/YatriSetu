from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def inject_r014_corruption():
    print("Starting R014 controlled corruption...")

    with test_engine.begin() as connection:

        result = connection.execute(
            text("""
                SELECT trip_id, stop_sequence
                FROM stop_times
                WHERE trip_id = :trip_id
                  AND stop_sequence = :sequence
            """),
            {
                "trip_id": "1_06_05",
                "sequence": 5,
            },
        ).fetchone()

        if result is None:
            print("Target stop_times record was not found.")
            return

        trip_id, original_sequence = result

        print("Database: DTMS_TEST")
        print("Trip ID:", trip_id)
        print("Original stop_sequence:", original_sequence)

        connection.execute(
            text("""
                UPDATE stop_times
                SET stop_sequence = :corrupted_sequence
                WHERE trip_id = :trip_id
                  AND stop_sequence = :original_sequence
            """),
            {
                "trip_id": trip_id,
                "original_sequence": original_sequence,
                "corrupted_sequence": -1,
            },
        )

        print("\nR014 corruption injected successfully.")
        print("Trip ID:", trip_id)
        print("Original stop_sequence:", original_sequence)
        print("Test stop_sequence: -1")
        print("Expected rule: R014")
        print("Expected severity: HIGH")
        print("Expected issue type: TIMETABLE")


if __name__ == "__main__":
    inject_r014_corruption()