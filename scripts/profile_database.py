from sqlalchemy import text

from db_connection import engine


def run_query(connection, title, query):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    result = connection.execute(text(query))

    rows = result.fetchall()

    for row in rows:
        print(row)

    return rows


def profile_database():

    print("Starting DTMS database profiling...")

    with engine.connect() as connection:

        # -------------------------------------------------
        # 1. Table record counts
        # -------------------------------------------------

        run_query(
            connection,
            "TABLE RECORD COUNTS",
            """
            SELECT 'agency' AS table_name, COUNT(*) AS records
            FROM agency

            UNION ALL

            SELECT 'calendar', COUNT(*)
            FROM calendar

            UNION ALL

            SELECT 'routes', COUNT(*)
            FROM routes

            UNION ALL

            SELECT 'stops', COUNT(*)
            FROM stops

            UNION ALL

            SELECT 'shapes', COUNT(*)
            FROM shapes

            UNION ALL

            SELECT 'trips', COUNT(*)
            FROM trips

            UNION ALL

            SELECT 'stop_times', COUNT(*)
            FROM stop_times

            ORDER BY table_name;
            """
        )

        # -------------------------------------------------
        # 2. Stops geographic profile
        # -------------------------------------------------

        run_query(
            connection,
            "STOPS GEOGRAPHIC PROFILE",
            """
            SELECT
                MIN(stop_lat) AS min_latitude,
                MAX(stop_lat) AS max_latitude,
                MIN(stop_lon) AS min_longitude,
                MAX(stop_lon) AS max_longitude,
                COUNT(*) AS total_stops
            FROM stops;
            """
        )

        # -------------------------------------------------
        # 3. Trip profile
        # -------------------------------------------------

        run_query(
            connection,
            "TRIP PROFILE",
            """
            SELECT
                COUNT(*) AS total_trips,
                COUNT(DISTINCT route_id) AS routes_used,
                COUNT(DISTINCT service_id) AS services_used,
                COUNT(DISTINCT shape_id) AS shapes_used
            FROM trips;
            """
        )

        # -------------------------------------------------
        # 4. Stop-time profile
        # -------------------------------------------------

        run_query(
            connection,
            "STOP TIMES PROFILE",
            """
            SELECT
                COUNT(*) AS total_stop_times,
                MIN(arrival_time) AS earliest_arrival_seconds,
                MAX(arrival_time) AS latest_arrival_seconds,
                MIN(departure_time) AS earliest_departure_seconds,
                MAX(departure_time) AS latest_departure_seconds
            FROM stop_times;
            """
        )

        # -------------------------------------------------
        # 5. Extended GTFS times
        # -------------------------------------------------

        run_query(
            connection,
            "EXTENDED GTFS TIME PROFILE",
            """
            SELECT
                COUNT(*) AS records_after_24_hours
            FROM stop_times
            WHERE arrival_time >= 86400
               OR departure_time >= 86400;
            """
        )

        # -------------------------------------------------
        # 6. Missing values in trips
        # -------------------------------------------------

        run_query(
            connection,
            "TRIPS MISSING VALUE PROFILE",
            """
            SELECT
                COUNT(*) FILTER (
                    WHERE trip_headsign IS NULL
                       OR trip_headsign = ''
                ) AS missing_trip_headsign,

                COUNT(*) FILTER (
                    WHERE trip_short_name IS NULL
                       OR trip_short_name = ''
                ) AS missing_trip_short_name,

                COUNT(*) FILTER (
                    WHERE direction_id IS NULL
                ) AS missing_direction_id,

                COUNT(*) FILTER (
                    WHERE block_id IS NULL
                       OR block_id = ''
                ) AS missing_block_id
            FROM trips;
            """
        )

        # -------------------------------------------------
        # 7. Missing stop distance
        # -------------------------------------------------

        run_query(
            connection,
            "STOP TIMES NULL PROFILE",
            """
            SELECT
                COUNT(*) AS total_records,
                COUNT(*) FILTER (
                    WHERE stop_dist IS NULL
                ) AS missing_stop_dist,
                COUNT(*) FILTER (
                    WHERE fare_stage IS NULL
                ) AS missing_fare_stage
            FROM stop_times;
            """
        )

        # -------------------------------------------------
        # 8. Referential integrity
        # -------------------------------------------------

        run_query(
            connection,
            "ORPHAN ROUTE REFERENCES",
            """
            SELECT COUNT(*)
            FROM routes r
            LEFT JOIN agency a
                ON r.agency_id = a.agency_id
            WHERE a.agency_id IS NULL;
            """
        )

        run_query(
            connection,
            "ORPHAN TRIP ROUTE REFERENCES",
            """
            SELECT COUNT(*)
            FROM trips t
            LEFT JOIN routes r
                ON t.route_id = r.route_id
            WHERE r.route_id IS NULL;
            """
        )

        run_query(
            connection,
            "ORPHAN TRIP SERVICE REFERENCES",
            """
            SELECT COUNT(*)
            FROM trips t
            LEFT JOIN calendar c
                ON t.service_id = c.service_id
            WHERE c.service_id IS NULL;
            """
        )

        run_query(
            connection,
            "ORPHAN TRIP SHAPE REFERENCES",
            """
            SELECT COUNT(*)
            FROM trips t
            LEFT JOIN (
                SELECT DISTINCT shape_id
                FROM shapes
            ) s
                ON t.shape_id = s.shape_id
            WHERE s.shape_id IS NULL;
            """
        )

        run_query(
            connection,
            "ORPHAN STOP TIME TRIP REFERENCES",
            """
            SELECT COUNT(*)
            FROM stop_times st
            LEFT JOIN trips t
                ON st.trip_id = t.trip_id
            WHERE t.trip_id IS NULL;
            """
        )

        run_query(
            connection,
            "ORPHAN STOP TIME STOP REFERENCES",
            """
            SELECT COUNT(*)
            FROM stop_times st
            LEFT JOIN stops s
                ON st.stop_id = s.stop_id
            WHERE s.stop_id IS NULL;
            """
        )

    print("\n" + "=" * 60)
    print("DTMS DATABASE PROFILING COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    profile_database()