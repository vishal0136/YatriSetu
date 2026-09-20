from validation.rules.validate_database import test_engine
from sqlalchemy import text

with test_engine.connect() as conn:
    with conn.begin():
        conn.execute(
            text("""
                UPDATE trips
                SET shape_id = 'shp_3_1744'
                WHERE trip_id = '10_07_45'
            """)
        )

print("R020 corruption repaired in DTMS_TEST.")
