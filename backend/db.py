"""Parameterized read-only queries. SQL connection strings are never stored here."""
import os
from contextlib import closing

import psycopg2

FIELDS = (
    "crash_date", "borough", "latitude", "longitude",
    "number_of_persons_injured", "contributing_factor_vehicle_1",
)
SELECT = (
    "SELECT crash_date, borough, latitude, longitude, "
    "number_of_persons_injured, contributing_factor_vehicle_1 FROM crash_data "
)


def _fetch(query, args):
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL is not configured")
    with closing(psycopg2.connect(dsn, connect_timeout=5)) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, args)
            rows = cursor.fetchall()
    return [dict(zip(FIELDS, row)) for row in rows]


def get_recent_crashes(limit=200):
    if not isinstance(limit, int) or not 1 <= limit <= 500:
        raise ValueError("Limit must be 1-500")
    return _fetch(
        SELECT + "WHERE latitude IS NOT NULL AND longitude IS NOT NULL "
        "ORDER BY crash_date DESC LIMIT %s", (limit,)
    )


def get_crashes_in_bbox(min_lon, min_lat, max_lon, max_lat, limit=500):
    if not isinstance(limit, int) or not 1 <= limit <= 500:
        raise ValueError("Limit must be 1-500")
    # Filtering numeric latitude and longitude avoids assuming the old
    # database has a PostGIS geom column (the import script did not create it).
    return _fetch(
        SELECT + "WHERE longitude BETWEEN %s AND %s "
        "AND latitude BETWEEN %s AND %s "
        "ORDER BY crash_date DESC LIMIT %s",
        (min_lon, max_lon, min_lat, max_lat, limit)
    )
