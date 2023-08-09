class UUDFMessage:
    """Class for the angle calculation event +UUDF."""

    def __init__(self) -> None:
        self.data = ""
        self.parameters = []

    @property
    def eddystone_id(self) -> str:
        """Eddystone instance ID."""
        return self.parameters[0]

    @property
    def rssi(self) -> int:
        """RSSI of polarization 1."""
        return int(self.parameters[1])

    @property
    def azimuth(self) -> int:
        """Azimuth angle in range -90° to +90°."""
        return int(self.parameters[2])

    @property
    def elevation(self) -> int:
        """Elevation angle in range -90° to +90°."""
        return int(self.parameters[3])

    # The 5th parameter is reserved for the future use.

    @property
    def channel(self) -> int:
        """Channel from which the packet angle was calculated."""
        return int(self.parameters[5])

    @property
    def anchor_id(self) -> str:
        """Anchor ID."""
        # '"myAncorID"' -> 'myAnchorID'
        return self.parameters[6].replace('"', '')

    @property
    def user_defined_str(self) -> str:
        """The value set by +UUDCFG param_tag 2."""
        return self.parameters[7]

    @property
    def timestamp_ms(self) -> int:
        """Time since boot in milliseconds."""
        return int(self.parameters[8])


    def validate(self, data: bytes) -> bool:
        """
        Validate the data that the anchor sent.

        :param data: Received message data.
        :returns: True if the data is valid, False if not.
        :rtype: bool.

        """
        # Expected message: b'\r\n+UUDF:param1,param2,...,param9\r\n'.
        isvalid = False
        try:
            self.data = data.decode().replace("\r\n", "")
            if self.data.startswith("+UUDF"):
                self.parameters = self.data.split(":")[1].split(",")
                if len(self.parameters) == 9:
                    isvalid = True
        except UnicodeDecodeError:
            pass
        except IndexError:
            pass
        return isvalid
