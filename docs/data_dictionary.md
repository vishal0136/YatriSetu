# YatriSetu GTFS Data Dictionary

## 1. agency

| Column | Data Type | Required | Primary Key | Foreign Key | Validation |
|---|---|---|---|---|---|
| agency_id | TEXT | Yes | Yes | No | Must be unique and non-empty |
| agency_name | TEXT | Yes | No | No | Must not be empty |
| agency_url | TEXT | No | No | No | Valid URL if provided |
| agency_timezone | TEXT | Yes | No | No | Must contain valid timezone |
| agency_lang | TEXT | No | No | No | Valid language code if provided |

## 2. stops

| Column | Data Type | Required | Primary Key | Foreign Key | Validation |
|---|---|---|---|---|---|
| stop_id | TEXT | Yes | Yes | No | Unique and non-empty |
| stop_code | TEXT | No | No | No | Valid format if provided |
| stop_name | TEXT | Yes | No | No | Must not be empty |
| stop_lat | DOUBLE PRECISION | Yes | No | No | Must be between -90 and 90 |
| stop_lon | DOUBLE PRECISION | Yes | No | No | Must be between -180 and 180 |

## 3. routes

| Column | Data Type | Required | Primary Key | Foreign Key | Validation |
|---|---|---|---|---|---|
| route_id | TEXT | Yes | Yes | No | Unique and non-empty |
| agency_id | TEXT | No | No | agency.agency_id | Referenced agency must exist |
| route_long_name | TEXT | No | No | No | Check empty/invalid values |
| route_short_name | TEXT | No | No | No | Check empty/invalid values |
| route_desc | TEXT | No | No | No | Check formatting |
| route_type | INTEGER | No | No | No | Validate against expected GTFS values |

## 4. calendar

| Column | Data Type | Required | Primary Key | Foreign Key | Validation |
|---|---|---|---|---|---|
| service_id | TEXT | Yes | Yes | No | Unique and non-empty |
| monday | BOOLEAN | Yes | No | No | 0/1 |
| tuesday | BOOLEAN | Yes | No | No | 0/1 |
| wednesday | BOOLEAN | Yes | No | No | 0/1 |
| thursday | BOOLEAN | Yes | No | No | 0/1 |
| friday | BOOLEAN | Yes | No | No | 0/1 |
| saturday | BOOLEAN | Yes | No | No | 0/1 |
| sunday | BOOLEAN | Yes | No | No | 0/1 |
| start_date | DATE | Yes | No | No | Valid date |
| end_date | DATE | Yes | No | No | Must be >= start_date |

## 5. shapes

| Column | Data Type | Required | Primary Key | Foreign Key | Validation |
|---|---|---|---|---|---|
| shape_id | TEXT | Yes | Composite | No | Must not be empty |
| shape_pt_lat | DOUBLE PRECISION | Yes | No | No | Between -90 and 90 |
| shape_pt_lon | DOUBLE PRECISION | Yes | No | No | Between -180 and 180 |
| shape_pt_sequence | INTEGER | Yes | Composite | No | Must be valid/increasing |
| shape_dist_traveled | DOUBLE PRECISION | No | No | No | Non-negative if provided |

## 6. trips

| Column | Data Type | Required | Primary Key | Foreign Key | Validation |
|---|---|---|---|---|---|
| trip_id | TEXT | Yes | Yes | No | Unique and non-empty |
| route_id | TEXT | Yes | No | routes.route_id | Route must exist |
| service_id | TEXT | Yes | No | calendar.service_id | Service must exist |
| trip_headsign | TEXT | No | No | No | Check empty/invalid values |
| direction_id | INTEGER | No | No | No | Expected directional value |
| block_id | TEXT | No | No | No | Check formatting |
| shape_id | TEXT | No | No | shapes.shape_id | Shape should exist if provided |

## 7. stop_times

| Column | Data Type | Required | Primary Key | Foreign Key | Validation |
|---|---|---|---|---|---|
| trip_id | TEXT | Yes | Composite | trips.trip_id | Trip must exist |
| arrival_time | TIME | No | No | No | Valid transit time |
| departure_time | TIME | No | No | No | Valid transit time |
| stop_id | TEXT | Yes | No | stops.stop_id | Stop must exist |
| stop_sequence | INTEGER | Yes | Composite | No | Positive and ordered |
| stop_headsign | TEXT | No | No | No | Check formatting |
| pickup_type | INTEGER | No | No | No | Validate allowed values |
| drop_off_type | INTEGER | No | No | No | Validate allowed values |
| shape_dist_traveled | DOUBLE PRECISION | No | No | No | Non-negative if provided |
| stop_dist | DOUBLE PRECISION | No | No | No | Validate missing/invalid values |

## 8. feed_info

| Column | Data Type | Required | Validation |
|---|---|---|---|
| feed_publisher_name | TEXT | Yes | Must not be empty |
| feed_publisher_url | TEXT | Yes | Valid URL |
| feed_lang | TEXT | Yes | Valid language code |
| feed_start_date | DATE | No | Valid date |
| feed_end_date | DATE | No | Must be >= start date |
| feed_version | TEXT | No | Check consistency/version format |