from pathlib import Path
import sys

from sqlalchemy import text

# Allow imports when running this file directly
sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from scripts.db_connection import engine
from validation.validation_engine import ValidationEngine


def check_orphan_references():

    print("=" * 70)
    print("YATRISETU - CROSS-TABLE REFERENTIAL INTEGRITY")
    print("=" * 70)

    validator = ValidationEngine(
        "DTMS Referential Integrity"
    )

    with engine.connect() as connection:

        # ---------------------------------------------------------
        # R005 - routes.agency_id -> agency.agency_id
        # ---------------------------------------------------------

        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM routes r
                LEFT JOIN agency a
                    ON r.agency_id = a.agency_id
                WHERE r.agency_id IS NOT NULL
                  AND a.agency_id IS NULL;
            """)
        )

        orphan_agencies = result.scalar()

        print(
            f"\nR005 - Orphan agency references: "
            f"{orphan_agencies:,}"
        )

        if orphan_agencies > 0:
            validator.add_issue(
                rule_id="R005",
                severity="HIGH",
                issue_type="ORPHAN_AGENCY_REFERENCE",
                description="Routes contain agency_id values that do not exist in agency.",
                count=orphan_agencies
            )

        # ---------------------------------------------------------
        # R006 - trips.route_id -> routes.route_id
        # ---------------------------------------------------------

        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM trips t
                LEFT JOIN routes r
                    ON t.route_id = r.route_id
                WHERE t.route_id IS NOT NULL
                  AND r.route_id IS NULL;
            """)
        )

        orphan_routes = result.scalar()

        print(
            f"R006 - Orphan route references: "
            f"{orphan_routes:,}"
        )

        if orphan_routes > 0:
            validator.add_issue(
                rule_id="R006",
                severity="HIGH",
                issue_type="ORPHAN_ROUTE_REFERENCE",
                description="Trips contain route_id values that do not exist in routes.",
                count=orphan_routes
            )

        # ---------------------------------------------------------
        # R007 - trips.service_id -> calendar.service_id
        # ---------------------------------------------------------

        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM trips t
                LEFT JOIN calendar c
                    ON t.service_id = c.service_id
                WHERE t.service_id IS NOT NULL
                  AND c.service_id IS NULL;
            """)
        )

        orphan_services = result.scalar()

        print(
            f"R007 - Orphan service references: "
            f"{orphan_services:,}"
        )

        if orphan_services > 0:
            validator.add_issue(
                rule_id="R007",
                severity="HIGH",
                issue_type="ORPHAN_SERVICE_REFERENCE",
                description="Trips contain service_id values that do not exist in calendar.",
                count=orphan_services
            )

        # ---------------------------------------------------------
        # R008 - stop_times.trip_id -> trips.trip_id
        # ---------------------------------------------------------

        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM stop_times st
                LEFT JOIN trips t
                    ON st.trip_id = t.trip_id
                WHERE t.trip_id IS NULL;
            """)
        )

        orphan_trips = result.scalar()

        print(
            f"R008 - Orphan trip references: "
            f"{orphan_trips:,}"
        )

        if orphan_trips > 0:
            validator.add_issue(
                rule_id="R008",
                severity="HIGH",
                issue_type="ORPHAN_TRIP_REFERENCE",
                description="stop_times contains trip_id values that do not exist in trips.",
                count=orphan_trips
            )

        # ---------------------------------------------------------
        # R009 - stop_times.stop_id -> stops.stop_id
        # ---------------------------------------------------------

        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM stop_times st
                LEFT JOIN stops s
                    ON st.stop_id = s.stop_id
                WHERE s.stop_id IS NULL;
            """)
        )

        orphan_stops = result.scalar()

        print(
            f"R009 - Orphan stop references: "
            f"{orphan_stops:,}"
        )

        if orphan_stops > 0:
            validator.add_issue(
                rule_id="R009",
                severity="HIGH",
                issue_type="ORPHAN_STOP_REFERENCE",
                description="stop_times contains stop_id values that do not exist in stops.",
                count=orphan_stops
            )

        # ---------------------------------------------------------
        # R010 - trips.shape_id -> shapes.shape_id
        # ---------------------------------------------------------

        result = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM trips t
                LEFT JOIN (
                    SELECT DISTINCT shape_id
                    FROM shapes
                ) s
                    ON t.shape_id = s.shape_id
                WHERE t.shape_id IS NOT NULL
                  AND s.shape_id IS NULL;
            """)
        )

        orphan_shapes = result.scalar()

        print(
            f"R010 - Orphan shape references: "
            f"{orphan_shapes:,}"
        )

        if orphan_shapes > 0:
            validator.add_issue(
                rule_id="R010",
                severity="HIGH",
                issue_type="ORPHAN_SHAPE_REFERENCE",
                description="Trips contain shape_id values that do not exist in shapes.",
                count=orphan_shapes
            )

    # ---------------------------------------------------------
    # Create report
    # ---------------------------------------------------------

    report = validator.create_report(
        total_records=0,
        valid_records=0,
        statistics={
            "orphan_agency_references": orphan_agencies,
            "orphan_route_references": orphan_routes,
            "orphan_service_references": orphan_services,
            "orphan_trip_references": orphan_trips,
            "orphan_stop_references": orphan_stops,
            "orphan_shape_references": orphan_shapes
        }
    )

    report_path = Path(
        "validation/reports/referential_integrity.json"
    )

    validator.save_report(
        report,
        report_path
    )

    print("\n" + "=" * 70)
    print("REFERENTIAL INTEGRITY CHECK COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    check_orphan_references()