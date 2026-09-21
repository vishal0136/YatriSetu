import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# Load variables from .env
load_dotenv()


# Read database configuration
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# Connection details are not printed during module import.
# This module can be imported by both production and controlled-test
# services, so import-time logging must not imply the active database.


# Create the PostgreSQL connection URL safely.
# URL.create() handles special characters such as @ in passwords.
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)


# Create production SQLAlchemy engine.
# This points to DTMS.
engine = create_engine(DATABASE_URL)


# Create controlled-test database engine.
# This points to DTMS_TEST and must be used for experiments.
def create_test_engine():
    test_db_name = os.getenv("TEST_DB_NAME")

    if not test_db_name:
        raise RuntimeError("TEST_DB_NAME is not configured in .env")

    TEST_DATABASE_URL = URL.create(
        drivername="postgresql+psycopg",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=test_db_name,
    )

    return create_engine(TEST_DATABASE_URL)


# Test the production database connection.
def test_connection():
    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("""
                    SELECT current_database(), version();
                """)
            )

            database, version = result.fetchone()

            print("\nConnection successful!")
            print("Database:", database)
            print("PostgreSQL:", version)

    except Exception as error:
        print("\nConnection failed!")
        print(error)


if __name__ == "__main__":
    test_connection()