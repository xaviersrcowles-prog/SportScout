"""Geographic helpers: Haversine distance and bounding-box pre-filtering."""

import math
from typing import Optional


EARTH_RADIUS_MILES = 3958.7613


def haversine_distance_miles(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Great-circle distance between two coordinates, in miles."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_MILES * c


def bounding_box(
    lat: float, lon: float, radius_miles: float
) -> tuple[float, float, float, float]:
    """Return (min_lat, max_lat, min_lon, max_lon) that fully contains the radius.

    Used to cheaply discard far-away records before the exact Haversine check.
    """
    lat_delta = radius_miles / 69.0
    lon_scale = max(math.cos(math.radians(lat)), 0.01)
    lon_delta = radius_miles / (69.0 * lon_scale)

    return (
        lat - lat_delta,
        lat + lat_delta,
        lon - lon_delta,
        lon + lon_delta,
    )


def in_bounding_box(
    lat: float,
    lon: float,
    box: tuple[float, float, float, float],
) -> bool:
    min_lat, max_lat, min_lon, max_lon = box
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon


def coordinates_of(facility: dict) -> Optional[tuple[float, float]]:
    try:
        return float(facility["latitude"]), float(facility["longitude"])
    except (KeyError, TypeError, ValueError):
        return None
