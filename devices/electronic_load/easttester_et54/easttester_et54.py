"""EastTester ET54 Series Electronic Load Controller."""

import sys
import time
from typing import Optional, List, Dict, Any
import pyvisa
from loguru import logger
from .channel import channel


class EastTesterET54:
    """EastTester ET54 Series Electronic Load.
    
    Multi-channel electronic load controller supporting 1 or 2 channel models.
    Provides SCPI command interface for load control and measurement.
    
    Attributes:
        ch1: Channel 1 object (always present)
        ch2: Channel 2 object (ET5420 models only)
        Channels: List of available channel objects
        idn: Device identification dictionary with model, SN, firmware, hardware
    """

    def __init__(
        self,
        resource_id: str,
        baudrate: int = 9600,
        eol_read: str = "\r\n",
        eol_write: str = "\n",
        query_delay: float = 0.2,
        timeout: int = 2000,
        model: Optional[str] = None,
    ) -> None:
        """Initialize ET54 electronic load.
        
        Args:
            resource_id: pyvisa resource ID string (e.g., "ASRL5::INSTR")
            baudrate: Serial communication speed (default 9600)
            eol_read: Line terminator for reading from device
            eol_write: Line terminator for writing to device
            query_delay: Delay after read/write operation in seconds
            timeout: Read timeout in milliseconds
            model: Optional model override (ET5410, ET5420, etc.)
                   Only needed if device *IDN? returns invalid response
        """
        rm = pyvisa.ResourceManager()
        self.connection = rm.open_resource(resource_id)
        self.connection.baud_rate = baudrate
        self.connection.query_delay = query_delay
        self.connection.timeout = timeout
        self.connection.read_termination = eol_read
        self.connection.write_termination = eol_write

        # Query device identification
        logger.info("Querying device identification")
        idn_response = self.connection.query("*IDN?")
        tmp = idn_response.split()
        self.idn: Dict[str, Any] = {}
        
        if len(tmp) == 4:
            (
                self.idn["model"],
                self.idn["SN"],
                self.idn["firmware"],
                self.idn["hardware"],
            ) = tmp
        elif len(tmp) == 3 and tmp[0] == "XXXXXX":
            # Handle Mustool branded device
            self.idn["model"] = tmp[0]
            self.idn["SN"] = None
            self.idn["firmware"] = tmp[1]
            self.idn["hardware"] = tmp[2]
        else:
            raise RuntimeError(f"Failed to parse device identification: {idn_response}")
            
        if model is not None:
            self.idn["model"] = model

        # Initialize channels based on model
        model_upper = self.idn["model"].upper()
        if model_upper in ("ET5406A+", "ET5407A+", "ET5410", "ET5410A+", "ET5411", "ET5411A+"):
            self.ch1 = channel("1", self.write, self.query)
            self.Channels = [self.ch1]
        elif model_upper in ("ET5420A+", "ET5420"):
            self.ch1 = channel("1", self.write, self.query)
            self.ch2 = channel("2", self.write, self.query)
            self.Channels = [self.ch1, self.ch2]
        else:
            raise RuntimeError(f"Device model '{self.idn['model']}' not supported")

        logger.info(f"ET54 initialized: {self.idn['model']} with {len(self.Channels)} channel(s)")

    @classmethod
    def auto_connect(cls, **kwargs: Any) -> "EastTesterET54":
        """Automatically detect and connect to first available ET54 device.
        
        Scans all serial ports for ET54 electronic loads and connects to the first one found.
        
        Returns:
            ET54 instance connected to detected device
            
        Raises:
            RuntimeError: If no ET54 device found on serial ports
        """
        logger.info("Auto-detecting ET54 electronic load on serial ports")
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()

        for resource_id in resources:
            if not resource_id.startswith("ASRL"):
                continue

            try:
                inst = rm.open_resource(resource_id)
                inst.timeout = kwargs.get("timeout", 500)

                response = inst.query("*IDN?")
                inst.close()

                if isinstance(response, str):
                    model = response.split()[0]

                    if model.upper().startswith("ET54") or model == "XXXXXX":
                        logger.success(f"ET54 found at {resource_id}: {response}")
                        return cls(resource_id, **kwargs)

            except Exception as e:
                logger.debug(f"Skipping {resource_id}: {e}")

        raise RuntimeError("No ET54 device found on available serial ports")

    def __del__(self) -> None:
        """Close connection on deletion."""
        try:
            self.connection.close()
        except Exception:
            pass

    def __str__(self) -> str:
        """Return device information as formatted string."""
        info = (
            f"Model:          {self.idn['model']}\n"
            f"Serial:         {self.idn['SN']}\n"
            f"Firmware:       {self.idn['firmware']}\n"
            f"Hardware:       {self.idn['hardware']}\n\n"
        )
        info += str(self.ch1)
        return info
    


    # =========================================
    # Core Commands
    # =========================================

    def write(self, cmd: str) -> None:
        """Send SCPI command and verify execution status.
        
        Args:
            cmd: SCPI command string
            
        Raises:
            RuntimeError: If command execution fails
        """
        logger.debug(f"Sending command: {cmd}")
        response = self.connection.query(cmd)
        time.sleep(self.connection.query_delay)
        
        if response == "Rexecu success":
            return
        elif response == "Rcmd err":
            raise RuntimeError(f"Unknown SCPI command: '{cmd}'")
        elif response == "Rexecu err":
            raise RuntimeError(f"SCPI command execution failed: '{cmd}'")
        else:
            raise RuntimeError(f"Unexpected response to '{cmd}': {response}")

    def query(self, 
              cmd: str, 
              nrows: int = 1, 
              timeout: Optional[int] = None) -> Any:
        """Send SCPI query command and read response.
        
        Args:
            cmd: SCPI query command string
            nrows: Number of response lines to read (default 1)
            timeout: Optional temporary timeout in milliseconds for this query
            
        Returns:
            Single response string if nrows=1, list of strings if nrows>1
            None if command fails
        """
        if timeout is not None:
            original_timeout = self.connection.timeout
            self.connection.timeout = timeout

        try:
            logger.debug(f"Querying: {cmd}")
            self.connection.write(cmd)
            time.sleep(self.connection.query_delay)
            
            responses = []
            for i in range(nrows):
                value = self.connection.read()
                time.sleep(self.connection.query_delay)
                
                if value == "Rcmd err":
                    logger.error(f"Query failed: '{cmd}'")
                    return None
                    
                responses.append(value)
                
            return responses if len(responses) > 1 else responses[0]
            
        finally:
            if timeout is not None:
                self.connection.timeout = original_timeout

    def close(self) -> None:
        """Close connection to device."""
        logger.info("Closing connection to ET54")
        self.connection.close()

    def beep(self) -> None:
        """Trigger device beep."""
        logger.debug("Sending beep command")
        self.write("SYST:BEEP")

    def reset(self) -> None:
        """Reset device to factory defaults."""
        logger.info("Resetting ET54 to default state")
        self.connection.write("RST")

    def trigger(self) -> None:
        """Send software trigger event."""
        logger.debug("Sending trigger event")
        self.connection.write("TRG")

    def unlock_local_interface(self) -> None:
        """Unlock local interface to enable front panel buttons.
        
        Note: Sending any SCPI command will lock the interface again.
        """
        logger.info("Unlocking local interface")
        self.write("SYST:LOCA")

    def get_fan_state(self) -> Optional[str]:
        """Query cooling fan state.
        
        Returns:
            Fan state string or None if query fails
        """
        return self.query("SELF:FAN?")
    


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
        """Enable all channels."""
        logger.info("Enabling all channels")
        for ch in self.Channels:
            ch.on()

    def load_off(self) -> None:
        """Disable all channels."""
        logger.info("Disabling all channels")
        for ch in self.Channels:
            ch.off()



    # =========================================
    # Configuration
    # =========================================


    def set_mode(self, mode: str = "CC", channel: int = 1) -> None:
        """Set load operating mode on selected channel.

        Args:
            mode: Operating mode. Options include:
                - "CC": Constant Current (default)
                - "CV": Constant Voltage
                - "CP": Constant Power
                - "CR": Constant Resistance
                See device manual for all available modes.
            channel: Channel number (1 or 2)
        """
        mode = mode.upper()
        logger.info(f"Setting CH{channel} mode to {mode}")
        self.Channels[channel - 1].set_function(mode)

    def set_current(self, 
                    current: float, 
                    channel: int = 1,) -> None:
        """
        Set current on selected channel.

        Args:
            current: Current in amperes
            channel: Channel number
        """

        logger.info(f"Setting CH{channel} current to {current} A")

        self.Channels[channel - 1].set_current(current)



    # =========================================
    # Measurement
    # =========================================


    def fetch(
        self,
        channel: int = 1,
    ) -> Optional[tuple[float, float]]:
        """
        Read voltage and current from selected channel.

        Returns:
            (voltage, current)
        """

        logger.info(
            f"Fetching measurements from CH{channel}"
        )

        ch = self.Channels[channel - 1]

        voltage = ch.get_voltage()
        current = ch.get_current()

        return (
            float(voltage),
            float(current),
        )
