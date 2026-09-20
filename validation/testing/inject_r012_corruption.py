from sqlalchemy import text
from validation.testing.inject_corruption import test_engine


def inject_r012_corruption():
    print("Starting R012 controlled corruption...")

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

        stop_id, original_longitude = result

        print("Database: DTMS_TEST")
        print("Stop ID:", stop_id)
        print("Original longitude:", original_longitude)

        connection.execute(
            text("""
                UPDATE stops
                SET stop_lon = :longitude
                WHERE stop_id = :stop_id
            """),
            {
                "stop_id": stop_id,
                "longitude": 999,
            },
        )

        print("\nR012 corruption injected successfully.")
        print("Stop ID:", stop_id)
        print("Corrupted longitude: 999")
        print("Expected rule: R012")
        print("Expected severity: HIGH")
        print("Expected issue type: GEOGRAPHIC")


if __name__ == "__main__":
    inject_r012_corruption()