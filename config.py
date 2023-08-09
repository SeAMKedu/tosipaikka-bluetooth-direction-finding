# Logging.
LOGGING_FILENAME = "bluetooth_df.log"
LOGGING_FORMAT = "%(message)s"

# UDP server socket.
SOCKET_HOST = "172.17.128.169"
SOCKET_PORT = 20000
SOCKET_QUIT_COMMAND = "quit"

# MQTT.
MQTT_CLIENT_ID = "btdf"
MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "seamkiot/btdf"

# IDs of the anchors, i.e. antenna boards (C211).
ID_ANCHOR1 = "6C1DEBA79944"
ID_ANCHOR2 = "6C1DEBA79CBD"
ID_ANCHOR3 = "6C1DEBA79D05"
ID_ANCHOR4 = "6C1DEBA79D14"
# Anchors' coordinates with respect to the position of the anchor #1.
COORDINATES_ANCHOR1 = (0.00, 0.00, 0.00)
COORDINATES_ANCHOR2 = (0.00, 4.05, 0.00)
COORDINATES_ANCHOR3 = (4.10, 4.05, 0.00)
COORDINATES_ANCHOR4 = (4.10, 0.00, 0.00)
# Anchors' azimuth angles with respect to the positive X axis.
AZIMUTH_ANCHOR1 = 45
AZIMUTH_ANCHOR2 = -45
AZIMUTH_ANCHOR3 = -135
AZIMUTH_ANCHOR4 = 135
# Anchors' elevation angles with respect to the XY plane.
ELEVATION_ANCHOR1 = 7
ELEVATION_ANCHOR2 = 7
ELEVATION_ANCHOR3 = 7
ELEVATION_ANCHOR4 = 7

# Reference point with known latitude and longitude values.
# This point is needed for computing the tag's position as (lat,lon).
REFERENCE_POINT_LAT = 62.78910212
REFERENCE_POINT_LON = 22.82212920
REFERENCE_POINT_HMSL = 45521

# Offset of the Y axis of the IPS's coordinate reference system and
# vertical axis of the WGS84 reference system.
IPS_WGS84_ANGLE_OFFSET = -9.0
# Offset of the position of the anchor #1 with respect to the ref point.
IPS_REF_POINT_OFFSET_X = -2.9
IPS_REF_POINT_OFFSET_Y = -4.0
# Allowed values are 20 ms, 200 ms, and 1000 ms: 0.02, 0.2, 1.0
IPS_TAG_ADVERTISING_INTERVAL = 0.02

# Kalman filter.
KF_X0 = 2.0
KF_Y0 = 2.0
KF_Z0 = -0.2
KF_STD_AZIMUTH = 5
KF_STD_ELEVATION = 10
