from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db_connection import engine


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data" / "raw" / "calendar.txt"


EXPECTED_COLUMNS = [
    "service_id",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
    "start_date",
    "end_date",
]


def import_calendar():
    print("Starting calendar import...")
    print(f"Source: {RAW_FILE}")

    df = pd.read_csv(
        RAW_FILE,
        dtype="string",
        keep_default_na=False
    )

    print(f"Records read: {len(df)}")

    # Check columns
    missing_columns = [
        column for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in calendar.txt: {missing_columns}"
        )

    df = df[EXPECTED_COLUMNS]

    # Validate service_id
    if df["service_id"].eq("").any():
        raise ValueError("service_id contains empty values.")

    if df["service_id"].duplicated().any():
        duplicates = df.loc[
            df["service_id"].duplicated(),
            "service_id"
        ].tolist()

        raise ValueError(
            f"Duplicate service_id values found: {duplicates}"
        )

    # Convert day flags to integers
    day_columns = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    for column in day_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="raise"
        )

        if not df[column].isin([0, 1]).all():
            raise ValueError(
                f"{column} contains values other than 0 or 1."
            )

    # Convert dates
    df["start_date"] = pd.to_datetime(
        df["start_date"],
        format="%Y%m%d",
        errors="raise"
    ).dt.date

    df["end_date"] = pd.to_datetime(
        df["end_date"],
        format="%Y%m%d",
        errors="raise"
    ).dt.date

    # Validate date range
    if (df["start_date"] > df["end_date"]).any():
        raise ValueError(
            "Found calendar records where start_date is after end_date."
        )

    # Convert day values to Python bool
    for column in day_columns:
        df[column] = df[column].astype(bool)

    # Insert into PostgreSQL
    with engine.begin() as connection:

        connection.execute(
            text("TRUNCATE TABLE calendar CASCADE")
        )

        insert_query = text("""
            INSERT INTO calendar (
                service_id,
                monday,
                tuesday,
                wednesday,
                thursday,
                friday,
                saturday,
                sunday,
                start_date,
                end_date
            )
            VALUES (
                :service_id,
                :monday,
                :tuesday,
                :wednesday,
                :thursday,
                :friday,
                :saturday,
                :sunday,
                :start_date,
                :end_date
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
            text("SELECT COUNT(*) FROM calendar")
        ).scalar_one()

    print("\nCALENDAR IMPORT SUCCESSFUL")
    print(f"Records inserted: {count}")


if __name__ == "__main__":
    import_calendar()