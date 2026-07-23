import serial
import time
from loguru import logger
from serial.tools import list_ports
from typing import Literal


class PEAKTECH_6070:

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        timeout: float = 1.0,
    ):

        self.address = 0x01

        self.inst = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=timeout,
            write_timeout=timeout,
        )

        self._voltage = 0
        self._current = 0

    # ------------------------------------------------------
    # CRC16 MODBUS
    # ------------------------------------------------------

    @staticmethod
    def crc16_modbus(data: bytes) -> bytes:

        crc = 0xFFFF

        for byte in data:

            crc ^= byte

            for _ in range(8):

                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1

        return crc.to_bytes(2, "little")

    # ------------------------------------------------------
    # Frame Handling
    # ------------------------------------------------------

    def _send_frame(
        self,
        payload: bytes,
    ) -> bytes:

        frame = (
            payload
            + self.crc16_modbus(payload)
            + bytes([0xFD])
        )

        self.inst.reset_input_buffer()

        self.inst.write(frame)
        self.inst.flush()

        time.sleep(0.1)

        response = self.inst.read_all()

        return response

    # ------------------------------------------------------
    # Auto Detection
    # ------------------------------------------------------

    @classmethod
    def auto_connect(cls) -> "PEAKTECH_6070":

        ports = [p.device for p in list_ports.comports()]

        logger.info(
            f"Searching PeakTech 6070 on {ports}"
        )

        for port in ports:

            try:

                ps = cls(port)

                values = ps._read_all()

                if values:

                    logger.success(
                        f"PeakTech 6070 found on {port}"
                    )

                    return ps

                ps.close()

            except Exception as ex:

                logger.debug(
                    f"{port} failed: {ex}"
                )

        raise RuntimeError(
            "No PeakTech 6070 detected"
        )

    # ------------------------------------------------------
    # Low Level Commands
    # ------------------------------------------------------

    def _write_register(
        self,
        register: int,
        value: int
    ):

        payload = bytes([
            0xF7,
            self.address,
            0x0A,
            register,
            0x01,
            (value >> 8) & 0xFF,
            value & 0xFF
        ])

        self._send_frame(payload)

    def _read_all(self):

        payload = bytes([
            0xF7,
            self.address,
            0x03,
            0x04,
            0x03,
        ])

        rx = self._send_frame(payload)

        #logger.warning(rx.hex(" "))

        if len(rx) < 14:
            return None

        status = (rx[5] & 0x20)
        voltage = (rx[7] << 8) | rx[8]
        current = (rx[9] << 8) | rx[10]

        return (
            bool(status),
            voltage / 100.0,
            current / 1000.0,
        )

    # ------------------------------------------------------
    # SCPI-like
    # ------------------------------------------------------

    def _scpi_set_voltage(
        self,
        voltage: float
    ):

        logger.info(
            f"Set voltage: {voltage}V"
        )

        value = int(voltage * 100)

        self._write_register(
            register=0x09,
            value=value
        )

    def _scpi_set_current(
        self,
        current: float
    ):

        logger.info(
            f"Set current: {current}A"
        )

        value = int(current * 1000)

        self._write_register(
            register=0x0A,
            value=value
        )

    def _scpi_output(
        self,
        enable: bool
    ):

        self._write_register(
            register=0x1E,
            value=1 if enable else 0
        )
    
    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def identify(self):
        """
        Identifies the device.

        Returns:
            Result of *IDN?
        """
        
        logger.warning(f"Function not supported")

        return "PeakTech 6070"

    def set_values(
        self,
        voltage: float = 0,
        current: float = 0
    ) -> None:
        """
        Sets voltage and current of power supply

        Args:
            <voltage>
            <current>
        """

        self._voltage = voltage
        self._current = current

        self._scpi_set_voltage(voltage)
        self._scpi_set_current(current)

    def power_on_off(
        self,
        enable: Literal["ON", "OFF"] = "OFF"
    ) -> None:
        """
        Powers channel on

        Args:
            <enable>   ON|OFF
        """

        self._scpi_output(
            enable == "ON"
        )

    def get_value(
        self
    ) -> tuple[float, float]:
        """
        Gets voltage and current of power supply

        Returns:
            <voltage>, <current>
        """

        _, voltage, current = self._read_all()

        return voltage, current

    def close(self):

        if self.inst and self.inst.is_open:
            self.inst.close()

    def lock(
        self,
        lock_enable: bool = False
    ) -> None:
        """
        Locks the power supply

        Args:
            <lock_enable>   TRUE|FALSE
        """

        logger.warning(f"Function not supported")
        
    def get_state(
        self
    ) -> Literal["ON", "OFF"]:
        """
        Gets state of PSU

        Returns:
            ON|OFF
        """

        status, _, _ = self._read_all()

        return "ON" if status else "OFF"