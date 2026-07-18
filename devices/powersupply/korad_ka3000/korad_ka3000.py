import serial
import time

from loguru import logger
from serial.tools import list_ports
from typing import Literal


class KORAD_KA3010DS:

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        timeout: float = 1.0,
    ):

        self.inst = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout,
            write_timeout=timeout,
        )

    # --------------------------------------------------
    # Connection Handling
    # --------------------------------------------------

    @classmethod
    def auto_connect(cls) -> "KORAD_KA3010DS":

        ports = [p.device for p in list_ports.comports()]

        logger.info(
            f"Searching Korad power supply on: {ports}"
        )

        for port in ports:

            try:

                ps = cls(port)

                ident = ps.identify()

                if ident:

                    logger.success(
                        f"Korad detected on {port}"
                    )

                    logger.info(
                        f"Identification: {ident}"
                    )

                    return ps

                ps.close()

            except Exception as ex:

                logger.debug(
                    f"{port} failed: {ex}"
                )

        raise RuntimeError(
            "No Korad KA3010DS found"
        )

    def close(self):

        if self.inst and self.inst.is_open:
            self.inst.close()

    # --------------------------------------------------
    # Low Level Communication
    # --------------------------------------------------

    def write(
        self,
        command: str
    ) -> None:

        logger.debug(
            f"TX -> {command}"
        )

        self.inst.write(
            command.encode("ascii")
        )

        self.inst.flush()

    def query(
        self,
        command: str,
        delay: float = 0.1,
    ) -> str:

        self.inst.reset_input_buffer()

        self.write(command)

        time.sleep(delay)

        response = (
            self.inst.read_all()
            .decode(
                "ascii",
                errors="ignore"
            )
            .strip()
        )

        logger.debug(
            f"RX <- {response}"
        )

        return response

    # --------------------------------------------------
    # Korad Commands
    # --------------------------------------------------

    def _scpi_identify(self) -> str:

        return self.query("*IDN?")

    def _scpi_set_voltage(
        self,
        voltage: float,
    ) -> None:

        logger.info(
            f"Set voltage to: {voltage:.2f} V"
        )

        self.write(
            f"VSET1:{voltage:.2f}"
        )

    def _scpi_set_current(
        self,
        current: float,
    ) -> None:

        logger.info(
            f"Set current to: {current:.3f} A"
        )

        self.write(
            f"ISET1:{current:.3f}"
        )

    def _scpi_get_voltage(
        self,
    ) -> float:

        response = self.query(
            "VOUT1?"
        )

        return float(response)

    def _scpi_get_current(
        self,
    ) -> float:

        response = self.query(
            "IOUT1?"
        )

        return float(response)

    def _scpi_get_target_voltage(
        self,
    ) -> float:

        response = self.query(
            "VSET1?"
        )

        return float(response)

    def _scpi_get_target_current(
        self,
    ) -> float:

        response = self.query(
            "ISET1?"
        )

        return float(response)

    def _scpi_output(
        self,
        enable: bool,
    ) -> None:

        logger.info(
            f"Output enable: {enable}"
        )

        self.write(
            "OUT1"
            if enable
            else "OUT0"
        )

    def _scpi_status(
        self,
    ) -> str:

        return self.query(
            "STATUS?"
        )

    # --------------------------------------------------
    # API Commands
    # --------------------------------------------------

    def identify(
        self,
    ) -> str:

        return self._scpi_identify()

    def power_on_off(
        self,
        enable: Literal["ON", "OFF"] = "OFF"
    ) -> None:

        self._scpi_output(
            enable == "ON"
        )

    def set_values(
        self,
        voltage: float = 0.0,
        current: float = 0.0,
    ) -> None:

        self._scpi_set_voltage(
            voltage
        )

        self._scpi_set_current(
            current
        )

    def get_value(
        self,
    ) -> tuple[float, float]:

        voltage = self._scpi_get_voltage()

        current = self._scpi_get_current()

        return (
            voltage,
            current,
        )

    def get_set_values(
        self,
    ) -> tuple[float, float]:

        voltage = (
            self._scpi_get_target_voltage()
        )

        current = (
            self._scpi_get_target_current()
        )

        return (
            voltage,
            current,
        )

    def lock(
        self,
        lock_enable: bool = False,
    ) -> None:

        logger.warning(
            "Front panel lock not implemented for Korad"
        )