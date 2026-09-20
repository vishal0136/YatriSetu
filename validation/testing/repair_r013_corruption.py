from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def repair_r013_corruption():
    print("Starting R013 controlled repair...")

    with test_engine.begin() as connection:

        result = connection.execute(
            text("""
                SELECT stop_id, stop_lat, stop_lon
                FROM stops
                WHERE stop_id = :stop_id
            """),
            {"stop_id": "1"},
        ).fetchone()

        if result is None:
            print("Stop ID 1 was not found.")
            return

        stop_id, current_latitude, current_longitude = result

        print("Database: DTMS_TEST")
        print("Stop ID:", stop_id)
        print("Current latitude:", current_latitude)
        print("Current longitude:", current_longitude)

        connection.execute(
            text("""
                UPDATE stops
                SET stop_lat = :latitude,
                    stop_lon = :longitude
                WHERE stop_id = :stop_id
            """),
            {
                "stop_id": stop_id,
                "latitude": 28.71797103184126,
                "longitude": 77.06389993096785,
            },
        )

        print("\nR013 repair completed successfully.")
        print("Restored latitude: 28.71797103184126")
        print("Restored longitude: 77.06389993096785")


if __name__ == "__main__":
    repair_r013_corruption()