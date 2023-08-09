import logging
import socket

import paho.mqtt.client as mqtt

import config
import indoor
import uudfmessage


def main():
    logging.basicConfig(
        filename=config.LOGGING_FILENAME,
        format=config.LOGGING_FORMAT,
        level=logging.DEBUG
    )
    logger = logging.getLogger()
    
    client = mqtt.Client(client_id=config.MQTT_CLIENT_ID)
    client.connect(host=config.MQTT_HOST, port=config.MQTT_PORT)

    ips = indoor.IndoorPositioningSystem(logger, client)

    # Measured azimuth angles.
    az1, az2, az3, az4 = (0, 0, 0, 0)
    # Measured elevation angles.
    el1, el2, el3, el4 = (0, 0, 0, 0)
    # True, if AoA measurements are received from anchor.
    ok1, ok2, ok3, ok4 = (False, False, False, False)

    # UDP server socket.
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((config.SOCKET_HOST, config.SOCKET_PORT))
    server.setblocking(False)
    print(f"Server is running on {config.SOCKET_HOST}:{config.SOCKET_PORT}")

    try:
        while True:
            try:       
                # Receive AoA measurements from the anchors.
                data, _ = server.recvfrom(256)
                message = uudfmessage.UUDFMessage()
                isvalid = message.validate(data)
                if isvalid is False:
                    continue
                print(data)

                # Handle AoA measurements.
                if message.anchor_id == config.ID_ANCHOR1:
                    az1 = message.azimuth
                    el1 = message.elevation
                    ok1 = True
                elif message.anchor_id == config.ID_ANCHOR2:
                    az2 = message.azimuth
                    el2 = message.elevation
                    ok2 = True
                elif message.anchor_id == config.ID_ANCHOR3:
                    az3 = message.azimuth
                    el3 = message.elevation
                    ok3 = True
                elif message.anchor_id == config.ID_ANCHOR4:
                    az4 = message.azimuth
                    el4 = message.elevation
                    ok4 = True

                # Position calculation requires valid AoA measurements from
                # all 4 anchors.
                if not (ok1 and ok2 and ok3 and ok4):
                    continue
                ok1, ok2, ok3, ok4 = (False, False, False, False)

                ips.compute_tag_position(az1, az2, az3, az4, el1, el2, el3, el4)
                ips.send_position()

            except BlockingIOError:
                pass
    except KeyboardInterrupt:
        print("\nClosing server...")

    server.close()
    client.disconnect()


if __name__ == "__main__":
    main()
