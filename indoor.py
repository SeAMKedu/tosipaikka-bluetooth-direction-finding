import json
from logging import Logger
import time

import numpy as np
import paho.mqtt.client as mqtt

import config
import geotools
import kalman


class IndoorPositioningSystem:
    """
    Indoor positioning system (IPS) class.

    :param logger: Logger object.
    :param client: MQTT client object.

    """
    def __init__(
            self, 
            logger: Logger = None, 
            client: mqtt.Client = None
        ) -> None:
        self.logger = logger
        self.client = client

        self.ekf = kalman.EKF(
            x0=config.KF_X0,
            y0=config.KF_Y0,
            z0=config.KF_Z0,
            dt=config.IPS_TAG_ADVERTISING_INTERVAL,
            std_az=config.KF_STD_AZIMUTH,
            std_el=config.KF_STD_ELEVATION
        )
        self.position = {}


    def compute_tag_position(
            self,
            measured_azimuth1: int,
            measured_azimuth2: int,
            measured_azimuth3: int,
            measured_azimuth4: int,
            measured_elevation1: int,
            measured_elevation2: int,
            measured_elevation3: int,
            measured_elevation4: int,
        ):
        """
        Compute the position of the Bluetooth tag by using the extended
        Kalman filter and measured azimuth and elevation angles.

        :param measured_azimuth1: Azimuth angle measured by anchor 1.
        :param measured_azimuth2: Azimuth angle measured by anchor 2.
        :param measured_azimuth3: Azimuth angle measured by anchor 3.
        :param measured_azimuth4: Azimuth angle measured by anchor 4.
        :param measured_elevation1: Elevation angle measured by anchor 1.
        :param measured_elevation2: Elevation angle measured by anchor 2.
        :param measured_elevation3: Elevation angle measured by anchor 3.
        :param measured_elevation4: Elevation angle measured by anchor 4.

        """
        # Azimuth angle with respect to the positive X axis of the IPS's
        # coordinate reference system:
        # Azimuth angle = anchor's azimuth angle - measured azimuth angle.
        az1 = config.AZIMUTH_ANCHOR1 - measured_azimuth1
        az2 = config.AZIMUTH_ANCHOR2 - measured_azimuth2
        az3 = config.AZIMUTH_ANCHOR3 - measured_azimuth3
        az4 = config.AZIMUTH_ANCHOR4 - measured_azimuth4

        # Elevation angle with respect to the XY plane of the IPS's
        # coordinate reference system:
        # Elevation angle = anchor's elevation angle + measured elevation angle.
        el1 = config.ELEVATION_ANCHOR1 + measured_elevation1
        el2 = config.ELEVATION_ANCHOR2 + measured_elevation2
        el3 = config.ELEVATION_ANCHOR3 + measured_elevation3
        el4 = config.ELEVATION_ANCHOR4 + measured_elevation4

        # Measurement data z for the Kalman filter.
        aoa = [az1, az2, az3, az4, el1, el2, el3, el4]
        z = np.array(aoa).T

        # Use extended Kalman filter to compute the tag's position.
        self.ekf.predict()
        self.ekf.update(z)

        # (px,py) -> (lat,lon)
        lat, lon = geotools.compute_lat_lon(self.ekf.x[0], self.ekf.x[2])

        self.position = {
            "time": time.time_ns() // 1_000_000,
            "name": "bluetooth-df",
            "lat": lat,
            "lon": lon,
            "pos": {
                "x": round(self.ekf.x[0], 2),
                "y": round(self.ekf.x[2], 2),
                "z": round(self.ekf.x[4], 2),
            },
            "aoa": aoa,
        }

        if self.logger:
            self.logger.debug(self.position)


    def send_position(self):
        """Send the position to the MQTT server."""

        payload = json.dumps(self.position)
        if self.client:
            self.client.publish(config.MQTT_TOPIC, payload)

