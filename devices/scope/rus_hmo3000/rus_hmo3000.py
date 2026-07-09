import pyvisa
import os
import time
from loguru import logger
from typing import Literal

class RUS_HMO3000:
    def __init__(self, resource):
        """
        resource examples:
        USB: 'USB0::0xF4EC::0xEE38::SDS1XXXX::INSTR'
        LAN: 'TCPIP0::192.168.1.100::INSTR'
        """
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(resource)
        self.inst.timeout = 5000

        self._channel_scales = {}

        self.write("CHDR SHORT")

    # ---------------------------
    # BASIC COMMUNICATION
    # ---------------------------
    def write(self, cmd):
        try:
            self.inst.write(cmd)
        except:
            logger.warning(f"Failure with command -> {cmd}")

    def query(self, cmd):
        try:
            return self.inst.query(cmd).strip()
        except:
            logger.warning(f"Failure with command -> {cmd}")

    def close(self):
        cmd = "CLOSE"
        try:
            self.inst.close()
        except:
            logger.warning(f"Could not close connection")

    # ---------------------------
    # SCPI Commands
    # ---------------------------

    def _scpi_display_persistance_state(
        self, 
        state: Literal["ON", "OFF"] = "OFF"
    ) -> None:
        '''
        Defines whether the waveform persists on the screen or whether 
        the screen is refreshed continuously.
        
        Args:
            <state> ON|OFF 
        '''

        logger.info(f"Settintg persistence state")

        return self.write(f"DISPlay:PERSistence:STATe {state}")

    def _scpi_display_persistance_time(
        self, 
        time: float
    ) -> None:
        '''
        Persistence time if persistence is active (please refer to DISPlay:PERSistence:STATe). 
        Each newdata point in the diagram area remains on the screen for the duration defined here. 
        To set infinitepersistence, use DISPlay:PERSistence:INFinite.

        Args:
            <time> time in seconds
        '''

        logger.info(f"Setting time for persistance mode")

        return self.write(f"DISPlay:PERSistence:TIME {time}")
    
    def _scpi_display_persistance_infinity(
        self,
        state: Literal["ON", "OFF"] = "OFF"
    ) -> None:
        '''
        Sets the persistence time to infinite if DISPlay:PERSistence:STATe is ON. 
        Each new data point remains on the screen infinitely until this setting is 
        changed or the persistence is cleared.

        Args:
            <state> ON|OFF 
        '''
        logger.info(f"Setting persistance to infinity mode")

        return self.write(f"DISPlay:PERSistence:INFinite {state}")
  
    def _scpi_display_persistance_clear(self) -> None:
        '''
        Removes the displayed persistent waveform from the screen.
        '''

        logger.info(f"Clear persistance trace")

        return self.write(f"DISPlay:PERSistence:CLEar")

    def _scpi_channel_state(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        state: Literal["ON", "OFF"] = "ON"
    ) -> None:
        '''
        Switches the channel signal on or off.
        
        Args:
            <channel>   1|2|3|4
            <state>     ON|OFF
        '''

        logger.info(f"Switch {channel} {state}")

        return self.write(f"CHANnel{channel}:STATe {state}")

    def _scpi_channel_coupling(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        coupling: Literal["AC", "DC"] = "DC"
    ) -> None:
        '''
        Selects the connection of the indicated channel signal.

        Args:
            <channel>   1|2|3|4
            <coupling>  AC|DC
        '''

        logger.info(f"Set channel {channel} to {coupling} coupling")

        return self.write(f"CHANnel{channel}:COUPling {coupling}")
    
    def _scpi_channel_scale(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        scale: float = 10
    ) -> None:
        '''
        Sets the vertical scale for the indicated channel.
        
        Args:
            <channel>   1|2|3|4
            <scale>     1E-3 to 10 V/div
        '''

        if not (1e-3 <= scale <= 10):
            logger.warning(f"Scale out of limits")
            return

        logger.info(f"Set channel {channel} to {scale} V/div")

        self._channel_scales[channel] = scale

        return self.write(f"CHANnel{channel}:SCALe {scale}")

    def _scpi_channel_position(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        position: float = 0
    ) -> None:
        '''
        Sets the position of the channel trace

        Args:
            <channel>   1|2|3|4
            <position>  -5 to 5
        '''

        if not (-5 <= position <= 5):
            logger.warning(f"Scale out of limits")
            return

        divisions = position/self._channel_scales.get(channel)

        logger.info(f"CH{channel}: Requesting position={position}V -> {divisions}div")

        self.write(f"CHANnel{channel}:POSition {divisions}")

    def _scpi_channel_bandwidth(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        bandwidth: Literal["FULL", "B20"] = "FULL"
    ) -> None:
        '''
        Selects the bandwidth limit for the indicated channel.
        
        Args:
            <channel>   1|2|3|4
            <bandwidth>  FULL|B20
        '''

        logger.info(f"Set channel {channel} to bandwidth {bandwidth}")

        return self.write(f"CHANnel{channel}:BANDwidth {bandwidth}")

    def _scpi_channel_label(
        self,
        channel: Literal[1, 2, 3, 4] = 1,
        label: str = ""
    ) -> None:
        """
        Set the label for the input channel.

        Args:
            <channel>   1|2|3|4
            <label>     String value with maximum 8 ASCII characters.
        """

        if len(label) > 8:
            logger.warning(
                f"Label '{label}' exceeds 8 characters. "
                f"Truncating to '{label[:8]}'."
            )
            label = label[:8]

        logger.info(f"Set label of channel {channel} to '{label}'")

        return self.write(f'CHANnel{channel}:LABel "{label}"')

    def _scpi_channel_label_state(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        state: Literal["ON", "OFF"] = "OFF"
    ) -> None:
        '''
        Switches the label of the channel on or off
        
        Args:
            <channel>   1|2|3|4
            <state>     ON|OFF
        '''

        logger.info(f"Enable label for channel {channel}")

        return self.write(f"CHANnel{channel}:LABel:STATe {state}")

    def _scpi_probe_unit(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        unit: Literal["V", "A"] = "V"
    ) -> None:
        '''
        Selects the unit that the probe can measure.

        Args:
            <channel>   1|2|3|4
            <unit>      V|A
        '''

        logger.info(f"Set unit of channel {channel} to {unit}")

        return self.write(f"PROBe{channel}:SETup:ATTenuation:UNIT {unit}")
    
    def _scpi_probe_attenuation(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        attenuation: float = 10
    ) -> None:
        '''
        Sets the attenuation or gain of the probe if the probe was not detected by the instrument.

        Args:
            <channel>   1|2|3|4
            <unit>      0.001 to 1000
        '''

        if not (0.001 <= attenuation <= 1000):
            logger.warning("Attenuation out of limits")
            return

        logger.info(f"Set channel {channel} to attenuation 1:{attenuation}")

        return self.write(f"PROBe{channel}:SETup:ATTenuation:MANual {attenuation}")

    def _scpi_trigger_mode(
        self, 
        mode: Literal["AUTO"] = "AUTO"
    ) -> None:
        '''
        Sets the trigger mode. The trigger mode determines the behaviour of 
        the instrument if no trigger occurs.

        Args:
            <mode>  AUTO|NORMal
        '''

        logger.info(f"Set trigger mode to {mode}")

        return self.write(f"TRIGger:A:MODE {mode}")

    def _scpi_identify(self) -> str:
        '''
        Returns the IDN of the device

        Returns:
            IDN String
        '''

        logger.debug(f"Querying ID")
    
        return self.query("*IDN?")
    
    def _scpi_run(self) -> None:
        '''
        Sets the scope in run mode
        '''

        logger.debug(f"Starting acquisition")
        
        self.write(":RUN")

    def _scpi_stop(self) -> None:
        '''
        Sets the scope to stop mode
        '''

        logger.debug(f"Stopping acquisition")

        self.write("STOP")

    def _scpi_set_resolution(
        self, 
        bit: Literal["AUTO", "OFF"] = "AUTO"
    ) -> None:
        """
        Set the acquisition resolution to AUTO or OFF
        For the HMO it is a native 8 Bit scope, but can scale up to 16
        
        Args:
            <bit>       Desired bitrate
        """
        
        logger.debug(f"Setting acquisition resolution to {bit}")

        self.write(cmd = f"ACQuire:HRESolution {bit}")

    def _scpi_set_timebase(
        self, 
        sec_per_div: float
    ) -> None:
        """
        Set the timebase to the desired setting
        
        Args:
            <sec_per_div>        1E-9 to 50
        """

        if not (1E-9 <= sec_per_div <= 50):
            logger.warning("Timebase out of limits")
            return

        logger.debug(f"Setting timebase to {sec_per_div} s/div")

        self.write(f"TIMebase:SCALe {sec_per_div}")

    def _scpi_set_trigger_edge(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        level: float=0.0
    ) -> None:
        """
        Sets trigger level. Level depends on the scale.
        So take care of the corret level

        Args:
            <channel>   1|2|3|4
            <level>     float
        """

        logger.debug(f"Setting trigger edge level to {level} V")

        self.write(f"TRIGger:A:LEVel{channel} {level}")

    def _scpi_measure_statistics_on_off(
        self, 
        position: Literal[1, 2, 3, 4, 5, 6] = 1, 
        state: Literal["ON", "OFF"] = "OFF"
    ) -> None:
        """
        Enable or disable measurement statistics on the oscilloscope.

        Args:
            <position>  1 to 6
            <state>     ON|OFF
        """

        logger.debug(f"Setting measurement position {position} statistics to {state}")

        self.write(f"MEASurement{position}:STATistics:ENABle {state}")

    def _scpi_measure_statistics_reset(
        self, 
        position: Literal[1, 2, 3, 4, 5, 6] = 1
    ) -> None:
        """
        Resets the statistic of given slot

        Args:
            <position>  1 to 6
        """

        logger.debug(f"Resetting measurement statistics on Position {position}")

        self.write(f"MEASurement{position}:STATistics:RESet")

    def _scpi_get_count(
        self, 
        position: Literal[1, 2, 3, 4, 5, 6] = 1
    ) -> int:
        """
        Get count of measurment at given position
        
        Args:
            <position>  1 to 6
        
        Returns:
            Counter of position 
        """

        logger.debug(f"Getting count of position {position}")

        return int(self.query(f"MEASurement{position}:RESult:WFMCount?"))       
        
    def _scpi_measure_enable(
        self, 
        position: Literal[1, 2, 3, 4, 5, 6] = 1, 
        state: Literal["ON", "OFF"] = "OFF"
    ) -> None:
        """
        Enable measurment on given position
        
        Args:
            <position>  1 to 6
            <state>     ON|OFF
        """

        logger.debug(f"Activating measurement at position {position}")

        self.write(f"MEASurement{position}:ENABle {state}")

    def _scpi_measurment_source(
        self, 
        position: Literal[1, 2, 3, 4, 5, 6] = 1, 
        source: Literal[1, 2, 3, 4] = 1
    ) -> None:
        """
        Changes the source of the measurment at the given position

        Args:
            <position>  Position of the measurment
            <source>    Channel for the measurment
        """
        
        logger.debug(f"Setting position {position} to channel {source}")

        self.write(f"MEASurement{position}:SOURce CH{source}")

    def _scpi_measure_item(
        self, 
        position: Literal[1, 2, 3, 4, 5, 6] = 1, 
        parameter: Literal["LPEakvalue", "UPEakvalue", "PEAK", "RMS"] = "RMS"
    ) -> None:
        """
        Measure a specific item on the oscilloscope.

        Internal measurment types (need to be maped)
            FREQuency | PERiod | PEAK | UPEakvalue | LPEakvalue | PPCount |
            NPCount | RECount | FECount | HIGH | LOW | AMPLitude | CRESt |
            MEAN | RMS | RTIMe | FTIMe | PDCYcle | NDCYcle | PPWidth |
            NPWidth | CYCMean | CYCRms | STDDev | TFRequency | TPERiode |
            POVershoot | NOVershoot | DELay | PHASe
        
        Args:
            <position>     1 to 6 (corresponding to the measurement slots on the oscilloscope)
            <parameter>     MIN|MAX|PKPK|RMS
        """

        logger.debug(f"Measuring {parameter} on channel {position}")

        return self.write(f":MEASurement{position}:MAIN {parameter}")
    
    # ---------------------------
    # API Commands
    # ---------------------------
    # Description is in the scope_protocol... not typing it again

    def identify(self) -> str:
        return(self._scpi_identify)
    
    def set_resolution(
        self,
        bit: Literal[8, 16] = 16
    ) -> None:
        
        if bit == 8: # Mapping    
            bit_scope = "OFF"
        else:
            bit_scope = "AUTO"

        self._scpi_set_resolution(bit)
        
    def set_channel(
        self,
        channel: Literal[1, 2, 3, 4] = 1,
        enable: Literal["ON", "OFF"] = "ON",
        attenuation: float = 10,
        unit: Literal["V", "A"] = "V",
        label: str = "",
        coupling: Literal["AC", "DC"] = "DC",
        bandwidth_limit: Literal["FULL", "20MHz"] = "FULL",
        volts_per_div: float = 5,
        position: float = 0,
        ) -> None:
        
        self._scpi_channel_state(
            channel=channel,
            state=enable
        )
        
        if enable == "OFF":
            return
        
        self._scpi_probe_attenuation(
            channel=channel,
            attenuation=attenuation
        )
        
        self._scpi_probe_unit(
            channel=channel,
            unit=unit
        )

        if label == "":
            self._scpi_channel_label_state(
                channel=channel,
                state=False
            )
        else:
            self._scpi_channel_label_state(
                channel=channel,
                state=True
            )

            self._scpi_channel_label(
                channel=channel,
                text=label
            )

        self._scpi_channel_coupling(
            channel=channel,
            coupling=coupling
        )

        if bandwidth_limit == "20MHz": # Mapping
            bandwidth_limit = "B20"

        self._scpi_channel_bandwidth(
            channel=channel,
            bandwidth=bandwidth_limit
        )

        self._scpi_channel_scale(
            channel=channel,
            scale=volts_per_div
        )

        self._scpi_channel_position(
            channel=channel,
            position=position
        )

    def set_trigger(
            self,
            channel:int,
            mode:str,
            level:float,
    ):
        if mode:
            self.trigger_mode(
                mode=mode
            )

        self.set_trigger_edge(
            channel=channel,
            level=level
        )

    def reset(self):

        for i in range(1, 5):
            self._scpi_channel_state(
                channel=i,
                state="OFF"
            )

        for i in range(1, 6):

            self._scpi_measure_enable(
                position=i,
                state="OFF"
            )

            self._scpi_measure_statistics_on_off(
                position=i,
                state="OFF"
            )
            
            self._scpi_measure_statistics_reset(
                position=i
            )

        self._scpi_display_persistance_clear()
        self._scpi_display_persistance_state("OFF")

        time.sleep(2)

    def set_persistence(
        self,
        duration: float = 0,
    ) -> None:

        if duration == 0:

            self._scpi_display_persistance_state(
                state="OFF"
            )

        else:

            self._scpi_display_persistance_state(
                state="ON"
            )

            if duration < 0:

                self._scpi_display_persistance_infinity(
                    state="ON"
                )

            else:

                self._scpi_display_persistance_infinity(
                    state="OFF"
                )

                self._scpi_display_persistance_time(
                    time=duration
                )

    def set_measurement(
        self,
        position: Literal[1, 2, 3, 4, 5, 6] = 1,
        channel: Literal[1, 2, 3, 4] = 1,
        measurement_type: Literal["OFF", "MIN", "MAX", "PKPK", "RMS"] = "OFF",
    ):

        if measurement_type == "OFF":
            enable = measurement_type
        else:
            enable = "ON"

        self._scpi_measure_enable(
            position=position,
            state=enable
        )

        self._scpi_measure_statistics_on_off(
            position=position,
            state=enable
        )

        if measurement_type == "OFF":
            return

        self._scpi_measurment_source(
            position=position,
            source=channel
        )

        if measurement_type == "MIN":  # Mapping
            parameter = "LPEakvalue"
        if measurement_type == "MAX":
            parameter = "UPEakvalue"
        if measurement_type == "PKPK":
            parameter = "PEAK"

        self._scpi_measure_item(
            position=position,
            parameter=measurement_type
        )

    def save_screenshot(
        self, 
        filename: str = "TEMP", 
        suffix: str = ""
    ) -> None:

        logger.debug(
            "Saving screenshot"
        )

        try:
            self._scpi_stop()
            time.sleep(0.5)

            result = self.inst.query_binary_values(
                "HCOPy:DATA?",
                datatype="B",
                container=bytearray
            )

            logger.debug(
                f"Received {len(result)} bytes from oscilloscope"
            )

            file_path = os.path.join(
                "measurements",
                f"{filename}_SCOPE_{suffix}.bmp"
            )

            with open(file_path, "wb") as fp:
                fp.write(result)

            logger.debug(
                f"Screenshot saved to {file_path}"
            )

        except Exception as ex:
            logger.exception(
                f"Failed to save screenshot: {ex}"
            )

    def persistence_clear(self) -> None:
        self.persistence_clear()

    def get_count(
        self,
        position: Literal[1, 2, 3, 4, 5, 6] = 1
    ) -> int:
        self._scpi_get_count(
            position=position
        )

    def run(self) -> None:
        self._scpi_run()

    def stop(self) -> None:
        self._scpi_stop()

    def set_timebase(self,
        sec_per_div: float,
    ) -> None:
        self._scpi_set_timebase(
            sec_per_div=sec_per_div
        )