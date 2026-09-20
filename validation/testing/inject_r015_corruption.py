from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def inject_r015_corruption():
    print("Starting R015 controlled corruption...")

    with test_engine.begin() as connection:

        result = connection.execute(
            text("""
                SELECT trip_id, stop_sequence, arrival_time, departure_time
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

        trip_id, sequence, original_arrival, original_departure = result

        print("Database: DTMS_TEST")
        print("Trip ID:", trip_id)
        print("Stop sequence:", sequence)
        print("Original arrival_time:", original_arrival)
        print("Original departure_time:", original_departure)

        connection.execute(
            text("""
                UPDATE stop_times
                SET arrival_time = :corrupted_arrival
                WHERE trip_id = :trip_id
                  AND stop_sequence = :sequence
            """),
            {
                "trip_id": trip_id,
                "sequence": sequence,
                "corrupted_arrival": -1,
            },
        )

        print("\nR015 corruption injected successfully.")
        print("Trip ID:", trip_id)
        print("Stop sequence:", sequence)
        print("Original arrival_time:", original_arrival)
        print("Test arrival_time: -1")
        print("Departure_time unchanged:", original_departure)
        print("Expected rule: R015")
        print("Expected severity: HIGH")
        print("Expected issue type: TIMETABLE")


if __name__ == "__main__":
    inject_r015_corruption()