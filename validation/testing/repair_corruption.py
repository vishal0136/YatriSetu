from sqlalchemy import text

from validation.testing.inject_corruption import test_engine


def repair_invalid_latitude():
    print("Starting controlled repair...")

    with test_engine.begin() as connection:

        result = connection.execute(
            text("""
                SELECT stop_id, stop_lat
                FROM stops
                WHERE stop_id = :stop_id
            """),
            {"stop_id": "1"},
        ).fetchone()

        if result is None:
            print("Stop ID 1 was not found.")
            return

        stop_id, current_latitude = result

        print("Database: DTMS_TEST")
        print("Stop ID:", stop_id)
        print("Current latitude:", current_latitude)

        connection.execute(
            text("""
                UPDATE stops
                SET stop_lat = :latitude
                WHERE stop_id = :stop_id
            """),
            {
                "stop_id": stop_id,
                "latitude": 28.71797103184126,
            },
        )

        print("Latitude restored successfully.")
        print("Restored latitude:", 28.71797103184126)


if __name__ == "__main__":
    repair_invalid_latitude()