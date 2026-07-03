from typing import Optional, Tuple
from utils.utils import to_float
from loguru import logger
import serial
from serial.tools import list_ports

class PeakTech2275:
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
    ) -> "PeakTech2275":
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

        ports = list(list_ports.comports())

        if not ports:
            logger.error("No serial ports detected")
            raise RuntimeError("No serial ports available")

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
                continue

        logger.error("No PeakTech electronic load found")
        raise RuntimeError("No PeakTech electronic load found")



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
    # Identification
    # =========================================

    def identify(self) -> Optional[str]:
        """Query device identification.
        
        Returns:
            Device ID string or None if failed
        """
        logger.info("Identifying device")
        return self.query("*IDN?")



    # =========================================
    # Load Control
    # =========================================

    def load_on(self) -> None:
        """Enable electronic load."""
        logger.info("Enabling load")
        self.write("LOAD ON")

    def load_off(self) -> None:
        """Disable electronic load."""
        logger.info("Disabling load")
        self.write("LOAD OFF")

    def get_load_state(self) -> Optional[str]:
        """Query current load state.
        
        Returns:
            Load state string or None if failed
        """
        logger.info("Querying load state")
        return self.query("LOAD?")



    # =========================================
    # Configuration
    # =========================================

    def set_mode(self, mode: str = "CC", channel: Optional[int] = None) -> None:
        """Set load operating mode.
        
        Args:
            mode: Operating mode. Options include:
                - "CC": Constant Current (default)
                - "CV": Constant Voltage
                
            channel: Channel number (ignored - PeakTech is single-channel,
                    provided for ET54 compatibility)
        
        See device manual for all available modes.
        """
        logger.info(f"Setting mode to {mode}")
        self.write(f"LOAD:MODE {mode}")

    def set_current(self, current: float, channel: Optional[int] = None) -> None:
        """Set target current for constant current mode.
        
        Args:
            current: Current value in amperes
            
            channel: Channel number (ignored - PeakTech is single-channel,
                    provided for ET54 compatibility)
        """
        logger.info(f"Setting current to {current}A")
        self.write(f"LOAD:CURR {current}")



    # =========================================
    # Measurement
    # =========================================

    def fetch(self, channel: Optional[int] = None) -> Optional[Tuple[float, float]]:
        """Fetch current measurement values from device.
        
        Retrieves voltage and current measurements in the current mode
        (CC, CV, CR, CP, etc).
        
        Args:
            channel: Channel number (ignored - PeakTech is single-channel,
                    provided for ET54 compatibility)
        
        Returns:
            Tuple of (voltage, current) as floats, or None if error occurred
            
        Raises:
            ValueError: If response cannot be parsed as floats
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
            
            # Strip units (V, A) from values like "4.959V" and "0.498A"
            voltage_str = values[0].strip().rstrip('V')
            current_str = values[1].strip().rstrip('A')
            
            voltage = float(voltage_str)
            current = float(current_str)
            
            logger.debug(f"Parsed: {voltage}V, {current}A")
            return (voltage, current)
            
        except ValueError as e:
            logger.error(f"Failed to parse FETCH response '{response}': {e}")
            return None