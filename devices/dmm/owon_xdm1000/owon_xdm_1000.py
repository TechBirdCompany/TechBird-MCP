"""OWON XDM1000 Digital Multimeter measurement functions."""

import time
from typing import Tuple, List, Optional

from xdm1000 import XDM1000
from loguru import logger
from utils.utils import plot_data

class OWON_XDM1000:

    OVERHEAD_FACTOR = 1.5

    RATE_TO_INTERVAL = {
        "HIGH": 0.015 * OVERHEAD_FACTOR,
        "MID":  0.020 * OVERHEAD_FACTOR,
        "LOW":  0.500 * OVERHEAD_FACTOR,
    }

    def __init__(self):
        self.dmm = XDM1000()

        self.mode = "V"
        self.range = 230
        self.speed = "HIGH"

    # =========================================
    # Setup Functions
    # =========================================

    def setup(
        self,
        mode: str = "V",
        range: float = 230,
        speed: str = "HIGH",
    ) -> None:
        """
        Configure the device to the desired settings.

        Args:
            mode:   V(olt) or A(mpere)
            range:  Highest value that should be measured
            speed:  LOW, MID or HIGH
        """

        mode = mode.upper()
        speed = speed.upper()

        # Measurement mode
        if mode == "V":
            self.dmm.set_mode("VDC")
        elif mode == "A":
            self.dmm.set_mode("ADC")
        else:
            raise ValueError(
                f"Unsupported mode '{mode}'. Use 'V' or 'A'."
            )

        # Measurement speed
        rate_map = {
            "LOW": "SLOW",
            "MID": "MID",
            "HIGH": "FAST",
        }

        try:
            self.dmm.set_rate(rate_map[speed])
        except KeyError:
            raise ValueError(
                f"Unsupported speed '{speed}'. Use LOW, MID or HIGH."
            )

        # Measurement speed is stored locally for fetch_storage timing.
        self.speed = speed

        # Range (if supported by library)
        try:
            self.dmm.set_range(range)
            logger.debug(f"Range set to {range}")
        except Exception:
            logger.debug(
                "Manual range not supported by XDM1000 library. "
                "Using current device setting."
            )

        logger.info(
            f"DMM configured: mode={mode}, "
            f"range={range}, speed={speed}"
        )


    # =========================================
    # Measurement Functions
    # =========================================

    def fetch_single(self) -> float:
        """
        Gets the current value which is displayed on the screen.

        Returns:
            Current measured value
        """
        value = self.dmm.measure()

        logger.debug(
            f"Current measurement: {value}"
        )

        return float(value)



    def fetch_storage(
        self,
        samples: int = 200,
    ):
        '''
        Gets values for a given samples

        Args:
            samples:    Sets how many samples should be gathered or
                        how long the storage should be filled

        Returns:
            <VALUE>
        '''

        values = []

        interval = self.RATE_TO_INTERVAL[self.speed]

        next_sample = time.perf_counter()

        while len(values) < samples:
            logger.info(f"DMM counter at: {len(values)}")

            values.append(
                float(self.dmm.measure())
            )

            next_sample += interval

            sleep_time = (
                next_sample -
                time.perf_counter()
            )

            if sleep_time > 0:
                time.sleep(sleep_time)

        return values



    def set_display(self) -> None:
        """
        Sets the device in a state for a statistical measurement.

        Note:
            The OWON XDM1041 Python interface does not provide
            remote control of the display layout. This function
            exists only for API compatibility.
        """
        logger.warning(
            "set_display() is not supported "
            "by the OWON XDM1041"
        )



    def get_screenshot(
        self,
        folder: str = "measurements",
        prefix: str = "",
        label: str = "",
    ) -> None:
        """
        Get a screenshot of the current screen.

        Note:
            The OWON XDM1041 does not provide a remote screenshot
            function through the Python API. This function exists
            only for API compatibility.
        """
        logger.warning(
            "get_screenshot() is not supported "
            "by the OWON XDM1041"
        )

        return None



    def get_plot(
        self,
        title: str,
        y_label: str,
        suffix: str = "",
        nominal_value: float = 0.0,
        min_limit: float = 0.0,
        max_limit: float = 0.0,
        limit: int = 200,
    ):
        values = self.fetch_storage(samples=limit)

        return plot_data(
            x_data=list(range(len(values))),
            y_data=values,
            title=title,
            y_label=y_label,
            suffix=suffix,
            unit=self.mode,
            nominal_value=nominal_value,
            min_limit=min_limit,
            max_limit=max_limit,
        )
