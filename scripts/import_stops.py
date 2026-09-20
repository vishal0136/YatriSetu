from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db_connection import engine


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data" / "raw" / "stops.txt"


EXPECTED_COLUMNS = [
    "stop_id",
    "stop_code",
    "stop_name",
    "stop_lat",
    "stop_lon",
]


def import_stops():
    print("Starting stops import...")
    print(f"Source: {RAW_FILE}")

    df = pd.read_csv(
        RAW_FILE,
        dtype={
            "stop_id": "string",
            "stop_code": "string",
            "stop_name": "string",
        },
        keep_default_na=False
    )

    print(f"Records read: {len(df)}")

    # Check source schema
    missing_columns = [
        column for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in stops.txt: {missing_columns}"
        )

    df = df[EXPECTED_COLUMNS]

    # Required fields
    for column in ["stop_id", "stop_name"]:
        if df[column].eq("").any():
            raise ValueError(
                f"{column} contains empty values."
            )

    # Duplicate stop IDs
    if df["stop_id"].duplicated().any():
        duplicates = df.loc[
            df["stop_id"].duplicated(),
            "stop_id"
        ].tolist()

        raise ValueError(
            f"Duplicate stop_id values found: {duplicates[:20]}"
        )

    # Convert coordinates
    df["stop_lat"] = pd.to_numeric(
        df["stop_lat"],
        errors="raise"
    )

    df["stop_lon"] = pd.to_numeric(
        df["stop_lon"],
        errors="raise"
    )

    # Validate geographic ranges
    if not df["stop_lat"].between(-90, 90).all():
        raise ValueError(
            "Invalid latitude value found."
        )

    if not df["stop_lon"].between(-180, 180).all():
        raise ValueError(
            "Invalid longitude value found."
        )

    # Insert into PostgreSQL
    with engine.begin() as connection:

        connection.execute(
            text("TRUNCATE TABLE stops CASCADE")
        )

        insert_query = text("""
            INSERT INTO stops (
                stop_id,
                stop_code,
                stop_name,
                stop_lat,
                stop_lon
            )
            VALUES (
                :stop_id,
                :stop_code,
                :stop_name,
                :stop_lat,
                :stop_lon
            )
        """)

        records = df.to_dict(orient="records")

        connection.execute(
            insert_query,
            records
        )

    # Verify
    with engine.connect() as connection:
        count = connection.execute(
            text("SELECT COUNT(*) FROM stops")
        ).scalar_one()

    print("\nSTOPS IMPORT SUCCESSFUL")
    print(f"Records inserted: {count}")


if __name__ == "__main__":
    import_stops()