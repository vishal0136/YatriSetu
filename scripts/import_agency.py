from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db_connection import engine


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "agency.txt"


EXPECTED_COLUMNS = [
    "agency_id",
    "agency_name",
    "agency_url",
    "agency_timezone",
    "agency_lang",
    "agency_phone",
    "agency_fare_url",
    "agency_email",
]


def import_agency():
    print("Starting agency import...")
    print(f"Source: {RAW_FILE}")

    df = pd.read_csv(
        RAW_FILE,
        dtype="string",
        keep_default_na=False
    )

    print(f"Records read: {len(df)}")

    # Check source schema
    missing_columns = [
        column for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    unexpected_columns = [
        column for column in df.columns
        if column not in EXPECTED_COLUMNS
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in agency.txt: {missing_columns}"
        )

    if unexpected_columns:
        print(
            f"Warning: unexpected columns found: {unexpected_columns}"
        )

    df = df[EXPECTED_COLUMNS]

    # Basic validation
    if df["agency_id"].duplicated().any():
        duplicates = df.loc[
            df["agency_id"].duplicated(),
            "agency_id"
        ].tolist()

        raise ValueError(
            f"Duplicate agency_id values found: {duplicates}"
        )

    if df["agency_id"].eq("").any():
        raise ValueError("agency_id contains empty values.")

    if df["agency_name"].eq("").any():
        raise ValueError("agency_name contains empty values.")

    # Insert into PostgreSQL
    with engine.begin() as connection:

        connection.execute(
            text("TRUNCATE TABLE agency CASCADE")
        )

        insert_query = text("""
            INSERT INTO agency (
                agency_id,
                agency_name,
                agency_url,
                agency_timezone,
                agency_lang,
                agency_phone,
                agency_fare_url,
                agency_email
            )
            VALUES (
                :agency_id,
                :agency_name,
                :agency_url,
                :agency_timezone,
                :agency_lang,
                :agency_phone,
                :agency_fare_url,
                :agency_email
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
            text("SELECT COUNT(*) FROM agency")
        ).scalar_one()

    print("\nAGENCY IMPORT SUCCESSFUL")
    print(f"Records inserted: {count}")


if __name__ == "__main__":
    import_agency()