from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db_connection import engine


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data" / "raw" / "routes.txt"


EXPECTED_COLUMNS = [
    "agency_id",
    "route_id",
    "route_long_name",
    "route_short_name",
    "route_desc",
    "route_type",
]


def import_routes():
    print("Starting routes import...")
    print(f"Source: {RAW_FILE}")

    df = pd.read_csv(
        RAW_FILE,
        dtype={
            "agency_id": "string",
            "route_id": "string",
            "route_long_name": "string",
            "route_short_name": "string",
            "route_desc": "string",
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
            f"Missing columns in routes.txt: {missing_columns}"
        )

    df = df[EXPECTED_COLUMNS]

    # Basic validation
    if df["route_id"].eq("").any():
        raise ValueError("route_id contains empty values.")

    if df["route_id"].duplicated().any():
        duplicates = df.loc[
            df["route_id"].duplicated(),
            "route_id"
        ].tolist()

        raise ValueError(
            f"Duplicate route_id values found: {duplicates[:20]}"
        )

    if df["agency_id"].eq("").any():
        raise ValueError("agency_id contains empty values.")

    # Convert route_type
    df["route_type"] = pd.to_numeric(
        df["route_type"],
        errors="raise"
    ).astype(int)

    # Validate route_type
    if (df["route_type"] < 0).any():
        raise ValueError(
            "route_type contains negative values."
        )

    # Insert into PostgreSQL
    with engine.begin() as connection:

        connection.execute(
            text("TRUNCATE TABLE routes CASCADE")
        )

        insert_query = text("""
            INSERT INTO routes (
                agency_id,
                route_id,
                route_long_name,
                route_short_name,
                route_desc,
                route_type
            )
            VALUES (
                :agency_id,
                :route_id,
                :route_long_name,
                :route_short_name,
                :route_desc,
                :route_type
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
            text("SELECT COUNT(*) FROM routes")
        ).scalar_one()

    print("\nROUTES IMPORT SUCCESSFUL")
    print(f"Records inserted: {count}")


if __name__ == "__main__":
    import_routes()