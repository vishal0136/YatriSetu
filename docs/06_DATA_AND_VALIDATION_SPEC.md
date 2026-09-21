# YatriSetu Data and Validation Specification

## Current Tables

`agency`, `feed_info`, `calendar`, `routes`, `stops`, `shapes`, `trips`,
`stop_times`

## Imported Record Counts

  Table            Records
  ------------ -----------
  agency                 2
  feed_info              2
  calendar               1
  routes             2,554
  stops              6,812
  shapes           765,633
  trips             65,322
  stop_times     2,385,381

## Data Observations

`stop_times` contains extended GTFS times greater than 24 hours. Maximum
observed time was `28:53:54`, with 22,719 records above 24 hours. These
are represented as integer seconds in the database.

All 65,322 trips currently have missing `trip_headsign`, `direction_id`,
and `block_id`. These are quality observations, not automatically
validation failures.

## Validation Rules

R001 Required field missing; R002 Duplicate primary key; R003 Duplicate
complete record; R004 Invalid data type; R005-R010 orphan references;
R011 invalid latitude; R012 invalid longitude; R013 suspicious
geographic location; R014 invalid stop sequence; R015 invalid
arrival/departure time; R016 departure before arrival; R017 invalid
service date range; R018 invalid service-day configuration; R019 missing
shape; R020 route/shape inconsistency; R021 suspicious duplicate stop;
R022 missing important field; R023 invalid categorical value.

## Validation Philosophy

Deterministic rules are preferred for mechanically provable conditions.
The LLM does not replace deterministic validation.
