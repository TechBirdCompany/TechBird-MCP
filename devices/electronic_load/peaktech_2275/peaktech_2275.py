"""PeakTech 2275 Electronic Load Controller"""

from typing import Optional, Tuple, Literal
from utils.utils import to_float
from loguru import logger
import serial
from serial.tools import list_ports
import time

class PEAKTECH_2275:
    """PeakTech 2275 Electronic Load.
    
    Serial-based electronic load controller. py-visa is not compatible
    with some commands like on/off control.
    
    Attributes:
        inst: Serial connection instance
        
    Notes:
        - Baudrate: 38400
        - Format: 8N1 (8 bits, no parity, 1 stop bit)
        - No flow control
    """

    def __init__(
        self,
        port: str = "COM9",
        baudrate: int = 38400,
        timeout: float = 2.0,
    ) -> None:
        """Initialize connection to PeakTech 2275 device.
        
        Args:
            port: Serial port name (e.g., "COM9")
            baudrate: Communication speed in baud
            timeout: Read timeout in seconds
        """
        self.inst = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout,
        )

    @classmethod
    def auto_connect(
        cls,
        baudrate: int = 38400,
        timeout: float = 10.0,
    ) -> "PEAKTECH_2275":
        """
        Automatically detect and connect to the first
        available PeakTech electronic load.

        Returns:
            Connected PeakTech2275 instance

        Raises:
            RuntimeError:
                If no compatible device is found
        """

        logger.info("Auto-detecting PeakTech electronic load...")

        for attempt in range(1, 4):
            logger.info(f"Auto-connect attempt {attempt}/3")

            ports = list(list_ports.comports())

            if not ports:
                logger.warning("No serial ports detected")
            else:
                for port in ports:
                    logger.debug(f"Testing serial port: {port.device}")

                    try:
                        logger.debug(f"Opening {port.device}")

                        ser = serial.Serial(
                            port=port.device,
                            baudrate=baudrate,
                            timeout=1,
                            write_timeout=1,
                        )

                        logger.debug(f"Sending IDN query to {port.device}")

                        ser.reset_input_buffer()
                        ser.write(b"*IDN?\r\n")

                        response = (
                            ser.readline()
                            .decode(errors="ignore")
                            .strip()
                        )

                        logger.debug(f"Received '{response}'")
                        ser.close()

                        if (
                            "PEAKTECH" in response.upper()
                            and "LOAD" in response.upper()
                        ):
                            logger.success(
                                f"PeakTech electronic load found on {port.device}"
                            )

                            return cls(
                                port=port.device,
                                baudrate=baudrate,
                                timeout=timeout,
                            )

                    except Exception as e:
                        logger.debug(f"Skipping {port.device}: {e}")

            logger.warning(
                f"No PeakTech electronic load found on attempt {attempt}/3"
            )

            if attempt < 3:
                time.sleep(1)

        logger.error("No PeakTech electronic load found after 3 attempts")
        raise RuntimeError(
            "No PeakTech electronic load found after 3 attempts"
        )

    # =========================================
    # Core Commands
    # =========================================

    def write(self, cmd: str) -> None:
        """Send command without expecting response.
        
        Args:
            cmd: Command string to send
        """
        try:
            logger.info(f"Sending command: {cmd}")
            self.inst.write(f"{cmd}\r\n".encode())
            self.inst.flush()
        except Exception as e:
            logger.error(f"Command failed '{cmd}': {e}")

    def query(self, cmd: str) -> Optional[str]:
        """Send command and read response.
        
        Args:
            cmd: Query command string
            
        Returns:
            Response string or None if error occurred
        """
        try:
            logger.info(f"Querying: {cmd}")
            self.inst.reset_input_buffer()
            self.inst.write(f"{cmd}\r\n".encode())
            self.inst.flush()
            
            response = (
                self.inst.readline()
                .decode(errors="ignore")
                .strip()
            )
            
            logger.info(f"Response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Query failed '{cmd}': {e}")
            return None

    def close(self) -> None:
        """Close device connection."""
        try:
            self.inst.close()
            logger.info("Connection closed")
        except Exception as e:
            logger.error(f"Close failed: {e}")

    # =========================================
    # SCPI Commands
    # =========================================

    def _scpi_identify(self) -> Optional[str]:
        """
        Query device identification.
        
        Returns:
            Device ID string or None if failed
        """
        
        logger.info("Identifying device")
        
        return self.query("*IDN?")

    def _scpi_load_on(self) -> None:
        """
        Enable electronic load.
        """
        
        logger.info("Enabling load")
        
        self.write("LOAD ON")

    def _scpi_load_off(self) -> None:
        """
        Disable electronic load.
        """
        
        logger.info("Disabling load")
        
        self.write("LOAD OFF")

    def _scpi_get_load_state(self) -> Optional[str]:
        """
        Query current load state.
        
        Returns:
            Load state string or None if failed
        """
        
        logger.info("Querying load state")
        
        state = self.query("LOAD:STATE?")
        
        if state is None:
            state = self.query("LOAD?")
        
        return state

    def _scpi_set_mode(
        self, 
        mode: Literal["CC", "CV", "CP", "CR", "SH", "BAT", "TRAN"] = "CC", 
    ) -> None:
        """
        Set load operating mode.
        
        Args:
            <mode>  Operating mode. Options include:
                    "CC":       Constant Current (default)
                    "CV":       Constant Voltage
                    "CP":       Constant Power
                    "CR":       Constant Resistance
                    "SH":       Circuit Short
                    "BAT":      Battery Test
                    "TRAN":     Dynamic Test
        """

        logger.info(f"Setting mode to {mode}")
        
        self.write(f"LOAD:MODE {mode}")

    def _scpi_set_current(
        self, 
        current: 
        Optional[float] = None
    ) -> None:
        """
        Set target current for constant current mode.
        
        Args:
            <current>   Current value in amperes
        """

        logger.info(f"Setting current to {current}A")

        self.write(f"LOAD:CURR {current}")

    def _scpi_fetch(self) -> Optional[Tuple[float, float]]:
        """
        Fetch current measurement values from device.
        
        Retrieves voltage and current measurements in the current mode
        (CC, CV, CR, CP, etc).
               
        Returns:
            Tuple of (voltage, current) as floats, or None if error occurred
            
        """
        response = self.query("FETCH?")
        
        if not response:
            logger.warning("No response from FETCH command")
            return None
        
        logger.debug(f"FETCH raw response: {repr(response)}")
        
        try:
            values = response.split(",")
            if len(values) < 2:
                logger.error(f"Invalid FETCH response format: {response}")
                return None
            
            voltage_str = values[0].strip().rstrip('V')
            current_str = values[1].strip().rstrip('A')
            
            voltage = float(voltage_str)
            current = float(current_str)
            
            logger.debug(f"Parsed: {voltage}V, {current}A")
            return (voltage, current)
            
        except ValueError as e:
            logger.error(f"Failed to parse FETCH response '{response}': {e}")
            return None
        
    # =========================================
    # SCPI Commands
    # =========================================

    def identify(
        self
    ) -> str:
        """
        Query device identification.
        
        Returns:
            Result of *IDN?
        """

        return self._scpi_identify()
    
    def load_on(
        self,
        channel: Optional[Literal[1, 2]] = 1
    ) -> None:
        """
        Enable electronic load.
        """

        self._scpi_load_on()

    def load_off(
        self,
        channel: Optional[Literal[1, 2]] = 1
    ) -> None:
        """
        Disable electronic load.
        """

        self._scpi_load_off()

    def set_mode(
        self,
        mode: Literal["CC"],
        channel: Optional[Literal[1, 2]] = 1
    ) -> None:
        """
        Configure operating mode.

        Args:
            <mode>      Mode of channel for eload
                        [CC]

            <channel>   Optional parameter as most do have only one channel
                        But beside this; Number of channel
        """

        self._scpi_set_mode(
            mode=mode
        )
    
    def set_current(
        self,
        current: float,
        channel: Optional[Literal[1, 2]] = 1
    ) -> None:
        """
        Configure load current.

        Args:
            <current>    Set current for channel... as currently on CC is defined
                        This definition need to be changed, when other modes should
                        be supported
                        [CC]

            <channel>    Optional parameter as most do have only one channel
                        But beside this; Number of channel
        """

        self._scpi_set_current(
            current=current
        )

    def fetch(
        self,
        channel: Optional[Literal[1, 2]] = 1
    ) -> tuple[float, float]:
        """
        Read measurement values.

        Args:
            <channel>   Optional parameter as most do have only one channel
                        But beside this; Number of channel

        Returns:
            Returns volage and current, which are mostly the returned values in SCPI command guides
            [voltage, current]
        """

        return self._scpi_fetch()
    
    def close(self) -> None:
        """
        Close connection.
        """

        self.close
