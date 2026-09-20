from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db_connection import engine


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "stop_times.txt"

CHUNK_SIZE = 50_000

EXPECTED_COLUMNS = [
    "trip_id",
    "arrival_time",
    "departure_time",
    "stop_id",
    "stop_sequence",
    "fare_stage",
    "stop_dist",
]


# ---------------------------------------------------------
# GTFS time conversion
# ---------------------------------------------------------

def gtfs_time_to_seconds(value):
    """
    Convert GTFS HH:MM:SS into seconds from the
    beginning of the service day.

    Supports extended GTFS times such as:
        24:30:00
        28:53:54

    Example:
        06:05:00 -> 21900
        28:53:54 -> 104034
    """

    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    parts = value.split(":")

    if len(parts) != 3:
        raise ValueError(
            f"Invalid GTFS time format: {value}"
        )

    hours, minutes, seconds = map(int, parts)

    if hours < 0:
        raise ValueError(
            f"Negative hour value: {value}"
        )

    if not 0 <= minutes <= 59:
        raise ValueError(
            f"Invalid minutes value: {value}"
        )

    if not 0 <= seconds <= 59:
        raise ValueError(
            f"Invalid seconds value: {value}"
        )

    return (
        hours * 3600
        + minutes * 60
        + seconds
    )


# ---------------------------------------------------------
# Import function
# ---------------------------------------------------------

def import_stop_times():

    print("Starting stop_times import...")
    print(f"Source: {RAW_FILE}")
    print(f"Chunk size: {CHUNK_SIZE}")

    total_inserted = 0
    first_chunk = True

    # -----------------------------------------------------
    # Read source file in chunks
    # -----------------------------------------------------

    for chunk_number, df in enumerate(
        pd.read_csv(
            RAW_FILE,
            dtype={
                "trip_id": "string",
                "arrival_time": "string",
                "departure_time": "string",
                "stop_id": "string",
                "stop_sequence": "string",
                "fare_stage": "string",
                "stop_dist": "string",
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
        # Check source schema
        # -------------------------------------------------

        missing_columns = [
            column
            for column in EXPECTED_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing columns in stop_times.txt: "
                f"{missing_columns}"
            )

        df = df[EXPECTED_COLUMNS]

        # -------------------------------------------------
        # Required fields
        # -------------------------------------------------

        for column in [
            "trip_id",
            "stop_id",
            "stop_sequence",
        ]:

            if df[column].eq("").any():

                raise ValueError(
                    f"{column} contains empty values "
                    f"in chunk {chunk_number}."
                )

        # -------------------------------------------------
        # Convert GTFS times
        # -------------------------------------------------

        df["arrival_time"] = df[
            "arrival_time"
        ].apply(gtfs_time_to_seconds)

        df["departure_time"] = df[
            "departure_time"
        ].apply(gtfs_time_to_seconds)

        # -------------------------------------------------
        # Validate arrival/departure relationship
        # -------------------------------------------------

        both_times_present = (
            df["arrival_time"].notna()
            & df["departure_time"].notna()
        )

        invalid_time_order = (
            both_times_present
            & (
                df["departure_time"]
                < df["arrival_time"]
            )
        )

        if invalid_time_order.any():

            bad_rows = df.loc[
                invalid_time_order,
                [
                    "trip_id",
                    "arrival_time",
                    "departure_time",
                    "stop_id",
                ]
            ].head(10)

            raise ValueError(
                "Departure time is earlier than "
                f"arrival time in chunk {chunk_number}.\n"
                f"{bad_rows}"
            )

        # -------------------------------------------------
        # Convert stop_sequence
        # -------------------------------------------------

        df["stop_sequence"] = pd.to_numeric(
            df["stop_sequence"],
            errors="raise"
        ).astype(int)

        if (df["stop_sequence"] < 0).any():

            raise ValueError(
                f"Negative stop_sequence found "
                f"in chunk {chunk_number}."
            )

        # -------------------------------------------------
        # Convert fare_stage
        #
        # Empty values remain NULL.
        # -------------------------------------------------

        df["fare_stage"] = pd.to_numeric(
            df["fare_stage"],
            errors="coerce"
        ).astype("Int64")

        # -------------------------------------------------
        # Convert stop_dist
        #
        # Empty values remain NULL.
        # -------------------------------------------------

        df["stop_dist"] = pd.to_numeric(
            df["stop_dist"],
            errors="coerce"
        )

        if (
            df["stop_dist"].notna()
            & (df["stop_dist"] < 0)
        ).any():

            raise ValueError(
                f"Negative stop_dist found "
                f"in chunk {chunk_number}."
            )

        # -------------------------------------------------
        # Convert pandas missing values to Python None
        # -------------------------------------------------

        df = df.astype(object).where(
            pd.notna(df),
            None
        )

        # -------------------------------------------------
        # Insert into PostgreSQL
        # -------------------------------------------------

        with engine.begin() as connection:

            if first_chunk:

                connection.execute(
                    text(
                        "TRUNCATE TABLE stop_times"
                    )
                )

                first_chunk = False

            insert_query = text("""
                INSERT INTO stop_times (
                    trip_id,
                    arrival_time,
                    departure_time,
                    stop_id,
                    stop_sequence,
                    fare_stage,
                    stop_dist
                )
                VALUES (
                    :trip_id,
                    :arrival_time,
                    :departure_time,
                    :stop_id,
                    :stop_sequence,
                    :fare_stage,
                    :stop_dist
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
    # Final verification
    # -----------------------------------------------------

    with engine.connect() as connection:

        count = connection.execute(
            text(
                "SELECT COUNT(*) FROM stop_times"
            )
        ).scalar_one()

    print("\nSTOP_TIMES IMPORT SUCCESSFUL")
    print(f"Records inserted: {count}")


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    import_stop_times()