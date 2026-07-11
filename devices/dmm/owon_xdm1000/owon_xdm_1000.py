"""OWON XDM1000 Digital Multimeter measurement functions."""

import time
from typing import Tuple, List, Optional, Literal

from xdm1000 import XDM1000
from loguru import logger
from utils.utils import plot_data

class OWON_XDM1000:

    OVERHEAD_FACTOR = 1.5

    RATE_TO_INTERVAL = {
        "F": 0.015 * OVERHEAD_FACTOR,   #FAST
        "M":  0.020 * OVERHEAD_FACTOR,  #MID
        "L":  0.500 * OVERHEAD_FACTOR,  #Low
    }

    def __init__(self):
        self.dmm = XDM1000()

        self.mode = "V"
        self.range = 230
        self.speed = "F"

    # =========================================
    # SCPI Ccommands
    # =========================================

    def _scpi_get_rate(
        self
    ) -> str:
        """
        Get the current rate of the DMM
        """
        rate = self.dmm.query("RATE?")
        
        logger.info(f"Current rate is {rate}")

    # =========================================
    # API Ccommands
    # =========================================

    def setup(
        self,
        mode: Literal["V", "A"] = "V",
        range: float = 0,
        speed: Literal["L", "M", "F"] = "F",
    ) -> None:
        """
        Configure the device.

        Args:
            <mode>  Sets the mode 
                    [V|A]
            
            <range> Range is kind of a stupid name and should be the
                    expected voltage which should be measured, as steps 
                    are different with every dmm
                    [0 = AUTO]

            <speed> Apperently most of DMMs do have speeds
                    [L|M|F]
        """

        mode = mode.upper()
        speed = speed.upper()

        # Measurement mode
        if mode == "V":
            self.dmm.set_mode("VDC")
        elif mode == "A":
            self.dmm.set_mode("ADC")
        else:
            logger.warning(f"Unsupported mode '{mode}'. Use 'V' or 'A'.")

        self.dmm.set_rate(speed)

        self.speed = speed

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

    def fetch_single(self) -> float:
        """
        Gets the current value which is displayed on the screen.

        Returns:
            Current measured value
        """

        value = self.dmm.measure()

        logger.debug(f"Current measurement: {value}")

        return float(value)

    def fetch_storage(
        self,
        samples: int = 200,
    ) -> list[float]:
        """
        Gets multiple measurement values.

        Args:
            <samples>   Store for a number of samples before returning

        Returns:
            List of measured values.
        """

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

    def set_display(
        self,
        scenario: Literal["STAT"]
    ) -> None:
        """
        Enables verious scenarious

        Args:
            <scenario>  STAT    sets the display to a statistic mode
        """
        ...

        logger.info("set_display() is not supported by the OWON XDM1041")

    def save_screenshot(
        self,
        filename: str = "TEMP"
    ) -> None:
        """
       Retrieves a screenshot.

        Args:
            <filename>     Label for the measured signal

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
        filename: str,
        nominal_value: float = 0.0,
        min_limit: float = 0.0,
        max_limit: float = 0.0,
        limit: int = 200,
    ) -> None:

        values = self.fetch_storage(
            samples=limit
        )

        return plot_data(
            x_data=list(range(len(values))),
            y_data=values,
            title=title,
            y_label=y_label,
            filename=filename,
            unit=self.mode,
            nominal_value=nominal_value,
            min_limit=min_limit,
            max_limit=max_limit,
        )
