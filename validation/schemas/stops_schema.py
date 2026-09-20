import pandera.pandas as pa
from pandera.pandas import Column


stops_schema = pa.DataFrameSchema(
    {
        "stop_id": Column(
            str,
            nullable=False,
            unique=True
        ),

        "stop_code": Column(
            str,
            nullable=True
        ),

        "stop_name": Column(
            str,
            nullable=False
        ),

        "stop_lat": Column(
            float,
            nullable=False,
            checks=pa.Check.in_range(-90, 90)
        ),

        "stop_lon": Column(
            float,
            nullable=False,
            checks=pa.Check.in_range(-180, 180)
        ),
    },

    strict=False
)