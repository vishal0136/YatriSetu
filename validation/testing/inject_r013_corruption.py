from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def inject_r013_corruption():
    print("Starting R013 controlled corruption...")

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

        stop_id, original_latitude, original_longitude = result

        print("Database: DTMS_TEST")
        print("Stop ID:", stop_id)
        print("Original latitude:", original_latitude)
        print("Original longitude:", original_longitude)

        # 32.0 is a valid latitude, but outside the
        # configured R013 review range (maximum 31).
        connection.execute(
            text("""
                UPDATE stops
                SET stop_lat = :latitude,
                    stop_lon = :longitude
                WHERE stop_id = :stop_id
            """),
            {
                "stop_id": stop_id,
                "latitude": 32.0,
                "longitude": 77.0,
            },
        )

        print("\nR013 corruption injected successfully.")
        print("Stop ID:", stop_id)
        print("Test latitude: 32.0")
        print("Test longitude: 77.0")
        print("Expected rule: R013")
        print("Expected severity: MEDIUM")
        print("Expected issue type: GEOGRAPHIC")
        print("R011/R012 should NOT be triggered.")


if __name__ == "__main__":
    inject_r013_corruption()