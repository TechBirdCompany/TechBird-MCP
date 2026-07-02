import pyvisa
import datetime
import os
import time
from loguru import logger
from utils.utils import plot_voltage_data

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

class DMM800:
    def __init__(self, resource):
        """
        resource examples:
        USB: 'USB0::0xF4EC::0xEE38::SDS1XXXX::INSTR'
        LAN: 'TCPIP0::192.168.1.100::INSTR'
        """
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(resource)
        self.inst.timeout = 5000

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
    # Configure Commands
    # ---------------------------

    def configure_voltage_dc(self, range, lim, resolution):
        '''
        Presets the multimeter with the specified range and resolution for DC voltage measurement
        This function is mainly used for range and resolution... and lim is not used? 
        
        <range>         100mV|1V|10V|100V|1000V|AUTO 
        <lim>           MIN|MAX|DEF
        <resolution>    1000|100|10 #FAST|MEDIUM|SLOW
        '''

        cmd = f"CONFigure:VOLTage:DC {range},{resolution}"
        try:
            logger.info(f"Configuring DMM for DC voltage measurement")
            return self.write(cmd)
        except:
            logger.warning(f"Failure with command -> {cmd}")

    # ---------------------------
    # Data Commands
    # ---------------------------

    def initiate(self):
        '''
        Initiate measurments, need to be done before a fetch
        '''

        cmd = f"INITiate[:IMMediate]"
        try:
            logger.info(f"Querying number of data points in measurement buffer")
            return self.query(cmd)
        except:
            logger.warning(f"Failure with command -> {cmd}")

    def read(self):
        '''
        Returns and clears all stored data
        '''

        cmd = f"R?"
        try:
            logger.info(f"Querying number of data points in measurement buffer")
            return self.query(cmd)
        except:
            logger.warning(f"Failure with command -> {cmd}")       

    def fetch(self):
        '''
        Fetches all values from the measurement buffer and returns them as a list of floats.
        '''
        
        try:
            logger.info(f"Fetching all values from measurement buffer")
            response = self.query("FETCh?")
        except:
            logger.warning(f"Failure with command -> FETCh?")
            response = "" \
            
        print(response)
            
        for element in response:
            print(element)

        return [
            float(v)
            for v in response.split(",")
            if v.strip()
        ]

    def data_points(self):
        '''
        Returns the number of data points currently stored in the measurement buffer.
        DM858 can store up to 500,000 readings while DM858E can store up to 20,000 readings
        '''

        cmd = f"DATA:POINTS?"
        try:
            logger.info(f"Querying number of data points in measurement buffer")
            return self.query(cmd)
        except:
            logger.warning(f"Failure with command -> {cmd}")

    def data_remove(self, points):
        '''
        Removes the specified number of data points from the measurement buffer.

        <points>    DM858: 1 to 500000
                    DM858E: 1 to 20000
        '''

        cmd = f"DATA:REMove? {points}"
        try:
            logger.info(f"Removing {points} data points from measurement buffer")
            return self.write(cmd)
        except:
            logger.warning(f"Failure with command -> {cmd}")

    def data_threshold(self, threshold):
        '''
        Sets the threshold for data storage in the measurement buffer.
        The total number of readings stored in the memory cannot exceed the threshold
        specified by this command.

        <threshold>    DM858:  1 to 500000
                       DM858E: 1 to 20000
        '''

        cmd = f"DATA:POINts:EVENt:THReshold {threshold}"
        try:
            logger.info(f"Setting data storage threshold to {threshold}")
            return self.write(cmd)
        except:
            logger.warning(f"Failure with command -> {cmd}")

    # ---------------------------
    # Calculate Commands
    # ---------------------------

    def calculate_average_all(self):
        """
        Queries the average value, standard deviation, minimum value, and maximum value
        for the Statistics operation:

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

    def calculate_clear(self):
        '''
        Clears all limit values, histogram data, statistical information, and measurement results.
        '''

        cmd = f"CALCulate:CLEar[:IMMediate]"
        try:
            logger.info(f"Clearing calculation data")
            return self.write(cmd)
        except:
            logger.warning(f"Failure with command -> {cmd}")

    def calculate_average_count(self):
        '''
        Returns the number of samples used in the average calculation.
        '''

        cmd = f"CALCulate:AVERage:COUNt?"
        try:
            logger.info(f"Querying number of samples used in average calculation") 
            return self.query(cmd)
        except:
            logger.warning(f"Failure with command -> {cmd}")

    def calculate_average_state(self, state):
        '''
        Enables or disables the average calculation.
        This command won't work in AUTO mode.

        <state>    ON|OFF
        '''

        cmd = f"CALCulate:AVERage:STATe {state}"
        try:
            logger.info(f"Setting average calculation state to {state}")
            return self.write(cmd)
        except:
            logger.warning(f"Failure with command -> {cmd}")

    # ---------------------------
    # Screenshot Command
    # ---------------------------

    def hcopy_sdump_data_format(self, format):
        '''
        Sets the format for the hardcopy dump data.

        <format>    BMP|PNG
        '''

        cmd = f"HCOPy:SDUMp:DATA:FORMat {format}"
        try:
            logger.info(f"Setting screenshot data format to {format}")
            return self.write(cmd)
        except:
            logger.warning(f"Failure with command -> {cmd}")

    def hcopy_sdump_data_dump(self, filename=None, folder=None, timestamp=None, format="PNG"):
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
    folder="screenshots",
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
        voltage,
        min_samples,
        mode="MEDIUM",
        folder="plots",
        filename="DMM",
        timeout_sec=30
    ):

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        range_val = self.get_voltage_range(voltage)

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
            voltages = [
                float(v)
                for v in raw.split(",")
                if v.strip()
            ]
        except Exception as e:
            logger.error(f"Failed to parse voltage values: {e}")
            return None

        logger.info(
            f"Parsed {len(voltages)} voltage samples"
        )

        if not voltages:
            return None

        samples = list(range(len(voltages)))

        return plot_voltage_data(
            times=samples,
            voltages=voltages,
            title=f"{filename} Voltage Trend",
            timestamp=timestamp,
            folder=folder
        )