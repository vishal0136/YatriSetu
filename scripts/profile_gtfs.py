from pathlib import Path
import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

RAW_DIR = Path("data/raw")

GTFS_FILES = [
    "agency.txt",
    "feed_info.txt",
    "stops.txt",
    "routes.txt",
    "calendar.txt",
    "trips.txt",
    "stop_times.txt",
    "shapes.txt",
]


# --------------------------------------------------
# Helper function
# --------------------------------------------------

def profile_file(file_name):
    file_path = RAW_DIR / file_name

    print("\n" + "=" * 70)
    print(f"FILE: {file_name}")
    print("=" * 70)

    if not file_path.exists():
        print("ERROR: File not found")
        return

    try:
        df = pd.read_csv(file_path)

        print(f"Rows              : {len(df):,}")
        print(f"Columns           : {len(df.columns)}")

        print("\nColumn names:")
        for column in df.columns:
            print(f"  - {column}")

        print("\nData types:")
        print(df.dtypes)

        print("\nMissing values:")
        missing = df.isnull().sum()

        for column, count in missing.items():
            print(f"  {column}: {count:,}")

        print("\nDuplicate rows:")
        print(f"  {df.duplicated().sum():,}")

        print("\nSample records:")
        print(df.head(3).to_string(index=False))

    except Exception as error:
        print(f"ERROR while reading {file_name}:")
        print(error)


# --------------------------------------------------
# Main program
# --------------------------------------------------

def main():

    print("=" * 70)
    print("YATRISETU GTFS DATA PROFILER")
    print("=" * 70)

    print(f"\nRaw data directory: {RAW_DIR.resolve()}")

    for file_name in GTFS_FILES:
        profile_file(file_name)

    print("\n" + "=" * 70)
    print("PROFILING COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()