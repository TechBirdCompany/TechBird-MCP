import serial
import time
from loguru import logger


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
    def connect(
        cls,
        port: str = "COM23",
    ) -> "PEAKTECH_1885":

        ps = cls(port)

        try:
            resp = ps.command("GMAX")

            logger.success(
                f"PeakTech detected on {port}"
            )

            logger.info(f"GMAX Response: {resp}")

            return ps

        except Exception:
            ps.close()
            raise

    def command(
        self,
        cmd: str,
        arg: str = "",
    ) -> list:

        tx = f"{cmd}{self.address}{arg}\r"

        logger.debug(f"TX: {repr(tx)}")

        self.inst.reset_input_buffer()

        self.inst.write(tx.encode())
        self.inst.flush()

        raw = (
            self.inst.read_until(b"OK")
            .decode(errors="ignore")
            .strip()
        )

        logger.debug(f"RAW RX: {repr(raw)}")

        response = [
            x.strip()
            for x in raw.split("\r")
            if x.strip() and x.strip() != "OK"
        ]

        return response

    def close(self):

        if self.inst and self.inst.is_open:
            self.inst.close()

    # -----------------------------------------
    # Device Commands
    # -----------------------------------------

    def remote_on(self):
        self.command("SESS")

    def remote_off(self):
        self.command("ENDS")

    def set_voltage(
        self,
        voltage: float,
    ):
        value = f"{int(voltage * 10):03d}"
        self.command("VOLT", value)

    def set_current(
        self,
        current: float,
    ):
        value = f"{int(current * 10):03d}"
        self.command("CURR", value)

    def output_on(self):
        self.command("SOUT", "1")

    def output_off(self):
        self.command("SOUT", "0")

    def get_values(self):

        resp = self.command("GETD")

        if not resp:
            return None

        data = resp[0]

        voltage = int(data[:4]) * 0.01
        current = int(data[4:8]) * 0.0001

        return voltage, current