from sqlalchemy import text

from db_connection import create_test_engine

def get_random_stop():
    engine = create_test_engine()

    query = text("""
        SELECT
            stop_id,
            stop_code,
            stop_name,
            stop_lat,
            stop_lon
        FROM stops
        ORDER BY RANDOM()
        LIMIT 1;
    """)

    with engine.connect() as connection:
        row = connection.execute(query).mappings().first()

    return dict(row) if row else None


if __name__ == "__main__":
    result = get_random_stop()

    print("\n--- RANDOM STOP FROM DTMS_TEST ---")

    if result:
        for key, value in result.items():
            print(f"{key}: {value}")
    else:
        print("No stop found.")