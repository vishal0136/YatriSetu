from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db_connection import engine


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data" / "raw" / "shapes.txt"

CHUNK_SIZE = 50_000

EXPECTED_COLUMNS = [
    "shape_id",
    "shape_pt_lat",
    "shape_pt_lon",
    "shape_pt_sequence",
    "shape_dist_traveled",
]


def import_shapes():
    print("Starting shapes import...")
    print(f"Source: {RAW_FILE}")
    print(f"Chunk size: {CHUNK_SIZE}")

    total_inserted = 0
    first_chunk = True

    for chunk_number, df in enumerate(
        pd.read_csv(
            RAW_FILE,
            dtype={
                "shape_id": "string",
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

        # Check columns
        missing_columns = [
            column
            for column in EXPECTED_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing columns in shapes.txt: "
                f"{missing_columns}"
            )

        df = df[EXPECTED_COLUMNS]

        # Required fields
        if df["shape_id"].eq("").any():
            raise ValueError(
                f"Empty shape_id found in chunk {chunk_number}."
            )

        # Convert numeric fields
        numeric_columns = [
            "shape_pt_lat",
            "shape_pt_lon",
            "shape_pt_sequence",
            "shape_dist_traveled",
        ]

        for column in numeric_columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="raise"
            )

        # Geographic validation
        if not df["shape_pt_lat"].between(-90, 90).all():
            raise ValueError(
                f"Invalid latitude found in chunk {chunk_number}."
            )

        if not df["shape_pt_lon"].between(-180, 180).all():
            raise ValueError(
                f"Invalid longitude found in chunk {chunk_number}."
            )

        # Sequence validation
        if (df["shape_pt_sequence"] <= 0).any():
            raise ValueError(
                f"Invalid shape_pt_sequence found "
                f"in chunk {chunk_number}."
            )

        # Distance validation
        if (df["shape_dist_traveled"] < 0).any():
            raise ValueError(
                f"Negative shape_dist_traveled found "
                f"in chunk {chunk_number}."
            )

        # Insert
        with engine.begin() as connection:

            if first_chunk:
                connection.execute(
                    text("TRUNCATE TABLE shapes CASCADE")
                )
                first_chunk = False

            insert_query = text("""
                INSERT INTO shapes (
                    shape_id,
                    shape_pt_lat,
                    shape_pt_lon,
                    shape_pt_sequence,
                    shape_dist_traveled
                )
                VALUES (
                    :shape_id,
                    :shape_pt_lat,
                    :shape_pt_lon,
                    :shape_pt_sequence,
                    :shape_dist_traveled
                )
            """)

            records = df.to_dict(orient="records")

            connection.execute(
                insert_query,
                records
            )

        total_inserted += len(df)

        print(
            f"Chunk {chunk_number} inserted successfully."
        )
        print(
            f"Total inserted so far: {total_inserted}"
        )

    # Final verification
    with engine.connect() as connection:
        count = connection.execute(
            text("SELECT COUNT(*) FROM shapes")
        ).scalar_one()

    print("\nSHAPES IMPORT SUCCESSFUL")
    print(f"Records inserted: {count}")


if __name__ == "__main__":
    import_shapes()