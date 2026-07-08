import pyvisa
import datetime
import os
import time
from loguru import logger
from utils.utils import plot_data
from typing import Literal

# ---------------------------
# Constants & ENUMS
# ---------------------------

ppm_map = {
    "FAST": 1000e-6,
    "MEDIUM": 100e-6,
    "SLOW": 10e-6
}

# ---------------------------
# Class
# ---------------------------

class RIGOL_DMM800:
    def __init__(self, resource):
        """
        resource examples:
        USB: 'USB0::0xF4EC::0xEE38::SDS1XXXX::INSTR'
        LAN: 'TCPIP0::192.168.1.100::INSTR'
        """
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(resource)
        self.inst.timeout = 5000

        self.mode = "V"
        self.range = 1000
        self.speed = "MEDIUM"

    # ---------------------------
    # Basic Commands
    # ---------------------------

    def write(self, cmd):
        try:
            self.inst.write(cmd)
            logger.info(f"Try command -> {cmd}")
        except:
            logger.warning(f"Failure with command -> {cmd}")

    def query(self, cmd):
        try:
            logger.info(f"Querying -> {cmd}")
            return self.inst.query(cmd).strip()
        except:
            logger.warning(f"Failure with command -> {cmd}")

    def close(self):
        cmd = "CLOSE"
        try:
            self.inst.close()
            logger.info(f"Closing connection -> {cmd}")
        except:
            logger.warning(f"Failure with command -> {cmd}")

    # ---------------------------
    # SCPI Commands
    # ---------------------------

    def _scpi_configure_voltage_dc(
        self, 
        range: Literal["100mV", "1V", "10V", "100V", "1000V", "AUTO"] = "AUTO", 
        lim = "", 
        resolution: Literal[1000, 100, 10] = 1000 
    ) -> None:
        '''
        Presets the multimeter with the specified range and resolution for DC voltage measurement
        This function is mainly used for range and resolution... and lim is not used? 
        
        range         100mV|1V|10V|100V|1000V|AUTO 
        lim           MIN|MAX|DEF
        resolution    1000|100|10 #FAST|MEDIUM|SLOW
        '''

        logger.info(f"Configure device for VDC")

        self.write(f"CONFigure:VOLTage:DC {range},{resolution}")

    def _scpi_initiate(self) -> None:
        '''
        Initiate measurments, need to be done before a fetch
        '''

        logger.info(f"Initialte measurments")

        self.write(f"INITiate[:IMMediate]")

    def _scpi_read(self) -> float:
        '''
        Returns and clears all stored data
        '''

        logger.info(f"Read and Clear buffer")

        return self.query(f"R?")
        
    def _parse_values(
        self, 
        response
    ) -> float:
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

        return [float(v) for v in response.split(",") if v.strip()]

    def _scpi_fetch_single(self) -> float:
        '''
        Compatibility wrapper for the OWON-style single-sample API.
        '''

        try:
            response = self.query("READ?")
            values = self._parse_values(response)
            if values:
                return values[0]
        except Exception as exc:
            logger.warning(f"Failure fetching single value: {exc}")

        response = self.query("FETCh?")
        values = self._parse_values(response)
        if not values:
            raise ValueError("No measurement values received from Rigol DMM")

        return values[-1]

    def _scpi_fetch_storage(
        self, 
        samples: int = 200
    ) -> None:
        '''
        Compatibility wrapper for the OWON-style buffered sampling API.
        
        Args:
            samples     Number of samples that should be fetched
        '''

        try:
            response = self.query(f"R? {samples}")
        except Exception as exc:
            logger.warning(f"Failure fetching buffered values: {exc}")
            response = self.query("FETCh?")

        values = self._parse_values(response)
        if not values:
            raise ValueError("No measurement values received from Rigol DMM")

        if len(values) > samples:
            return values[:samples]

        return values

    def _scpip_data_points(self) -> None:
        '''
        Returns the number of data points currently stored in the measurement buffer.
        DM858 can store up to 500,000 readings while DM858E can store up to 20,000 readings
        '''

        logger.info(f"Querying number of data points in measurement buffer")

        self.query(f"DATA:POINTS?")
        
    def _scpi_data_remove(
        self, 
        points: int = 200
    ) -> None:
        '''
        Removes the specified number of data points from the measurement buffer.

        points      DM858: 1 to 500000
                    DM858E: 1 to 20000
        '''

        logger.info(f"Removing {points} data points from measurement buffer")

        return self.write(f"DATA:REMove? {points}")

    def _scpi_data_threshold(self, 
        threshold: int = 200
    ) -> None:
        '''
        Sets the threshold for data storage in the measurement buffer.
        The total number of readings stored in the memory cannot exceed the threshold
        specified by this command.

        <threshold>    DM858:  1 to 500000
                       DM858E: 1 to 20000
        '''

        logger.info(f"Setting data storage threshold to {threshold}")

        return self.write(f"DATA:POINts:EVENt:THReshold {threshold}")
    
    def _scpi_calculate_average_all(self) -> list[float]:
        """
        Queries the average value, standard deviation, minimum value, and maximum value
        for the Statistics operation:

        Returns:
            [average, std_dev, min, max]
        """

        cmd = "CALCulate:AVERage:ALL?"
        try:
            logger.info("Querying statistics from measurement buffer")

            response = self.query(cmd)  # z.B. "1.23E+00,4.56E-02,..."
            
            values = [float(v) for v in response.split(",")]

            if len(values) != 4:
                raise ValueError(f"Unexpected response format: {response}")

            return {
                "average": values[0],
                "std_dev": values[1],
                "min": values[2],
                "max": values[3]
            }

        except:
            logger.warning(f"Failure with command -> {cmd}")
            return None

    def _scpi_calculate_clear(self) -> None:
        '''
        Clears all limit values, histogram data, statistical information, and measurement results.
        '''

        logger.info(f"Clearing calculation data")

        return self.write(f"CALCulate:CLEar[:IMMediate]")

    def _scpi_calculate_average_count(self) -> int:
        '''
        Returns the number of samples used in the average calculation.
        '''

        logger.info(f"Querying number of samples used in average calculation") 

        return self.query(cmd = f"CALCulate:AVERage:COUNt?")

    def _scpi_calculate_average_state(
        self, 
        state: Literal["ON", "OFF"] = "OFF"
    ) -> None:
        '''
        Enables or disables the average calculation.
        This command won't work in AUTO mode.

        Args:
            state:    ON|OFF
        '''

        logger.info(f"Setting average calculation state to {state}")

        return self.write(f"CALCulate:AVERage:STATe {state}")
    
    def _scpi_hcopy_sdump_data_format(
        self, 
        format: Literal["BMP", "PNG"] = "PNG"
    ) -> None:
        '''
        Sets the format for the hardcopy dump data.

        Args:
            format: BMP|PNG
        '''

        logger.info(f"Setting screenshot data format to {format}")

        return self.write(f"HCOPy:SDUMp:DATA:FORMat {format}")

    def _scpi_hcopy_sdump_data_dump(
        self, 
        filename=None, 
        folder=None, 
        timestamp=None, 
        format="PNG"):
        '''
        Saves a screenshot of the current display to a file.
        '''

        self.hcopy_sdump_data_format(format)

        cmd = f"HCOPy:SDUMp:DATA?"  
        logger.info(f"Saving screenshot from Rigol DM858 -> {cmd}")

        time.sleep(2)

        if folder is None:
            folder = "."

        os.makedirs(folder, exist_ok=True)

        # Use an external timestamp when one is provided.
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        if filename:
            full_name = f"{timestamp}_{filename}_DMM.{format.lower()}"
        else:
            full_name = f"{timestamp}_DMM.{format.lower()}"

        path = os.path.join(folder, full_name)

        self.inst.chunk_size = 20 * 1024 * 1024

        data = self.inst.query_binary_values(
            cmd,
            datatype="B",
            container=bytes
        )

        with open(path, "wb") as f:
            f.write(data)

        logger.debug(f"Screenshot saved to {path}")

        return path

    # ---------------------------
    # Helper Functions
    # ---------------------------

    def get_voltage_range(self, voltage):
        """
        Determines the appropriate measurement range based on the given voltage.

        Returns one of:
        '100mV', '1V', '10V', '100V', '1000V'
        """

        abs_v = abs(voltage)

        if abs_v <= 0.1:
            return "100mV"
        elif abs_v <= 1:
            return "1V"
        elif abs_v <= 10:
            return "10V"
        elif abs_v <= 100:
            return "100V"
        else:
            return "1000V"
        
    # ---------------------------
    # Functions
    # ---------------------------

    def measure_with_statistics_and_screenshot(
    self,
    voltage,
    min_samples,
    mode="MEDIUM",
    folder="measurements",
    filename="DMM"
    ):
        """
        Performs a measurement with statistics enabled until a minimum number of samples is reached,
        then captures a screenshot.

        <voltage>      expected voltage value (used to set range)
        <min_samples>  minimum number of samples before screenshot
        <mode>         FAST | MEDIUM | SLOW
        <folder>       folder to save the screenshot
        <filename>     optional filename prefix for the screenshot
        """

        timeout_sec = 30
        start_time = time.time()

        range_val = self.get_voltage_range(voltage)

        logger.info(f"Auto-selected range: {range_val}")


        numeric_range = {
            "100mV": 0.1,
            "1V": 1,
            "10V": 10,
            "100V": 100,
            "1000V": 1000
        }[range_val]

        if mode.upper() not in ppm_map:
            raise ValueError(
                f"Invalid mode '{mode}'. Use FAST, MEDIUM or SLOW."
            )
        
        resolution = numeric_range * ppm_map[mode.upper()]

        self.configure_voltage_dc(
            range_val,
            "DEF",
            f"{resolution:.6E}"
        )

        self.calculate_clear()

        self.calculate_average_state("ON")

        logger.info(f"Waiting for at least {min_samples} samples...")

        while True:
            try:
                count = int(self.calculate_average_count())
            except:
                count = 0

            logger.info(f"Current sample count: {count}")

            if count >= min_samples:
                break

            if time.time() - start_time > timeout_sec:
                logger.warning("Timeout reached while waiting for samples")
                break

            time.sleep(0.1)

        logger.info("Minimum sample count reached.")

        self.hcopy_sdump_data_dump(
            filename=filename,
            folder=folder,
            format="PNG"
        )

        self.calculate_average_state("OFF")



    def measure_and_plot_voltage(
        self,
        voltage_range,
        voltage_norm,
        voltage_min,
        voltage_max,
        min_samples,
        mode="MEDIUM",
        folder="plots",
        filename="DMM",
        timeout_sec=30
    ):

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        range_val = self.get_voltage_range(voltage_range)

        numeric_range = {
            "100mV": 0.1,
            "1V": 1,
            "10V": 10,
            "100V": 100,
            "1000V": 1000
        }[range_val]

        resolution = numeric_range * ppm_map[mode.upper()]

        logger.info(f"Auto-selected range: {range_val}")

        self.configure_voltage_dc(
            range_val,
            "DEF",
            f"{resolution:.6E}"
        )

        self.calculate_clear()

        try:
            points = int(self.data_points())

            if points > 0:
                logger.info(f"Removing {points} old buffer entries")
                self.data_remove(points)

        except Exception as e:
            logger.warning(f"Failed to clear measurement buffer: {e}")

        self.calculate_average_state("ON")

        logger.info("Starting measurement")
        self.initiate()

        start_time = time.time()

        while True:

            try:
                points = int(self.data_points())
            except Exception:
                points = 0

            logger.info(
                f"Buffer contains {points}/{min_samples} samples"
            )

            if points >= min_samples:
                logger.info("Required sample count reached.")
                break

            if time.time() - start_time > timeout_sec:
                logger.warning(
                    f"Timeout reached ({points}/{min_samples} samples)"
                )
                break

            time.sleep(0.1)

        raw = self.read()

        self.calculate_average_state("OFF")

        if not raw:
            logger.warning("No data received from instrument")
            return None

        if raw.startswith("#"):

            digits = int(raw[1])

            header_len = 2 + digits

            payload_len = int(raw[2:header_len])

            raw = raw[header_len:header_len + payload_len]

        logger.info(f"Received {len(raw)} characters")

        try:
            points = [
                float(v)
                for v in raw.split(",")
                if v.strip()
            ]

        except Exception as e:
            logger.error(f"Failed to parse voltage values: {e}")
            return None

        logger.info(
            f"Parsed {len(points)} voltage samples"
        )

        if not points:
            return None

        samples = list(range(len(points)))

        return plot_data(
            x_data=samples,
            y_data=points,
            title=f"{filename} Voltage Trend",
            y_label="Voltage",
            suffix=timestamp,
            unit="V",
            nominal_value=voltage_norm,
            min_limit=voltage_min,
            max_limit=voltage_max,
        )
    
    def setup(
            self,
            mode: str = "V",
            range: float = 230,
            speed: str = "HIGH",
        ) -> None:
            """
            Configure the Rigol DMM.

            Args:
                mode:   V or A
                range:  Expected maximum measurement value
                speed:  LOW, MID or HIGH
            """

            mode = mode.upper()
            speed = speed.upper()

            speed_map = {
                "LOW": "SLOW",
                "MID": "MEDIUM",
                "HIGH": "FAST",
            }

            if speed not in speed_map:
                raise ValueError(
                    f"Unsupported speed '{speed}'. "
                    "Use LOW, MID or HIGH."
                )

            rigol_speed = speed_map[speed]

            if mode == "V":

                range_val = self.get_voltage_range(range)

                numeric_range = {
                    "100mV": 0.1,
                    "1V": 1,
                    "10V": 10,
                    "100V": 100,
                    "1000V": 1000,
                }[range_val]

                resolution = (
                    numeric_range *
                    ppm_map[rigol_speed]
                )

                self.configure_voltage_dc(
                    range_val,
                    "DEF",
                    f"{resolution:.6E}"
                )

            elif mode == "A":

                logger.warning(
                    "Current mode setup not yet implemented."
                )

            else:
                raise ValueError(
                    f"Unsupported mode '{mode}'. "
                    "Use V or A."
                )

            self.mode = mode
            self.range = range
            self.speed = speed

            logger.info(
                f"DMM configured: "
                f"mode={mode}, "
                f"range={range}, "
                f"speed={speed}"
            )

    def set_display(self) -> None:
        """
        Compatibility wrapper for the OWON display-control API.
        """
        logger.info("Rigol DMM display control is not exposed via this adapter")

    def get_screenshot(
        self,
        folder: str = "measurements",
        prefix: str = "",
        label: str = "",
    ):
        """
        Compatibility wrapper for the OWON screenshot API.
        """
        filename = prefix or label or "DMM"
        return self.hcopy_sdump_data_dump(
            filename=filename,
            folder=folder,
            format="PNG",
        )

    def get_plot(
        self,
        title: str,
        y_label: str,
        suffix: str = "",
        nominal_value: float = 0.0,
        min_limit: float = 0.0,
        max_limit: float = 0.0,
        limit: int = 200,
    ):
        """
        Compatibility wrapper for OWON API.
        """

        timestamp = (
            suffix
            if suffix
            else datetime.datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
        )

        try:
            values = self.fetch_storage(samples=limit)
        except Exception as exc:
            logger.warning(f"Failed to read DMM data buffer: {exc}")
            return None

        logger.info(
            f"Parsed {len(values)} samples"
        )

        if not values:
            return None

        return plot_data(
            x_data=list(range(len(values))),
            y_data=values,
            title=title,
            y_label=y_label,
            suffix=timestamp,
            unit=self.mode,
            nominal_value=nominal_value,
            min_limit=min_limit,
            max_limit=max_limit,
        )