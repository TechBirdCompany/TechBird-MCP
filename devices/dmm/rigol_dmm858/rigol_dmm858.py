import pyvisa
import datetime
import os
import time
from loguru import logger

class DMM858:
    def __init__(self, resource):
        """
        resource examples:
        USB: 'USB0::0xF4EC::0xEE38::SDS1XXXX::INSTR'
        LAN: 'TCPIP0::192.168.1.100::INSTR'
        """
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(resource)
        self.inst.timeout = 5000

        # SCPI empfohlen: kurze Headers deaktivieren/aktivieren je nach Bedarf
        self.write("CHDR SHORT")

    # ---------------------------
    # BASIC COMMUNICATION
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



    def calculate_average_cout(self):
        '''
        Returns the number of samples used in the average calculation.
        '''

        cmd = f"CALCulate:AVERage:COUNt?"
        try:
            logger.info(f"Querying number of samples used in average calculation") 
            return self.query(cmd)
        except:
            logger.warning(f"Failure with command -> {cmd}")

