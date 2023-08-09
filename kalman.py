import numpy as np
from numpy.linalg import inv

import config

X1, Y1, Z1 = config.COORDINATES_ANCHOR1
X2, Y2, Z2 = config.COORDINATES_ANCHOR2
X3, Y3, Z3 = config.COORDINATES_ANCHOR3
X4, Y4, Z4 = config.COORDINATES_ANCHOR4


class EKF:
    """Extended Kalman Filter (EKF) class."""

    def __init__(
        self,
        x0: float,
        y0: float,
        z0: float,
        dt: float,
        std_az: int,
        std_el: int,
    ) -> None:
        """
        Extended Kalman Filter (EKF) that uses constant velocity model.

        :param x0: Initial X location of the tag.
        :param y0: Initial Y location of the tag.
        :param z0: Initial Z location of the tag.
        :param dt: Time step in seconds.
        :param std_az: Standard deviation of the azimuth angle.
        :param std_el: Standard deviation of the elevation angle.

        """
        # State x.
        self.x = np.array([x0, 0.0, y0, 0.0, z0, 0.0]).T
        # State transition matrix F.
        self.F = np.array(
            [
                [1, dt, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0],
                [0, 0, 1, dt, 0, 0],
                [0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, dt],
                [0, 0, 0, 0, 0, 1],
            ]
        )
        # Covariance matrix P.
        self.P = np.eye(6) * 100
        # Process noise matrix Q.
        self.Q = np.eye(6) * 1e-4
        self.Q = np.array([
                [2.667e-6, 2.000e-4, 0.0, 0.0, 0.0, 0.0],
                [2.000e-4, 2.000e-2, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 2.667e-6, 2.000e-4, 0.0, 0.0],
                [0.0, 0.0, 2.000e-4, 2.000e-2, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 2.667e-6, 2.000e-4],
                [0.0, 0.0, 0.0, 0.0, 2.000e-4, 2.000e-2],
        ])
        
        # Measurement noise matrix R.
        self.R = np.diag([
            np.power(np.deg2rad(std_az), 2),
            np.power(np.deg2rad(std_az), 2),
            np.power(np.deg2rad(std_az), 2),
            np.power(np.deg2rad(std_az), 2),
            np.power(np.deg2rad(std_el), 2),
            np.power(np.deg2rad(std_el), 2),
            np.power(np.deg2rad(std_el), 2),
            np.power(np.deg2rad(std_el), 2),
        ])
        # Identity matrix I.
        self.I = np.eye(6)


    def HJacobian(self) -> np.ndarray:
        """Compute Jacobian of the measurement function H at x."""
        # Helper variables.
        x, y, z = (self.x[0], self.x[2], self.x[4])
        dx1, dx2, dx3, dx4 = (x - X1, x - X2, x - X3, x - X4)
        dy1, dy2, dy3, dy4 = (y - Y1, y - Y2, y - Y3, y - Y4)
        dz1, dz2, dz3, dz4 = (z - Z1, z - Z2, z - Z3, z - Z4)
        c1 = dx1**2 + dy1**2
        c2 = dx2**2 + dy2**2
        c3 = dx3**2 + dy3**2
        c4 = dx4**2 + dy4**2
        sqrt1 = np.sqrt(c1)
        sqrt2 = np.sqrt(c2)
        sqrt3 = np.sqrt(c3)
        sqrt4 = np.sqrt(c4)
        d1 = dx1**2 + dy1**2 + dz1**2
        d2 = dx2**2 + dy2**2 + dz2**2
        d3 = dx3**2 + dy3**2 + dz3**2
        d4 = dx4**2 + dy4**2 + dz4**2

        return np.array([
            [-dy1/c1, 0, dx1/c1, 0, 0, 0],
            [-dy2/c2, 0, dx2/c2, 0, 0, 0],
            [-dy3/c3, 0, dx3/c3, 0, 0, 0],
            [-dy4/c4, 0, dx4/c4, 0, 0, 0],
            [-(dx1*dz1)/(sqrt1*d1), 0, -(dy1*dz1)/(sqrt1*d1), 0, sqrt1/d1, 0],
            [-(dx2*dz2)/(sqrt2*d2), 0, -(dy2*dz2)/(sqrt2*d2), 0, sqrt2/d2, 0],
            [-(dx3*dz3)/(sqrt3*d3), 0, -(dy3*dz3)/(sqrt3*d3), 0, sqrt3/d3, 0],
            [-(dx4*dz4)/(sqrt4*d4), 0, -(dy4*dz4)/(sqrt4*d4), 0, sqrt4/d4, 0]
        ])


    def Hx(self) -> np.ndarray:
        """Compute the measurement function H at x."""
        x, y, z = (self.x[0], self.x[2], self.x[4])

        return np.array([
            np.arctan2((y-Y1), (x-X1)),
            np.arctan2((y-Y2), (x-X2)),
            np.arctan2((y-Y3), (x-X3)),
            np.arctan2((y-Y4), (x-X4)),
            np.arctan2((z-Z1), np.sqrt((x-X1)**2 + (y-Y1)**2)),
            np.arctan2((z-Z2), np.sqrt((x-X2)**2 + (y-Y2)**2)),
            np.arctan2((z-Z3), np.sqrt((x-X3)**2 + (y-Y3)**2)),
            np.arctan2((z-Z4), np.sqrt((x-X4)**2 + (y-Y4)**2)),
        ])


    def predict(self):
        """Predict the state x and covariance matrix P."""
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q


    def update(self, z: np.ndarray):
        """
        Update the state x and covariance matrix P.

        :param ndarray z: Measured azimuth and elevation angles as
            [az1, az2, az3, az4, el1, el2, el3, el4].

        """
        H = self.HJacobian()
        hx = self.Hx()
        # System uncertainty.
        S = H @ self.P @ H.T + self.R
        # Kalman gain.
        K = self.P @ H.T @ inv(S)
        # Residual.
        y = np.subtract(np.deg2rad(z), hx)
        # Update state.
        self.x = self.x + K @ y
        # Update covariance.
        I_KH = self.I - K @ H
        self.P = I_KH @ self.P @ I_KH + K @ self.R @ K.T
