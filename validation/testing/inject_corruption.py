import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

TEST_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database="DTMS_TEST",
)

test_engine = create_engine(TEST_DATABASE_URL)


def inject_invalid_latitude():

    print("Starting controlled corruption...")

    with test_engine.begin() as connection:

        result = connection.execute(
            text("""
                SELECT stop_id, stop_lat
                FROM stops
                ORDER BY stop_id
                LIMIT 1
            """)
        ).fetchone()

        if result is None:
            raise RuntimeError("No stops found in DTMS_TEST.")

        stop_id, original_latitude = result

        connection.execute(
            text("""
                UPDATE stops
                SET stop_lat = 999
                WHERE stop_id = :stop_id
            """),
            {
                "stop_id": stop_id
            },
        )

        print("\nCorruption injected successfully.")
        print("Database: DTMS_TEST")
        print("Stop ID:", stop_id)
        print("Original latitude:", original_latitude)
        print("Corrupted latitude: 999")
        print("Expected rule: R011")


if __name__ == "__main__":
    inject_invalid_latitude()