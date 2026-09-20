from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db_connection import engine


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "trips.txt"

CHUNK_SIZE = 50_000


EXPECTED_COLUMNS = [
    "route_id",
    "service_id",
    "trip_id",
    "trip_headsign",
    "trip_short_name",
    "direction_id",
    "block_id",
    "shape_id",
    "wheelchair_accessible",
    "bikes_allowed",
]


# ---------------------------------------------------------
# Import function
# ---------------------------------------------------------

def import_trips():

    print("Starting trips import...")
    print(f"Source: {RAW_FILE}")
    print(f"Chunk size: {CHUNK_SIZE}")

    total_inserted = 0
    first_chunk = True

    # -----------------------------------------------------
    # Read trips.txt in chunks
    # -----------------------------------------------------

    for chunk_number, df in enumerate(
        pd.read_csv(
            RAW_FILE,
            dtype={
                "route_id": "string",
                "service_id": "string",
                "trip_id": "string",
                "trip_headsign": "string",
                "trip_short_name": "string",
                "direction_id": "string",
                "block_id": "string",
                "shape_id": "string",
                "wheelchair_accessible": "string",
                "bikes_allowed": "string",
            },
            chunksize=CHUNK_SIZE,
            keep_default_na=False,
        ),
        start=1,
    ):

        print(
            f"\nProcessing chunk {chunk_number} "
            f"({len(df)} records)..."
        )

        # -------------------------------------------------
        # Check source columns
        # -------------------------------------------------

        missing_columns = [
            column
            for column in EXPECTED_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing columns in trips.txt: "
                f"{missing_columns}"
            )

        df = df[EXPECTED_COLUMNS]

        # -------------------------------------------------
        # Required fields
        # -------------------------------------------------

        required_columns = [
            "route_id",
            "service_id",
            "trip_id",
            "shape_id",
        ]

        for column in required_columns:

            if df[column].eq("").any():

                raise ValueError(
                    f"{column} contains empty values "
                    f"in chunk {chunk_number}."
                )

        # -------------------------------------------------
        # Duplicate trip IDs
        # -------------------------------------------------

        if df["trip_id"].duplicated().any():

            duplicates = df.loc[
                df["trip_id"].duplicated(),
                "trip_id"
            ].tolist()

            raise ValueError(
                f"Duplicate trip_id values found "
                f"in chunk {chunk_number}: "
                f"{duplicates[:20]}"
            )

        # -------------------------------------------------
        # Convert optional integer fields
        #
        # Empty values become <NA>.
        # They will be inserted into PostgreSQL as NULL.
        # -------------------------------------------------

        integer_columns = [
            "direction_id",
            "wheelchair_accessible",
            "bikes_allowed",
        ]

        for column in integer_columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            ).astype("Int64")

        # -------------------------------------------------
        # Validate direction_id
        # -------------------------------------------------

        direction_values = df[
            "direction_id"
        ].dropna()

        if not direction_values.isin([0, 1]).all():

            raise ValueError(
                f"Invalid direction_id found "
                f"in chunk {chunk_number}."
            )

        # -------------------------------------------------
        # Validate wheelchair_accessible
        # -------------------------------------------------

        wheelchair_values = df[
            "wheelchair_accessible"
        ].dropna()

        if not wheelchair_values.isin([0, 1, 2]).all():

            raise ValueError(
                f"Invalid wheelchair_accessible value "
                f"in chunk {chunk_number}."
            )

        # -------------------------------------------------
        # Validate bikes_allowed
        # -------------------------------------------------

        bikes_values = df[
            "bikes_allowed"
        ].dropna()

        if not bikes_values.isin([0, 1, 2]).all():

            raise ValueError(
                f"Invalid bikes_allowed value "
                f"in chunk {chunk_number}."
            )

        # -------------------------------------------------
        # Insert into PostgreSQL
        # -------------------------------------------------

        with engine.begin() as connection:

            # Only clear the table once, before the first
            # successful chunk.
            if first_chunk:

                connection.execute(
                    text("TRUNCATE TABLE trips CASCADE")
                )

                first_chunk = False

            insert_query = text("""
                INSERT INTO trips (
                    trip_id,
                    route_id,
                    service_id,
                    trip_headsign,
                    direction_id,
                    block_id,
                    shape_id,
                    trip_short_name,
                    wheelchair_accessible,
                    bikes_allowed
                )
                VALUES (
                    :trip_id,
                    :route_id,
                    :service_id,
                    :trip_headsign,
                    :direction_id,
                    :block_id,
                    :shape_id,
                    :trip_short_name,
                    :wheelchair_accessible,
                    :bikes_allowed
                )
            """)

            records = df.to_dict(
                orient="records"
            )

            connection.execute(
                insert_query,
                records
            )

        # -------------------------------------------------
        # Progress
        # -------------------------------------------------

        total_inserted += len(df)

        print(
            f"Chunk {chunk_number} "
            f"inserted successfully."
        )

        print(
            f"Total inserted so far: "
            f"{total_inserted}"
        )

    # -----------------------------------------------------
    # Final database verification
    # -----------------------------------------------------

    with engine.connect() as connection:

        count = connection.execute(
            text("SELECT COUNT(*) FROM trips")
        ).scalar_one()

    print("\nTRIPS IMPORT SUCCESSFUL")
    print(f"Records inserted: {count}")


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    import_trips()