import serial
import time
from loguru import logger
from serial.tools import list_ports
from typing import Protocol, Literal, runtime_checkable

class PEAKTECH_1885:

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        timeout: float = 1.0,
    ):

        self.address = "00"

        self.inst = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=timeout,
            write_timeout=timeout,
        )


    @classmethod
    def auto_connect(cls) -> "PEAKTECH_1885":

        ports = [p.device for p in list_ports.comports()]

        logger.info(f"Searching PeakTech on: {ports}")

        for port in ports:
            try:
                logger.debug(f"Trying {port}")

                ps = cls(port)

                resp = ps.command("GMAX")

                if resp:
                    logger.success(
                        f"PeakTech detected on {port}"
                    )
                    logger.info(
                        f"GMAX Response: {resp}"
                    )
                    return ps

                ps.close()

            except Exception as ex:
                logger.debug(
                    f"{port} failed: {ex}"
                )

        raise RuntimeError(
            "No PeakTech 1885 power supply found"
        )

    def command(
        self, 
        cmd: str, 
        arg: str = ""
    )-> list:
        
        tx = f"{cmd}{self.address}{arg}\r"

        self.inst.reset_input_buffer()

        self.inst.write(tx.encode("ascii"))
        self.inst.flush()

        time.sleep(0.1)

        raw = self.inst.read_all()

        text = raw.decode("ascii", errors="ignore")

        return [
            line.strip()
            for line in text.split("\r")
            if line.strip() and line.strip() != "OK"
        ]

    def close(self):
        if self.inst and self.inst.is_open:
            self.inst.close()

    # -----------------------------------------
    # SCPI Commands... not really but we still name it that
    # -----------------------------------------

    def _scpi_remote_on(self) -> None:
        """
        Disable front panel keypad and make PS to Remote Mode
        """

        logger.info("Lock front Panel")
        self.command("SESS")

    def _scpi_remote_off(self) -> None:
        """
        Enable front panel keypad and make PS to exit Remote Mode
        """
        
        logger.info("Unlock front Panel")
        self.command("ENDS")

    def _scpi_get_current_data(self) -> tuple[float, float]:
        """
        Get Voltage & Current reading from PS
        """

        resp = self.command("GETD")

        if not resp:
            return None

        data = resp[0]

        voltage = int(data[:4]) * 0.01
        current = int(data[4:8]) * 0.001

        return voltage, current
    
    def _scpi_get_target_data(self) -> tuple[float, float]:
        """
        Get Voltage & Current Set Value from PS
        """

        resp = self.command("GETS")

        if not resp:
            return None

        data = resp[0]

        voltage = int(data[:4]) * 0.01
        current = int(data[4:8]) * 0.001

        return voltage, current
    
    def _scpi_set_voltage(
            self,
            voltage: float = 0
    ) -> None:
        """
        Set Voltage Level

        Args:
            <voltage>   Float
        """

        logger.info(f"Set voltage to: {voltage}")

        voltage = f"{int(voltage*10):03d}"

        self.command(
            cmd = f"VOLT",
            arg= f"{voltage}"
        )

    def _scpi_set_current(
        self,
        current: float = 0
    ) -> None:
        """
        Set current Level

        Args:
            <current>   Float
        """

        logger.info(f"Set current to: {current}")

        current = f"{int(current*100):03d}"

        self.command(
            cmd = f"CURR",
            arg= f"{current}"
        )

    def _scpi_disable(
        self,
        disable: bool = True
    ) -> None:
        """
        Disable/Enable output

        Args:
            <disable>   True|False
        """

        logger.info(f"Set the power state to diable: {disable}")

        self.command(
            cmd = "SOUT",
            arg = int(disable)
        )

    # -----------------------------------------
    # API Commands
    # -----------------------------------------

    def identify(self) -> str:
        """
        Identifies the device.

        Returns:
            Result of *IDN?
        """
        
        logger.warning(f"Function not supported")

        
    def power_on_off(
        self,
        enable: Literal["ON", "OFF"] = "OFF"
    ) -> None:
        """
        Powers channel on

        Args:
            <enable>   ON|OFF
        """
        
        if enable == "OFF":
            self._scpi_disable(True)
        else:
            self._scpi_disable(False)

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

        self._scpi_set_voltage(voltage)
        self._scpi_set_current(current)

    def get_value(
        self
    ) -> tuple[float, float]:
        """
        Gets voltage and current of power supply

        Returns:
            <voltage>, <current>
        """
        voltage, current = self._scpi_get_current_data()

        return voltage, current

    def lock(
        self,
        lock_enable: bool = False
    ) -> None:
        """
        Locks the power supply

        Args:
            <lock_enable>   TRUE|FALSE
        """
        
        if lock_enable == True:
            self._scpi_remote_on()
        else:
            self._scpi_remote_off()