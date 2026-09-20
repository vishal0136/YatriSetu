from sqlalchemy import text

from db_connection import engine


def check_tables():
    print("Checking DTMS database tables...\n")

    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
            )

            tables = result.fetchall()

            print(f"Number of tables found: {len(tables)}")
            print("-" * 35)

            if not tables:
                print("No tables found.")

            else:
                for table in tables:
                    print(table[0])

            print("\nDatabase table check completed.")

    except Exception as error:
        print("\nDatabase table check failed!")
        print(error)


if __name__ == "__main__":
    check_tables()