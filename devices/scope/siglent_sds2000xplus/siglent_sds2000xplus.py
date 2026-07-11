import pyvisa
import os
import time
from loguru import logger
from typing import Literal

class Siglent_SDS2000:
    def __init__(self, resource):
        """
        resource examples:
        USB: 'USB0::0xF4EC::0xEE38::SDS1XXXX::INSTR'
        LAN: 'TCPIP0::192.168.1.100::INSTR'
        """
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(resource)
        self.inst.timeout = 5000

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
    def _scpi_display_hide_menu(self) -> None:
        """
        Hides menu
        """

        logger.debug(f"Hiding menu")

        self.write(F":DISPlay:HIDemenu")

    def _scpi_display_clear(self) -> None:
        """
        Clears Display
        """

        logger.debug(f"Clearing display")

        self.write(":DISPlay:CLEar")

    def _scpi_display_persistance(self, 
        duration: float
    ) -> None:
        """
        Set the display persistence duration.
        Internal settings which need to be mapped "OFF", "INFinite", "1S", "5S", "10S", "30S" 
        Pay attention to the corret writing of INFinite, otherwise the command

        Args:
            <duration>  Time in Seconds
                        0 is OFF
                        -1 is infinite
        """

        if duration == 0:
            duration = "OFF"
        elif duration == -1:
            duration = "INFinite"
        else:
            allowed = [1, 5, 10, 30]


            nearest = min(allowed, key=lambda x: abs(x - duration))

            if nearest != duration:
                logger.warning(
                    f"Unsupported persistence {duration}s. "
                    f"Using nearest supported value: {nearest}s."
                )

            duration = f"{nearest}S"

        logger.debug(f"Setting display persistence to {duration}")
        
        self.write(f":DISPlay:PERSistence {duration}")

    def _scpi_save_screenshot(self, 
        filename:str, 
        suffix:str
    ) -> None:
        """
        Saves screenshot
        
        """

        logger.debug(f"Saving screenshot from Siglent SDS oscilloscope")
        
        self._scpi_display_hide_menu()
    
        os.makedirs("measurements", exist_ok=True)

        if filename:
            full_name = f"{filename}_SCOPE_{suffix}.bmp"
        else:
            full_name = f"SCOPE_{suffix}.bmp"

        path = os.path.join("measurements", full_name)

        self.inst.chunk_size = 20 * 1024 * 1024

        self.write("PRIN? BMP")

        data = self.inst.read_raw()

        with open(path, "wb") as f:
            f.write(data)

        return path

    def _scpi_identify(self) -> str:
        """
        Identifies the device.

        Returns:
            Result of *IDN?
        """

        logger.debug(f"Querying ID")

        return self.query("*IDN?")

    def _scpi_run(self) -> None:
        """
        Sets the scope into run mode
        """

        logger.debug(f"Starting acquisition")
        
        self.write(":TRIGger:RUN")

    def _scpi_stop(self) -> None:
        """
        Sets the scope into stop mode
        """

        logger.debug(f"Stopping acquisition")
        
        self.write(":TRIGger:STOP")

    def _scpi_set_resolution(
        self, 
        bit: Literal["8Bits", "10Bits"]
    ) -> None:
        """
        Set the acquisition resolution to AUTO or OFF
        For the Siglent it is a native 8 Bit scope, but can scale up to 10
        
        Args:
            <bit>       Desired bitrate
        """

        logger.debug(f"Setting acquisition resolution to {bit}")

        self.write(f":ACQuire:RESolution {bit}")

    def _scpi_set_channel_bwlimit(
        self, 
        channel: Literal[1, 2, 3, 4], 
        bw: Literal["FULL", "20M"]
    ) -> None:
        """
        Set the bandwidth limit for a specific channel.

        Args:
            <channel>   Channel 1 to 4
            <bw>        Bandwith of channel.
        """
        
        logger.debug(f"Setting bandwidth limit for channel {channel} to {bw}")
        
        self.write(f":CHANnel{channel}:BWLimit {bw}")

    def _scpi_set_channel_vertical_scale(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        volts_per_div: float = 10
    ) -> None:
        '''
        Sets the vertical scale for the indicated channel.
        
        Args:
            <channel>   1|2|3|4
            <scale>     1E-3 to 10 V/div
        '''

        logger.debug(f"Setting vertical scale for channel {channel} to {volts_per_div} V/div")

        self.write(f":CHANnel{channel}:SCALe {volts_per_div}")

    def _scpi_set_channel_offset(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        offset: float = 0
    ) -> None:
        """
        Set the vertical offset for a specific channel.
                
        Args:
            <channel>   1 to 4
            <offset>    Actual voltage of the origin of the channel
        """

        logger.debug(f"Setting vertical offset for channel {channel} to {offset} V")

        self.write(f":CHANnel{channel}:OFFset {offset}")

    def _scpi_set_channel_enable(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        state: Literal["ON", "OFF"] = "OFF"
    ) -> None:
        """
        Enables channel

        Args:
            <channel>   1 to 4
            <state>     ON|OFF
        """

        logger.debug(f"Setting channel {channel} enable state to {state}")
        
        self.write(f":CHANnel{channel}:SWITch {state}")

    def _scpi_set_channel_coupling(
        self,
        channel: Literal[1, 2, 3, 4] = 1, 
        coupling: Literal["AC", "DC"] = "DC"
    ) -> None:
        """
        Set the coupling mode for a specific channel.
        
        Args:
            <channel>   1 to 4
            <coupling>  AC|DC
        """
        
        logger.debug(f"Setting coupling mode for channel {channel} to {coupling}")
        
        self.write(f":CHANnel{channel}:COUPling {coupling}")

    def _scpi_set_channel_label_on_off(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        state: Literal["ON", "OFF"] = "OFF"
    ) -> None:
        """
        Enables the label of given channel

        Args:
            <channel>   1 to 4
            <state>     ON|OFF
        """

        logger.debug(f"Setting label visibility for channel {channel} to {state}")

        self.write(f":CHANnel{channel}:LABel {state}")

    def _scpi_set_channel_label_text(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        text = ""
    ) -> None:
        """
        Set the label text for a specific channel.
        
        Args:
            <channel>   1 to 4
            <Text>      Label 
        """

        if len(text) > 20:
            logger.warning(
                f"Label '{text}' exceeds 20 characters. "
                f"Truncating to '{text[:20]}'."
            )
            text = text[:20]

        logger.debug(f"Setting label text for channel {channel} to {text}")
        
        self.write(f':CHANnel{channel}:LABel:TEXT "{text}"')

    def _scpi_set_channel_unit(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        unit: Literal["V", "A"] = "V"):
        """
        Set the unit for a specific channel.
        
        Args:
            <channel>   1 to 4
            <unit>      V|A
        """
        
        logger.debug(f"Setting unit for channel {channel} to {unit}")
        
        self.write(f":CHANnel{channel}:UNIT {unit}")

    def _scpi_set_channel_attenuation(
        self, 
        channel: Literal[1, 2, 3, 4] = 1, 
        attenuation: float = 10
    ) -> None:
        """
        Set the attenuation for a specific channel.
        
        Args:
            <channel>       1 to 4
            <attenuation>   float
        """

        attenuation_nr3 = f"{attenuation:.6E}"

        logger.debug(f"Setting attenuation for channel {channel} to {attenuation}")

        self.write(f":CHANnel{channel}:PROBe VALue,{attenuation_nr3}")

    def _scpi_set_timebase(
        self, 
        sec_per_div: float
    ) -> None:
        """
        Sets the timebase of the scope

        Args:
            <sec_per_div>   Seconds per Devision
        """
        
        logger.debug(f"Setting timebase to {sec_per_div} s/div")
        
        self.write(f":TIMebase:SCALe {sec_per_div}")

    def _scpi_set_trigger_edge(
        self, 
        level: float = 0
    ) -> None:
        """
        Sets the trigger edge level

        Args:
            <level> Level of the trigger
        """

        logger.debug(f"Setting trigger edge level to {level} V")
        
        self.write(f":TRIGger:EDGE:LEVel {level}")

    def _scpi_set_trigger_edge_source(
        self, 
        channel: Literal[1, 2, 3, 4] = 1
    ) -> None:
        """
        Sets the trigger source
        
        Args:
            <channel>   1 to 4
        """
        
        logger.debug(f"Setting trigger edge source to channel {channel}")
        
        self.write(f":TRIGger:EDGE:SOURce C{channel}")

    def _scpi_measure_statistics_on_off(
        self, 
        state: Literal["ON", "OFF"] = "OFF"
    ) -> None:
        """
        Enable or disable measurement statistics on the oscilloscope.
        
        Args:
            <state> ON|OFF
        """

        logger.debug(f"Setting measurement statistics to {state}")

        self.write(f":MEASure:ADVanced:STATistics {state}")

    def _scpi_measure_statistics_reset(self) -> None:
        """
        Resets statistics
        """
        
        logger.debug(f"Resetting measurement statistics on Siglent SDS oscilloscope")
        
        self.write(":MEASure:ADVanced:STATistics:RESet")

    def _scpi_measure_item(self, 
        position: Literal[1, 2, 3, 4, 5] = 1, 
        parameter: Literal["MIN", "MAX", "PKPK", "RMS"] = "RMS"
    ) -> None:
        """
        Measure a specific item on the oscilloscope.

        OFF is not supported with the Siglent, pelase use respective function
        
        Args:
            <position>  Position of the measurment

            <parameter> Type of measurment
                        PKPK|MAX|MIN|AMPL|TOP|BASE|LEVELX|CMEAN|MEAN|S
                        TDEV|VSTD|RMS|CRMS|MEDIAN|CMEDIAN|OVSN|FPRE|O
                        VSP|RPRE|PER|FREQ|TMAX|TMIN|PWID|NWID|DUTY|NDU
                        TY|WID|NBWID|DELAY|TIMEL|RISE|FALL|RISE10T90|FALL9
                        0T10|CCJ|PAREA|NAREA|AREA|ABSAREA|CYCLES|REDGE
                        S|FEDGES|EDGES|PPULSES|NPULSES|PHA|SKEW|FRR|F
                        RF|FFR|FFF|LRR|LRF|LFR|LFF|PACArea|NACArea|ACArea|A
                        BSACArea|PSLOPE|NSLOPE|TSR|TSF|THR|THF
        """

        logger.debug(f"Set measurment position {position} to {parameter}")

        return self.write(f":MEASure:ADVanced:P{position}:TYPE {parameter}")

    def _scpi_measure_source1(
        self, 
        position: Literal[1, 2, 3, 4, 5] = 1, 
        channel: Literal[1, 2, 3, 4] = 1
    ) -> None:
        """
        Set the source for the set position

        Args:
            <position>  1 to 5

            <channel>    1 to 4
        """
        
        logger.debug(f"Measuring source {channel} on channel {position}")
        
        return self.write(f":MEASure:ADVanced:P{position}:SOURce1 C{channel}")

    def _scpi_measure_on_off(
        self, 
        position: Literal[1, 2, 3, 4, 5] = 1, 
        state: Literal["ON", "OFF"] = "OFF"
    ) -> None:
        """
        Enable measurment on position

        Args:
            <position>  1 to 5

            <state>     ON|OFF
        """

        logger.debug(f"Setting measurement {position} to {state}")
        
        self.write(f":MEASure:ADVanced:P{position} {state}")

    # ---------------------------
    # API Functions
    # ---------------------------

    def identify(
        self
    ) -> str:
        
        return(self._scpi_identify())
    
    def set_resolution(
        self,
        bit: Literal[8, 16] = 16
    ) -> None:
        
        if bit == 10: # Mapping    
            bit_scope = "10Bits"
        else:
            bit_scope = "8Bits"
        
        self._scpi_set_resolution(
            bit=bit_scope
        )

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
        position: float = 0
    ) -> None:
        
        self._scpi_set_channel_enable(
            channel=channel,
            state=enable
        )

        if enable == "OFF":
            return
        
        self._scpi_set_channel_attenuation(
            channel=channel,
            attenuation=attenuation
        )

        self._scpi_set_channel_unit(
            channel=channel,
            unit=unit
        )

        if label == "":
            self._scpi_set_channel_label_on_off(
                channel=channel,
                state="OFF"
            )
        else:
            self._scpi_set_channel_label_on_off(
                channel=channel,
                state="ON"
            )

            self._scpi_set_channel_label_text(
                channel=channel,
                text=label
            )

        self._scpi_set_channel_attenuation(
            channel=channel,
            attenuation=attenuation
        )

        self._scpi_set_channel_coupling(
            channel=channel,
            coupling=coupling
        )

        if bandwidth_limit == "20MHz": # Mapping
            bandwidth_limit = "20M"

        self._scpi_set_channel_bwlimit(
            channel=channel,
            bw=bandwidth_limit
        )

        self._scpi_set_channel_vertical_scale(
            channel=channel,
            volts_per_div=volts_per_div
        )

        self._scpi_set_channel_offset(
            channel=channel,
            offset=position
        )
    
    def set_trigger(
        self,
        channel: int,
        mode: str,
        level: float
    ) -> None:
        
        self._scpi_set_trigger_edge_source(
            channel=channel
        )

        self._scpi_set_trigger_edge(
            level=level
        )
    
    def set_timebase(
        self,
        sec_per_div: float
    ) -> None:
        
        self._scpi_set_timebase(
            sec_per_div=sec_per_div
        )

    def set_persistence(
        self,
        duration: float = 0
    ) -> None:
        
        self._scpi_display_persistance(
            duration=duration
        )

    def reset(
        self
    ) -> None:

        for i in range(1, 4+1):
            self._scpi_set_channel_enable(
                channel=i,
                state="OFF"
            )

        self._scpi_measure_statistics_on_off(
            state="OFF"
        )

        for i in range(1, 5+1):

            self._scpi_measure_on_off(
                position=i,
                state="OFF"
            )

        self._scpi_display_persistance(
            duration=0
        )

        time.sleep(2)

    def set_measurement(
        self,
        position: Literal[1, 2, 3, 4, 5, 6] = 1,
        channel: Literal[1, 2, 3, 4] = 1,
        measurement_type: Literal["OFF", "MIN", "MAX", "PKPK", "RMS"] = "OFF"
    ) -> None:
                
        if measurement_type == "OFF":

            self._scpi_measure_on_off(
                position=position,
                channel = "OFF"
            )
            
            self._scpi_measure_statistics_on_off(
                state="OFF"
            )

            return
        else:
            self._scpi_measure_on_off(
                position=position,
                state = "ON"
            )
            
            self._scpi_measure_statistics_on_off(
                state="ON"
            )

            self._scpi_measure_source1(
                position=position,
                channel=channel
            )

            self._scpi_measure_item(
                position=position,
                parameter=measurement_type
            )

    def save_screenshot(
        self,
        filename: str = "TEMP",
    ) -> str:
        """
        Save screenshot and return path.

        Args:
            <filename>  Filename of the screenshot

            <suffix1>   Additional suffix to unify with other screenshots or so

            <suffix2>   Additional suffix to unify with other screenshots or so

        Returns:
            String to saved file
        """
        
        cmd = "PRIN? BMP"
        logger.debug(f"Saving screenshot from Siglent SDS oscilloscope -> {cmd}")
        
        self._scpi_display_hide_menu()
    
        os.makedirs("measurements", exist_ok=True)

        path = os.path.join("measurements", f"{filename}.bmp")

        self.inst.chunk_size = 20 * 1024 * 1024

        self.write(cmd)
        data = self.inst.read_raw()

        with open(path, "wb") as f:
            f.write(data)

        return path

    def run(
        self
    ) -> None:
        
        self._scpi_run()

    def stop(
        self
    ) -> None:
        
        self._scpi_stop()

    def close(
        self
    ) -> None:
        
        self.close

    def get_count(
        self,
        position: Literal[1, 2, 3, 4, 5, 6] = 1
    ) -> int:

        #logger.debug(f"Get count from statistics at position {position}")

        return float(self.query(f":MEASure:ADVanced:P{position}:STATistics? COUNt"))
    
    def persistence_clear(self) -> None:
        
        self._scpi_display_clear()

    def set_label(
        self,
        channel: Literal[1, 2, 3, 4],
        label: str
    ) -> None:
        """
        Sets label for channel
        """

        if label == None or label == "":
            self._scpi_set_channel_label_on_off(
                channel=channel,
                state="OFF"
            )
        else:
            self._scpi_set_channel_label_on_off(
                channel=channel,
                state="ON"
            )

            self._scpi_set_channel_label_text(
                channel=channel,
                text=label
            )
