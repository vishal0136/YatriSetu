from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def repair_r016_corruption():
    print("Starting R016 controlled repair...")

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
            print("Corrupted R016 record was not found.")
            return

        trip_id, sequence, current_arrival, current_departure = result

        print("Database: DTMS_TEST")
        print("Trip ID:", trip_id)
        print("Stop sequence:", sequence)
        print("Current arrival_time:", current_arrival)
        print("Current departure_time:", current_departure)

        connection.execute(
            text("""
                UPDATE stop_times
                SET departure_time = :original_departure
                WHERE trip_id = :trip_id
                  AND stop_sequence = :sequence
            """),
            {
                "trip_id": trip_id,
                "sequence": sequence,
                "original_departure": 22406,
            },
        )

        print("\nR016 repair completed successfully.")
        print("Restored departure_time: 22406")
        print("Arrival_time unchanged:", current_arrival)


if __name__ == "__main__":
    repair_r016_corruption()