import sys
import json
import os
from pathlib import Path

import pandas as pd

# Allow imports when running this file directly
sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from schemas.stops_schema import stops_schema


RAW_FILE = Path(
    "data/raw/stops_r004_backup.txt"
    if os.getenv("VALIDATE_R004_TEST", "false").lower() == "true"
    else "data/raw/stops.txt"
)
REPORT_FILE = Path("validation/reports/stops_validation.json")


def validate_stops():

    print("=" * 60)
    print("YATRISETU - STOPS VALIDATION")
    print("=" * 60)

    print(f"\nReading: {RAW_FILE}")

    if not RAW_FILE.exists():
        print("ERROR: stops.txt not found.")
        return

    # ---------------------------------------------------------
    # 1. Load data with correct identifier types
    # ---------------------------------------------------------

    df = pd.read_csv(
        RAW_FILE,
        dtype={
            "stop_id": "string",
            "stop_code": "string",
            "stop_name": "string",
        }
    )

    total_records = len(df)

    print(f"Records loaded: {total_records:,}")

    # ---------------------------------------------------------
    # 2. Basic data-quality statistics
    # ---------------------------------------------------------

    missing_values = {
        column: int(count)
        for column, count in df.isnull().sum().items()
        if count > 0
    }

    duplicate_ids = int(
        df["stop_id"].duplicated().sum()
    )

    invalid_coordinates = 0

    numeric_lat = pd.to_numeric(
        df["stop_lat"],
        errors="coerce"
    )

    numeric_lon = pd.to_numeric(
        df["stop_lon"],
        errors="coerce"
    )

    valid_coordinate_values = (
        numeric_lat.notna()
        & numeric_lon.notna()
    )

    invalid_coordinates = int(
        (
            valid_coordinate_values
            & (
                (numeric_lat < -90)
                | (numeric_lat > 90)
                | (numeric_lon < -180)
                | (numeric_lon > 180)
            )
        ).sum()
    )

    duplicate_rows = int(
        df.duplicated().sum()
    )

    # ---------------------------------------------------------
    # 3. Pandera schema validation
    # ---------------------------------------------------------

    schema_valid = True
    schema_errors = []

    try:

        validated_df = stops_schema.validate(
            df,
            lazy=True
        )

        valid_records = len(validated_df)

        print("\nVALIDATION SUCCESSFUL")
        print(f"Valid records: {valid_records:,}")

    except Exception as error:

        schema_valid = False
        valid_records = 0

        print("\nVALIDATION FAILED")
        print(error)

        schema_errors.append(
            str(error)
        )

    # ---------------------------------------------------------
    # 4. Determine invalid records
    # ---------------------------------------------------------

    invalid_records = (
        total_records - valid_records
        if schema_valid
        else total_records
    )

    # ---------------------------------------------------------
    # 5. Create issues list
    # ---------------------------------------------------------

    issues = []

    if duplicate_ids > 0:
        issues.append({
            "rule_id": "R002",
            "severity": "HIGH",
            "issue_type": "DUPLICATE_PRIMARY_KEY",
            "column": "stop_id",
            "count": duplicate_ids,
            "description": "Duplicate stop_id values detected."
        })

    if duplicate_rows > 0:
        issues.append({
            "rule_id": "R003",
            "severity": "MEDIUM",
            "issue_type": "DUPLICATE_RECORD",
            "count": duplicate_rows,
            "description": "Duplicate complete records detected."
        })

    if invalid_coordinates > 0:
        issues.append({
            "rule_id": "R012",
            "severity": "HIGH",
            "issue_type": "INVALID_COORDINATES",
            "count": invalid_coordinates,
            "description": "Latitude or longitude is outside the valid geographic range."
        })

    if missing_values:
        issues.append({
            "rule_id": "R001",
            "severity": "HIGH",
            "issue_type": "MISSING_VALUES",
            "columns": missing_values,
            "description": "Missing values detected in the dataset."
        })

    if not schema_valid:
        issues.append({
            "rule_id": "R004",
            "severity": "HIGH",
            "issue_type": "SCHEMA_VALIDATION_FAILED",
            "description": "One or more schema validation checks failed.",
            "errors": schema_errors
        })

    # ---------------------------------------------------------
    # 6. Build machine-readable report
    # ---------------------------------------------------------

    report = {
        "dataset": "stops.txt",
        "validation_status": (
            "PASS"
            if schema_valid and len(issues) == 0
            else "FAIL"
        ),
        "total_records": total_records,
        "valid_records": valid_records,
        "invalid_records": invalid_records,

        "statistics": {
            "missing_values": missing_values,
            "duplicate_ids": duplicate_ids,
            "duplicate_rows": duplicate_rows,
            "invalid_coordinates": invalid_coordinates
        },

        "issues": issues
    }

    # ---------------------------------------------------------
    # 7. Save report
    # ---------------------------------------------------------

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print("\nValidation report created:")
    print(REPORT_FILE)

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    validate_stops()