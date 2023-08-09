from geographiclib.geodesic import Geodesic
import numpy as np

import config


def compute_lat_lon(px: float, py: float) -> tuple:
    """
    Compute the position in the global WGS84 coordinate reference system.

    :param px: X position in the local coordinate reference system.
    :param py: Y position in the local coordinate reference system.
    :return: Latitude and longitude values.
    :rtype: tuple.

    """
    # Reference point with known latitude and longitude values.
    lat1 = config.REFERENCE_POINT_LAT
    lon1 = config.REFERENCE_POINT_LON

    # Position with respect to the reference point.
    px += config.IPS_REF_POINT_OFFSET_X
    py += config.IPS_REF_POINT_OFFSET_Y

    # Angle with respect to the positive X axis of the IPS.
    angle = np.rad2deg(np.arctan2(py, px))
    # Angle with respect to the vertical axis of the WGS84
    # reference system, -180.0..+180.0.
    azimuth = 90.0 - angle - np.abs(config.IPS_WGS84_ANGLE_OFFSET)
    if azimuth > 180.0:
        azimuth = azimuth - 360.0

    # Distance between the reference point and point (px,py).
    distance = np.sqrt(np.power(px, 2) + np.power(py, 2))
    
    # Solve a direct geodesic problem.
    solution = Geodesic.WGS84.Direct(lat1, lon1, azimuth, distance)
    latitude = round(solution["lat2"], 9)
    longitude = round(solution["lon2"], 9)

    return (latitude, longitude)
