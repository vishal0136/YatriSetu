from pathlib import Path
import json
import os

from dotenv import load_dotenv
from sqlalchemy import text, create_engine
from sqlalchemy.engine import URL

from scripts.db_connection import engine


# Load environment variables from .env
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent.parent

PRODUCTION_REPORT_FILE = (
    BASE_DIR
    / "validation"
    / "reports"
    / "database_validation.json"
)

TEST_REPORT_FILE = (
    BASE_DIR
    / "validation"
    / "reports"
    / "database_validation_test.json"
)


# ============================================================
# SAFE TEST DATABASE CONFIGURATION
# ============================================================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

TEST_DATABASE_NAME = os.getenv(
    "TEST_DB_NAME",
    "DTMS_TEST"
)


if not DB_PASSWORD:
    raise RuntimeError(
        "DB_PASSWORD is not configured. "
        "Check your .env file."
    )


TEST_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=TEST_DATABASE_NAME,
)

test_engine = create_engine(TEST_DATABASE_URL)


class DatabaseValidator:

    def __init__(self):
        self.issues = []

    def add_issue(
        self,
        rule_id,
        severity,
        issue_type,
        description,
        details=None,
    ):
        issue = {
            "rule_id": rule_id,
            "severity": severity,
            "issue_type": issue_type,
            "description": description,
        }

        if details:
            issue["details"] = details

        self.issues.append(issue)

    # ============================================================
    # R001 — Required fields
    # ============================================================

    def validate_required_fields(self, connection):

        queries = {
            "agency": """
                SELECT COUNT(*)
                FROM agency
                WHERE agency_id IS NULL
                   OR agency_name IS NULL
                   OR agency_name = ''
                   OR agency_timezone IS NULL
                   OR agency_timezone = ''
            """,

            "calendar": """
                SELECT COUNT(*)
                FROM calendar
                WHERE service_id IS NULL
                   OR start_date IS NULL
                   OR end_date IS NULL
            """,

            "stops": """
                SELECT COUNT(*)
                FROM stops
                WHERE stop_id IS NULL
                   OR stop_name IS NULL
                   OR stop_name = ''
                   OR stop_lat IS NULL
                   OR stop_lon IS NULL
            """,

            "routes": """
                SELECT COUNT(*)
                FROM routes
                WHERE route_id IS NULL
            """,

            "trips": """
                SELECT COUNT(*)
                FROM trips
                WHERE trip_id IS NULL
                   OR route_id IS NULL
                   OR service_id IS NULL
            """,

            "stop_times": """
                SELECT COUNT(*)
                FROM stop_times
                WHERE trip_id IS NULL
                   OR stop_id IS NULL
                   OR stop_sequence IS NULL
            """,

            "shapes": """
                SELECT COUNT(*)
                FROM shapes
                WHERE shape_id IS NULL
                   OR shape_pt_lat IS NULL
                   OR shape_pt_lon IS NULL
                   OR shape_pt_sequence IS NULL
            """,
        }

        for table_name, query in queries.items():

            count = connection.execute(
                text(query)
            ).scalar_one()

            if count > 0:
                self.add_issue(
                    "R001",
                    "HIGH",
                    "COMPLETENESS",
                    f"Required fields missing in {table_name}.",
                    {
                        "table": table_name,
                        "affected_records": count,
                    },
                )

    # ============================================================
    # R002 — Duplicate primary keys
    # ============================================================

    def validate_duplicate_keys(self, connection):

        checks = {
            "agency": "agency_id",
            "calendar": "service_id",
            "routes": "route_id",
            "stops": "stop_id",
            "trips": "trip_id",
        }

        for table_name, column_name in checks.items():

            query = f"""
                SELECT COUNT(*)
                FROM (
                    SELECT {column_name}
                    FROM {table_name}
                    GROUP BY {column_name}
                    HAVING COUNT(*) > 1
                ) duplicates
            """

            count = connection.execute(
                text(query)
            ).scalar_one()

            if count > 0:
                self.add_issue(
                    "R002",
                    "HIGH",
                    "UNIQUENESS",
                    f"Duplicate primary-key values in {table_name}.",
                    {
                        "table": table_name,
                        "duplicate_keys": count,
                    },
                )

        # stop_times composite primary key
        query = """
            SELECT COUNT(*)
            FROM (
                SELECT trip_id, stop_sequence
                FROM stop_times
                GROUP BY trip_id, stop_sequence
                HAVING COUNT(*) > 1
            ) duplicates
        """

        count = connection.execute(
            text(query)
        ).scalar_one()

        if count > 0:
            self.add_issue(
                "R002",
                "HIGH",
                "UNIQUENESS",
                "Duplicate composite keys in stop_times.",
                {
                    "table": "stop_times",
                    "duplicate_keys": count,
                },
            )

        # shapes composite primary key
        query = """
            SELECT COUNT(*)
            FROM (
                SELECT shape_id, shape_pt_sequence
                FROM shapes
                GROUP BY shape_id, shape_pt_sequence
                HAVING COUNT(*) > 1
            ) duplicates
        """

        count = connection.execute(
            text(query)
        ).scalar_one()

        if count > 0:
            self.add_issue(
                "R002",
                "HIGH",
                "UNIQUENESS",
                "Duplicate composite keys in shapes.",
                {
                    "table": "shapes",
                    "duplicate_keys": count,
                },
            )

    # ============================================================
    # R003 — Duplicate complete records
    # ============================================================

    def validate_duplicate_records(self, connection):

        checks = {
            "agency": """
                agency_id,
                agency_name,
                agency_url,
                agency_timezone,
                agency_lang,
                agency_phone,
                agency_fare_url,
                agency_email
            """,

            "stops": """
                stop_id,
                stop_code,
                stop_name,
                stop_lat,
                stop_lon
            """,

            "routes": """
                route_id,
                agency_id,
                route_long_name,
                route_short_name,
                route_desc,
                route_type
            """,
        }

        for table_name, columns in checks.items():

            query = f"""
                SELECT COUNT(*)
                FROM (
                    SELECT {columns}
                    FROM {table_name}
                    GROUP BY {columns}
                    HAVING COUNT(*) > 1
                ) duplicates
            """

            count = connection.execute(
                text(query)
            ).scalar_one()

            if count > 0:
                self.add_issue(
                    "R003",
                    "MEDIUM",
                    "UNIQUENESS",
                    f"Duplicate complete records in {table_name}.",
                    {
                        "table": table_name,
                        "duplicate_groups": count,
                    },
                )

    # ============================================================
    # R005–R010 — Referential integrity
    # ============================================================

    def validate_references(self, connection):

        checks = [
            (
                "R005",
                "routes",
                "agency_id",
                "agency",
                "agency_id",
                "Orphan agency references detected in routes.",
            ),
            (
                "R006",
                "trips",
                "route_id",
                "routes",
                "route_id",
                "Orphan route references detected in trips.",
            ),
            (
                "R007",
                "trips",
                "service_id",
                "calendar",
                "service_id",
                "Orphan service references detected in trips.",
            ),
            (
                "R008",
                "stop_times",
                "trip_id",
                "trips",
                "trip_id",
                "Orphan trip references detected in stop_times.",
            ),
            (
                "R009",
                "stop_times",
                "stop_id",
                "stops",
                "stop_id",
                "Orphan stop references detected in stop_times.",
            ),
        ]

        for (
            rule_id,
            child_table,
            child_column,
            parent_table,
            parent_column,
            description,
        ) in checks:

            query = f"""
                SELECT COUNT(*)
                FROM {child_table} child
                LEFT JOIN {parent_table} parent
                    ON child.{child_column} = parent.{parent_column}
                WHERE child.{child_column} IS NOT NULL
                  AND parent.{parent_column} IS NULL
            """

            count = connection.execute(
                text(query)
            ).scalar_one()

            if count > 0:
                self.add_issue(
                    rule_id,
                    "HIGH",
                    "REFERENTIAL_INTEGRITY",
                    description,
                    {
                        "table": child_table,
                        "affected_records": count,
                    },
                )

        # R010 — trip shape references
        query = """
            SELECT COUNT(*)
            FROM trips t
            LEFT JOIN (
                SELECT DISTINCT shape_id
                FROM shapes
            ) s
                ON t.shape_id = s.shape_id
            WHERE t.shape_id IS NOT NULL
              AND s.shape_id IS NULL
        """

        count = connection.execute(
            text(query)
        ).scalar_one()

        if count > 0:
            self.add_issue(
                "R010",
                "HIGH",
                "REFERENTIAL_INTEGRITY",
                "Orphan shape references detected in trips.",
                {
                    "table": "trips",
                    "affected_records": count,
                },
            )

    # ============================================================
    # R011 / R012 — Geographic validation
    # ============================================================

    def validate_coordinates(self, connection):

        invalid_latitude = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM stops
                WHERE stop_lat < -90
                   OR stop_lat > 90
            """)
        ).scalar_one()

        if invalid_latitude > 0:
            self.add_issue(
                "R011",
                "HIGH",
                "GEOGRAPHIC",
                "Invalid latitude values detected.",
                {
                    "affected_records": invalid_latitude,
                },
            )

        invalid_longitude = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM stops
                WHERE stop_lon < -180
                   OR stop_lon > 180
            """)
        ).scalar_one()

        if invalid_longitude > 0:
            self.add_issue(
                "R012",
                "HIGH",
                "GEOGRAPHIC",
                "Invalid longitude values detected.",
                {
                    "affected_records": invalid_longitude,
                },
            )

    # ============================================================
    # R013 — Suspicious geographic location
    # ============================================================

    def validate_geographic_range(self, connection):

        result = connection.execute(
            text("""
                SELECT
                    MIN(stop_lat),
                    MAX(stop_lat),
                    MIN(stop_lon),
                    MAX(stop_lon)
                FROM stops
            """)
        ).fetchone()

        min_lat, max_lat, min_lon, max_lon = result

        if (
            min_lat is not None
            and max_lat is not None
            and min_lon is not None
            and max_lon is not None
        ):

            if (
                min_lat < 27
                or max_lat > 31
                or min_lon < 74
                or max_lon > 79
            ):
                self.add_issue(
                    "R013",
                    "MEDIUM",
                    "GEOGRAPHIC",
                    "Stops contain coordinates outside the configured Delhi-NCR review range.",
                    {
                        "min_lat": float(min_lat),
                        "max_lat": float(max_lat),
                        "min_lon": float(min_lon),
                        "max_lon": float(max_lon),
                    },
                )

    # ============================================================
    # R014 — Stop sequence
    # ============================================================

    def validate_stop_sequences(self, connection):

        negative_sequences = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM stop_times
                WHERE stop_sequence < 0
            """)
        ).scalar_one()

        if negative_sequences > 0:
            self.add_issue(
                "R014",
                "HIGH",
                "TIMETABLE",
                "Negative stop_sequence values detected.",
                {
                    "affected_records": negative_sequences,
                },
            )

        duplicate_sequences = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM (
                    SELECT trip_id, stop_sequence
                    FROM stop_times
                    GROUP BY trip_id, stop_sequence
                    HAVING COUNT(*) > 1
                ) duplicates
            """)
        ).scalar_one()

        if duplicate_sequences > 0:
            self.add_issue(
                "R014",
                "HIGH",
                "TIMETABLE",
                "Duplicate stop_sequence values detected within trips.",
                {
                    "affected_groups": duplicate_sequences,
                },
            )

    # ============================================================
    # R015 — Timetable values
    # ============================================================

    def validate_times(self, connection):

        invalid_times = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM stop_times
                WHERE arrival_time < 0
                   OR departure_time < 0
            """)
        ).scalar_one()

        if invalid_times > 0:
            self.add_issue(
                "R015",
                "HIGH",
                "TIMETABLE",
                "Negative timetable values detected.",
                {
                    "affected_records": invalid_times,
                },
            )

    # ============================================================
    # R016 — Arrival/departure ordering
    # ============================================================

    def validate_arrival_departure(self, connection):

        invalid_order = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM stop_times
                WHERE arrival_time IS NOT NULL
                  AND departure_time IS NOT NULL
                  AND departure_time < arrival_time
            """)
        ).scalar_one()

        if invalid_order > 0:
            self.add_issue(
                "R016",
                "HIGH",
                "TIMETABLE",
                "Departure occurs before arrival.",
                {
                    "affected_records": invalid_order,
                },
            )

    # ============================================================
    # R017 — Service date range
    # ============================================================

    def validate_service_dates(self, connection):

        invalid_dates = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM calendar
                WHERE start_date > end_date
            """)
        ).scalar_one()

        if invalid_dates > 0:
            self.add_issue(
                "R017",
                "MEDIUM",
                "SERVICE",
                "Service start date occurs after end date.",
                {
                    "affected_records": invalid_dates,
                },
            )

    # ============================================================
    # R018 — Service-day configuration
    # ============================================================

    def validate_service_days(self, connection):

        invalid_days = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM calendar
                WHERE COALESCE(monday, FALSE) = FALSE
                  AND COALESCE(tuesday, FALSE) = FALSE
                  AND COALESCE(wednesday, FALSE) = FALSE
                  AND COALESCE(thursday, FALSE) = FALSE
                  AND COALESCE(friday, FALSE) = FALSE
                  AND COALESCE(saturday, FALSE) = FALSE
                  AND COALESCE(sunday, FALSE) = FALSE
            """)
        ).scalar_one()

        if invalid_days > 0:
            self.add_issue(
                "R018",
                "MEDIUM",
                "SERVICE",
                "Service has no active operating day.",
                {
                    "affected_records": invalid_days,
                },
            )

    # ============================================================
    # R019 — Missing shape
    # ============================================================

    def validate_missing_shapes(self, connection):

        missing_shapes = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM trips
                WHERE shape_id IS NULL
                   OR shape_id = ''
            """)
        ).scalar_one()

        if missing_shapes > 0:
            self.add_issue(
                "R019",
                "HIGH",
                "ROUTE_SHAPE",
                "Trips are missing shape references.",
                {
                    "affected_records": missing_shapes,
                },
            )

    # ============================================================
    # R020 — Route/shape consistency
    # ============================================================

    def validate_route_shape_consistency(self, connection):

        inconsistent = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM trips t
                JOIN (
                    SELECT route_id, shape_id, COUNT(*) AS shape_count
                    FROM trips
                    WHERE route_id IS NOT NULL
                      AND shape_id IS NOT NULL
                    GROUP BY route_id, shape_id
                ) rs
                    ON t.route_id = rs.route_id
                   AND t.shape_id = rs.shape_id
                JOIN (
                    SELECT route_id, MAX(shape_count) AS dominant_count
                    FROM (
                        SELECT route_id, shape_id, COUNT(*) AS shape_count
                        FROM trips
                        WHERE route_id IS NOT NULL
                          AND shape_id IS NOT NULL
                        GROUP BY route_id, shape_id
                    ) counts
                    GROUP BY route_id
                ) dominant
                    ON rs.route_id = dominant.route_id
                WHERE rs.shape_count < dominant.dominant_count
            """)
        ).scalar_one()

        if inconsistent > 0:
            self.add_issue(
                "R020",
                "MEDIUM",
                "ROUTE_SHAPE",
                "Trip references a shape inconsistent with the dominant shape pattern of its route.",
                {
                    "affected_records": inconsistent,
                },
            )

    # ============================================================
    # R021 — Suspicious duplicate stops
    # ============================================================

    def validate_suspicious_stops(self, connection):

        suspicious = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM (
                    SELECT
                        stop_name,
                        ROUND(stop_lat::numeric, 5),
                        ROUND(stop_lon::numeric, 5),
                        COUNT(*) AS occurrences
                    FROM stops
                    GROUP BY
                        stop_name,
                        ROUND(stop_lat::numeric, 5),
                        ROUND(stop_lon::numeric, 5)
                    HAVING COUNT(*) > 1
                ) duplicates
            """)
        ).scalar_one()

        if suspicious > 0:
            self.add_issue(
                "R021",
                "MEDIUM",
                "SEMANTIC",
                "Potential duplicate stops detected using name and geographic proximity.",
                {
                    "duplicate_groups": suspicious,
                },
            )

    # ============================================================
    # R022 — Missing important fields
    # ============================================================

    def validate_important_fields(self, connection):

        missing_headsign = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM trips
                WHERE trip_headsign IS NULL
                   OR trip_headsign = ''
            """)
        ).scalar_one()

        missing_direction = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM trips
                WHERE direction_id IS NULL
            """)
        ).scalar_one()

        missing_block = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM trips
                WHERE block_id IS NULL
                   OR block_id = ''
            """)
        ).scalar_one()

        total_trips = connection.execute(
            text("SELECT COUNT(*) FROM trips")
        ).scalar_one()

        self.quality_observations = {
            "trip_headsign_missing": missing_headsign,
            "direction_id_missing": missing_direction,
            "block_id_missing": missing_block,
            "total_trips": total_trips,
        }

    # ============================================================
    # R023 — Domain values
    # ============================================================

    def validate_domain_values(self, connection):

        invalid_direction = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM trips
                WHERE direction_id IS NOT NULL
                  AND direction_id NOT IN (0, 1)
            """)
        ).scalar_one()

        if invalid_direction > 0:
            self.add_issue(
                "R023",
                "HIGH",
                "DOMAIN",
                "Invalid direction_id values detected.",
                {
                    "affected_records": invalid_direction,
                },
            )

    # ============================================================
    # RUN VALIDATION
    # ============================================================

    def run(self, use_test_database=False):

        database_engine = (
            test_engine
            if use_test_database
            else engine
        )

        database_name = (
            TEST_DATABASE_NAME
            if use_test_database
            else "DTMS"
        )

        report_file = (
            TEST_REPORT_FILE
            if use_test_database
            else PRODUCTION_REPORT_FILE
        )

        print("Starting database validation...")
        print("Database:", database_name)

        self.quality_observations = {}

        with database_engine.connect() as connection:

            self.validate_required_fields(connection)
            self.validate_duplicate_keys(connection)
            self.validate_duplicate_records(connection)
            self.validate_references(connection)
            self.validate_coordinates(connection)
            self.validate_geographic_range(connection)
            self.validate_stop_sequences(connection)
            self.validate_times(connection)
            self.validate_arrival_departure(connection)
            self.validate_service_dates(connection)
            self.validate_service_days(connection)
            self.validate_missing_shapes(connection)
            self.validate_route_shape_consistency(connection)
            self.validate_suspicious_stops(connection)
            self.validate_important_fields(connection)
            self.validate_domain_values(connection)

        status = "PASS" if not self.issues else "FAIL"

        report = {
            "dataset": database_name,
            "validation_status": status,
            "issue_count": len(self.issues),
            "issues": self.issues,
            "quality_observations": self.quality_observations,
        }

        report_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            report_file,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                report,
                file,
                indent=4,
            )

        print("\nDATABASE VALIDATION COMPLETED")
        print(f"Status: {status}")
        print(f"Issues: {len(self.issues)}")
        print(f"Report: {report_file}")


if __name__ == "__main__":

    validator = DatabaseValidator()

    use_test_database = (
        os.getenv(
            "VALIDATE_TEST_DB",
            "false"
        ).strip().lower()
        in {"true", "1", "yes"}
    )

    validator.run(
        use_test_database=use_test_database
    )