from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def repair_r012_corruption():
    print("Starting R012 controlled repair...")

    with test_engine.begin() as connection:

        result = connection.execute(
            text("""
                SELECT stop_id, stop_lon
                FROM stops
                WHERE stop_id = :stop_id
            """),
            {"stop_id": "1"},
        ).fetchone()

        if result is None:
            print("Stop ID 1 was not found.")
            return

        stop_id, current_longitude = result

        print("Database: DTMS_TEST")
        print("Stop ID:", stop_id)
        print("Current longitude:", current_longitude)

        connection.execute(
            text("""
                UPDATE stops
                SET stop_lon = :longitude
                WHERE stop_id = :stop_id
            """),
            {
                "stop_id": stop_id,
                "longitude": 77.06389993096785,
            },
        )

        print("\nR012 repair completed successfully.")
        print("Restored longitude: 77.06389993096785")


if __name__ == "__main__":
    repair_r012_corruption()