from validation.rules.validate_database import test_engine
from sqlalchemy import text

with test_engine.connect() as conn:
    with conn.begin():
        conn.execute(
            text("""
                UPDATE trips
                SET direction_id = 2
                WHERE trip_id = '10_07_45'
            """)
        )

print("R023 corruption injected into DTMS_TEST.")
