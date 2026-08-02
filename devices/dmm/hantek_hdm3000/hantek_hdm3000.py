import pyvisa
from typing import Literal

from loguru import logger
from utils.utils import plot_data

nplc_map = {
    "FAST": 0.02,
    "MID": 1,
    "SLOW": 10,
}

class HANTEK_HDM3000:

    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.inst = None

        try:
            self.inst = self.autoconnect()
            self.write("*RST")
        except Exception as exc:
            logger.warning(f"Could not connect to Hantek DMM: {exc}")

        if self.inst is not None:
            self.inst.timeout = 30000

        self.mode = "V"
        self.range = 0
        self.speed = "MID"

        if self.inst is not None:
            self.setup(
                mode="V",
                range=0,
                speed="MID",
            )

    # -------------------------------------------------
    # CONNECTION
    # -------------------------------------------------

    def autoconnect(self):
        resources = self.rm.list_resources()

        logger.info(f"Found VISA resources: {resources}")

        for resource in resources:
            try:
                inst = self.rm.open_resource(resource)
                inst.timeout = 50

                idn = inst.query("*IDN?").strip()
                logger.info(f"{resource} -> {idn}")

                if "HANTEK" in idn.upper() or "HDM" in idn.upper():
                    logger.success(f"Connected to {idn}")
                    return inst

                inst.close()
            except Exception as exc:
                logger.debug(f"Skipping {resource}: {exc}")

        raise ConnectionError("No Hantek HDM3000 found")

    def _release_resource(self):
        inst = self.inst
        self.inst = None

        if inst is None:
            return

        try:
            inst.write("SYST:LOC")
        except Exception:
            pass

        try:
            inst.write("*CLS")
        except Exception:
            pass

        try:
            inst.clear()
        except Exception:
            pass

        try:
            inst.close()
        except Exception:
            pass

    def close(self):
        logger.info("Closing Hantek connection")
        self._release_resource()

    # -------------------------------------------------
    # BASIC I/O
    # -------------------------------------------------

    def write(self, cmd: str):
        if self.inst is None:
            raise RuntimeError("Hantek DMM not connected")

        logger.info(f"Write -> {cmd}")
        self.inst.write(cmd)

    def query(self, cmd: str) -> str:
        if self.inst is None:
            raise RuntimeError("Hantek DMM not connected")

        logger.info(f"Query -> {cmd}")
        return self.inst.query(cmd).strip()

    # -------------------------------------------------
    # HELPERS
    # -------------------------------------------------

    def get_voltage_range(self, voltage: float) -> str:
        voltage = abs(voltage)

        if voltage <= 0.1:
            return "0.1"
        elif voltage <= 1:
            return "1"
        elif voltage <= 10:
            return "10"
        elif voltage <= 100:
            return "100"
        return "1000"

    def get_current_range(self, current: float) -> str:
        current = abs(current)

        if current <= 100e-6:
            return "100E-6"
        elif current <= 1e-3:
            return "1E-3"
        elif current <= 10e-3:
            return "10E-3"
        elif current <= 100e-3:
            return "100E-3"
        elif current <= 1:
            return "1"
        elif current <= 3:
            return "3"
        return "10"

    def _parse_values(self, response: str) -> list[float]:
        if response is None:
            return []

        if isinstance(response, bytes):
            response = response.decode("ascii", errors="ignore")

        response = str(response).strip()

        if not response:
            return []

        if response.startswith("#"):
            digits = int(response[1])
            header_len = 2 + digits
            payload_len = int(response[2:header_len])
            response = response[header_len:header_len + payload_len]

        try:
            return [float(v) for v in response.split(",") if v.strip()]
        except Exception as exc:
            logger.warning(f"Failed parsing values: {exc}")
            return []

    # -------------------------------------------------
    # SCPI
    # -------------------------------------------------

    def _scpi_abort(self):
        self.write("ABOR")

    def _scpi_initiate(self):
        self.write("INIT")

    def _scpi_fetch(self):
        self.write("FETC?")

        try:
            raw = self.inst.read_raw()

            print("RAW LEN:", len(raw))
            print(repr(raw))

            return raw.decode("ascii")
        except Exception as exc:
            print("READ_RAW FAILED:", exc)
            raise

    def _scpi_read(self):
        return self.query("READ?")

    def _scpi_set_trigger_source(self, source: Literal["IMM", "EXT", "BUS", "MAN"] = "IMM"):
        self.write(f"TRIG:SOUR {source}")

    def _scpi_sample_count(self, count: int):
        self.write(f"SAMP:COUN {count}")

    def _scpi_set_voltage_nplc(self, nplc: float):
        self.write(f"SENS:VOLT:DC:NPLC {nplc}")

    def _scpi_set_current_nplc(self, nplc: float):
        self.write(f"SENS:CURR:DC:NPLC {nplc}")

    def _scpi_remove_remote(self):
        self.write("SYST:LOC")

    # -------------------------------------------------
    # CONFIGURATION
    # -------------------------------------------------

    def setup(
        self,
        mode: Literal["V", "A"] = "V",
        range: float = 0,
        speed: Literal["SLOW", "MID", "FAST"] = "FAST",
    ):
        mode = mode.upper()
        speed = speed.upper()

        if speed not in nplc_map:
            raise ValueError(speed)

        if mode == "V":
            if range == 0:
                self.write("CONF:VOLT:DC AUTO")
            else:
                self.write(f"CONF:VOLT:DC {self.get_voltage_range(range)}")
            self._scpi_set_voltage_nplc(nplc_map[speed])
        elif mode == "A":
            if range == 0:
                self.write("CONF:CURR:DC AUTO")
            else:
                self.write(f"CONF:CURR:DC {self.get_current_range(range)}")
            self._scpi_set_current_nplc(nplc_map[speed])
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        self.mode = mode
        self.range = range
        self.speed = speed

    # -------------------------------------------------
    # ACQUISITION
    # -------------------------------------------------

    def fetch_single(self) -> float:

        values = self._parse_values(
            self.query("READ?")
        )

        if not values:
            raise RuntimeError(
                "No measurement received"
            )

        return values[0]

    def fetch_storage(
        self,
        samples: int = 200,
    ) -> list:

        if samples <= 0:
            return []

        values = []

        for _ in range(samples):

            value = self.fetch_single()

            values.append(value)

        return values


    def set_display(self, scenario: Literal["STAT"]) -> None:
        logger.info("set_display() is not implemented for this Hantek driver")

    def save_screenshot(self, filename: str = "TEMP") -> None:
        logger.info(f"save_screenshot({filename}) is not implemented for this Hantek driver")

    # -------------------------------------------------
    # PLOT
    # -------------------------------------------------

    def get_plot(
        self,
        title: str,
        y_label: str,
        filename: str,
        nominal_value: float = 0.0,
        min_limit: float = 0.0,
        max_limit: float = 0.0,
        limit: int = 200,
    ):
        values = self.fetch_storage(samples=limit)

        if not values:
            logger.warning("No measured values available")
            return None

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