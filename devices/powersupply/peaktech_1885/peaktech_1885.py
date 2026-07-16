"""PeakTech 1885 Power Supply"""

from typing import Optional, Tuple, Literal
from utils.utils import to_float
from loguru import logger
import serial
from serial.tools import list_ports
import time

class PEAKTECH_1885:
    """PeakTech 1885 Electronic Load.
    
    Serial-based electronic load controller. py-visa is not compatible
    with some commands like on/off control.
    
    Attributes:
        inst: Serial connection instance
        
    Notes:
        - Baudrate: 9600
        - Format: 8N1 (8 bits, no parity, 1 stop bit)
        - No flow control
    """

    def __init__(
        self,
    ) -> None:
        
        self.address = 0

    @classmethod
    def auto_connect(
        cls,
        baudrate: int = 9600,
        timeout: float = 10.0,
    ) -> "PEAKTECH_1885":
        """
        Automatically detect and connect to a PeakTech 1885.
        """

        logger.info("Auto-detecting PeakTech 1885...")

        for attempt in range(1, 4):

            logger.info(
                f"Auto-connect attempt {attempt}/3"
            )

            for port in list_ports.comports():

                try:

                    with serial.Serial(
                        port=port.device,
                        baudrate=baudrate,
                        timeout=1,
                        write_timeout=1,
                    ) as ser:

                        for addr in range(1, 256):

                            address = f"{addr:02X}"

                            try:

                                ser.reset_input_buffer()

                                cmd = f"GMAX{address}\r"

                                logger.debug(
                                    f"{port.device}: {cmd.strip()}"
                                )

                                ser.write(cmd.encode())
                                ser.flush()

                                response = (
                                    ser.read_until(b"OK\r")
                                    .decode(errors="ignore")
                                    .strip()
                                )

                                if "OK" in response:

                                    logger.success(
                                        f"PeakTech 1885 found "
                                        f"on {port.device} "
                                        f"(address={address})"
                                    )

                                    device = cls(
                                        port=port.device,
                                        baudrate=baudrate,
                                        timeout=timeout,
                                    )

                                    device.address = address

                                    return device

                            except Exception:
                                continue

                except Exception as e:
                    logger.debug(
                        f"Skipping {port.device}: {e}"
                    )

            if attempt < 3:
                time.sleep(1)

        raise RuntimeError(
            "No PeakTech 1885 found"
        )

    # =========================================
    # Core Commands
    # =========================================

    def write(
        self,
        cmd: str,
    ) -> None:
        """
        Send command to power supply.

        Args:
            <cmd>   Command
        """

        try:

            full_cmd = f"{cmd} {self.address}"

            logger.info(f"Sending command: {full_cmd}")

            self.inst.reset_input_buffer()
            self.inst.write(f"{full_cmd}\r".encode())
            self.inst.flush()

        except Exception as e:
            logger.error(
                f"Command failed '{full_cmd}': {e}"
            )


    def query(
        self,
        cmd: str,
    ) -> Optional[str]:
        """
        Send query and return response.

        Args:
            <cmd>   Command
        
        Returns:
            Returns the response for the command
        """

        try:

            full_cmd = f"{cmd} {self.address}"

            logger.info(f"Querying: {full_cmd}")

            self.inst.reset_input_buffer()

            self.inst.write(f"{full_cmd}\r".encode())
            self.inst.flush()

            response = (
                self.inst.read_until(b"OK\r")
                .decode(errors="ignore")
                .strip()
            )

            logger.info(f"Response: {response}")

            return response

        except Exception as e:
            logger.error(
                f"Query failed '{full_cmd}': {e}"
            )

            return None
        
    def close(self) -> None:
        """
        Close device connection.
        """

        try:

            if self.inst is not None and self.inst.is_open:
                logger.info("Closing connection")
                self.inst.close()

            logger.info("Connection closed")

        except Exception as e:
            logger.error(f"Close failed: {e}")

    # =========================================
    # SCPI Commands
    # =========================================

    def _scpi_sess(self) -> None:
        """
        Disable front panel keypad and make PS to
        Remote Mode
        """

        self.write(f"SESS {self.address}")

    def _scpi_ends(self) -> None:
        """
        Enable front panel keypad and make PS to
        exit Remote Mode
        """

        self.write(f"ENDS {self.address}")

    def _scpi_get_value(self) -> Tuple[float, float]:
        """
        Get Voltage & Current reading from PS
        """

        voltage, current = self.query(f"GETS {self.addrress}")

        return voltage, current
    
    def _scpi_set_voltage(
        self,
        voltage: int = 0
    ) -> None:
        """
        Set Voltage Level XXX-Max. Output Rating
        Voltage = XX.X V

        Args:
            <voltage>   Voltage/10
        """

        self.write(f"VOLT {self.address} {voltage}")

    def _scpi_set_current(
        self,
        current: int = 0
    ) -> None:
        """
        Set current Level XXX-Max. Output Rating
        Current = XX.X A

        Args:
            <current>   Current/10
        """

        self.write(f"CURR {self.address} {current}")

    def _scpi_enable(
        self,
        disable: bool= True
    ) -> None:
        """
        Enable/Disable Output of PS

        Args:
            <state>     True:   Disable
                        Fals:   Enable 
        """
    
        self.write(f"SOUT {self.address} {str(int(disable))}")