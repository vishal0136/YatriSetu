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


# Display safe connection information
# Never print the password.
print("Host:", DB_HOST)
print("Port:", DB_PORT)
print("Database:", DB_NAME)
print("User:", DB_USER)


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


# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)


# Test the connection
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