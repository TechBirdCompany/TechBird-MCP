import pyvisa
import datetime
import os
import time
from loguru import logger

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

        # SCPI empfohlen: kurze Headers deaktivieren/aktivieren je nach Bedarf
        self.write("CHDR SHORT")

    # ---------------------------
    # BASIC COMMUNICATION
    # ---------------------------
    def write(self, cmd):
        self.inst.write(cmd)

    def query(self, cmd):
        return self.inst.query(cmd).strip()

    def close(self):
        cmd = "CLOSE"
        logger.debug(f"Closing connection to Siglent SDS oscilloscope -> {cmd}")
        self.inst.close()

    # ---------------------------
    # BASIC FUNCTIONS
    # ---------------------------
    def display_hide_menu(self):
        cmd = ":DISPlay:HIDemenu"
        logger.debug(f"Hiding menu on Siglent SDS oscilloscope -> {cmd}")
        self.write(cmd)

    def display_clear(self):
        cmd = ":DISPlay:CLEar"
        logger.debug(f"Clearing display on Siglent SDS oscilloscope -> {cmd}")
        self.write(cmd)

    def display_persistance(self, duration="OFF"):
        """
        Set the display persistence duration.
        duration: "OFF", "INFinite", "1S", "5S", "10S", "30S"
        Pay attention to the corret writing of INFinite, otherwise the command will not be accepted by the device.
        """
        cmd = f":DISPlay:PERSistence {duration}"
        logger.debug(f"Setting display persistence to {duration} -> {cmd}")
        self.write(cmd)


    def save_screenshot(self, filename=None, suffix=None):
        cmd = "PRIN? BMP"
        logger.debug(f"Saving screenshot from Siglent SDS oscilloscope -> {cmd}")
        
        self.display_hide_menu()
    
        os.makedirs("measurements", exist_ok=True)

        if filename:
            full_name = f"{filename}_SCOPE_{suffix}.bmp"
        else:
            full_name = f"SCOPE_{suffix}.bmp"

        path = os.path.join("measurements", full_name)

        self.inst.chunk_size = 20 * 1024 * 1024

        self.write(cmd)
        data = self.inst.read_raw()

        with open(path, "wb") as f:
            f.write(data)

        return path



    # ---------------------------
    # IDENTIFICATION
    # ---------------------------
    def identify(self):
        cmd = "*IDN?"
        logger.debug(f"Querying ID from Siglent SDS oscilloscope -> {cmd}")
        return self.query(cmd)

    # ---------------------------
    # ACQUIRE CONTROL
    # ---------------------------
    def run(self):
        cmd = ":TRIGger:RUN"
        logger.debug(f"Starting acquisition on Siglent SDS oscilloscope -> {cmd}")
        self.write(cmd)

    def stop(self):
        cmd = ":TRIGger:STOP"
        logger.debug(f"Stopping acquisition on Siglent SDS oscilloscope -> {cmd}")
        self.write(cmd)

    def set_resolution(self, bit="8Bits"):
        """
        Set the acquisition resolution to 10-bits or 8-bits.
        bit: "10bits" or "8bits"
        """
        cmd = f":ACQuire:RESolution {bit}"
        logger.debug(f"Setting acquisition resolution to {bit} -> {cmd}")
        self.write(cmd)


    # ---------------------------
    # CHANNEL SETTINGS
    # ---------------------------
    def set_channel_bwlimit(self, channel, bw="FULL"):
        """
        Set the bandwidth limit for a specific channel.
        channel: 1, 2, 3, or 4 
        bw: "FULL" or "20MHz"
        """
        cmd = f":CHANnel{channel}:BWLimit {bw}"
        logger.debug(f"Setting bandwidth limit for channel {channel} to {bw} -> {cmd}")
        self.write(cmd)

    def set_channel_vertical_scale(self, channel, volts_per_div):
        """
        Set the vertical scale (volts per division) for a specific channel.
        channel: 1, 2, 3, or 4
        volts_per_div: float value representing volts per division
        """
        cmd = f":CHANnel{channel}:SCALe {volts_per_div}"
        logger.debug(f"Setting vertical scale for channel {channel} to {volts_per_div} V/div -> {cmd}")
        self.write(cmd)

    def set_channel_offset(self, channel, offset):
        """
        Set the vertical offset for a specific channel.
        channel: 1, 2, 3, or 4
        offset: float value representing the offset
        """
        cmd = f":CHANnel{channel}:OFFset {offset}"
        logger.debug(f"Setting vertical offset for channel {channel} to {offset} V -> {cmd}")
        self.write(cmd)

    def set_channel_enable(self, channel, state=True):
        cmd = f":CHANnel{channel}:SWITch {'ON' if state else 'OFF'}"
        logger.debug(f"Setting channel {channel} enable state to {'ON' if state else 'OFF'} -> {cmd}")
        self.write(cmd)

    def set_channel_coupling(self, channel, coupling="DC"):
        """
        Set the coupling mode for a specific channel.
        channel: 1, 2, 3, or 4
        coupling: "DC" or "AC"
        """
        cmd = f":CHANnel{channel}:COUPling {coupling}"
        logger.debug(f"Setting coupling mode for channel {channel} to {coupling} -> {cmd}")
        self.write(cmd)

    def set_channel_label_on_off(self, channel, state=False):
        cmd = f":CHANnel{channel}:LABel {'ON' if state else 'OFF'}"
        logger.debug(f"Setting label visibility for channel {channel} to {'ON' if state else 'OFF'} -> {cmd}")
        self.write(cmd)

    def set_channel_label_text(self, channel, text):
        """
        Set the label text for a specific channel.
        channel: 1, 2, 3, or 4
        text: string value representing the label text 
        """
        cmd = f':CHANnel{channel}:LABel:TEXT "{text}"'
        logger.debug(f"Setting label text for channel {channel} to '{text}' -> {cmd}")
        self.write(cmd)

    def set_channel_unit(self, channel, unit="V"):
        """
        Set the unit for a specific channel.
        channel: 1, 2, 3, or 4
        unit: "V" or "A"
        """
        cmd = f":CHANnel{channel}:UNIT {unit}"
        logger.debug(f"Setting unit for channel {channel} to {unit} -> {cmd}")
        self.write(cmd)


    def set_channel_attenuation(self, channel, attenuation):
        """
        Set the attenuation for a specific channel.
        channel: 1, 2, 3, or 4
        attenuation: float value representing the attenuation
        """
        attenuation_nr3 = f"{attenuation:.6E}"

        cmd = f":CHANnel{channel}:PROBe VALue,{attenuation_nr3}"
        
        logger.debug(
            f"Setting attenuation for channel {channel} to {attenuation} "
            f"(NR3: {attenuation_nr3}) -> {cmd}"
        )

        self.write(cmd)


    # ---------------------------
    # TIMEBASE
    # ---------------------------
    def set_timebase(self, sec_per_div):
        cmd = f":TIMebase:SCALe {sec_per_div}"
        logger.debug(f"Setting timebase to {sec_per_div} s/div -> {cmd}")
        self.write(cmd)

    # ---------------------------
    # TRIGGER
    # ---------------------------
    def set_trigger_edge(self, level=0.0):
        cmd = f":TRIGger:EDGE:LEVel {level}"
        logger.debug(f"Setting trigger edge level to {level} V -> {cmd}")
        self.write(cmd)

    def set_trigger_edge_source(self, channel):
        """
        Siglent SDS 2000xplus: Needs to activate the desired channel first, otherwise Ext Trigger will be selected
        """
        cmd = f":TRIGger:EDGE:SOURce C{channel}"
        logger.debug(f"Setting trigger edge source to channel {channel} -> {cmd}")
        self.write(cmd)

    # ---------------------------
    # MEASUREMENT  
    # ---------------------------

    def measure_statistics_on_off(self, state=True):
        """
        Enable or disable measurement statistics on the oscilloscope.
        state: True to enable, False to disable
        """
        cmd = f":MEASure:ADVanced:STATistics {'ON' if state else 'OFF'}"
        logger.debug(f"Setting measurement statistics to {'ON' if state else 'OFF'} -> {cmd}")
        self.write(cmd)

    def measure_statistics_reset(self):
        cmd = ":MEASure:ADVanced:STATistics:RESet"
        logger.debug(f"Resetting measurement statistics on Siglent SDS oscilloscope -> {cmd}")
        self.write(cmd)

    def measure_item(self, position, parameter):
        """
        Measure a specific item on the oscilloscope.
        position: 1, 2, 3, 4, or 5 (corresponding to the measurement slots on the oscilloscope)
        parameter:
            {PKPK|MAX|MIN|AMPL|TOP|BASE|LEVELX|CMEAN|MEAN|S
            TDEV|VSTD|RMS|CRMS|MEDIAN|CMEDIAN|OVSN|FPRE|O
            VSP|RPRE|PER|FREQ|TMAX|TMIN|PWID|NWID|DUTY|NDU
            TY|WID|NBWID|DELAY|TIMEL|RISE|FALL|RISE10T90|FALL9
            0T10|CCJ|PAREA|NAREA|AREA|ABSAREA|CYCLES|REDGE
            S|FEDGES|EDGES|PPULSES|NPULSES|PHA|SKEW|FRR|F
            RF|FFR|FFF|LRR|LRF|LFR|LFF|PACArea|NACArea|ACArea|A
            BSACArea|PSLOPE|NSLOPE|TSR|TSF|THR|THF}
        """
        cmd = f":MEASure:ADVanced:P{position}:TYPE {parameter}"
        logger.debug(f"Measuring {parameter} on channel {position} -> {cmd}")
        return self.write(cmd)

    def measure_source1(self, position, source):
        """
        Measure a specific source on the oscilloscope.
        position: 1, 2, 3, 4, or 5 (corresponding to the measurement slots on the oscilloscope)
        source: "C1", "C2", "C3", "C4", "MATH", "REF1", "REF2", "REF3", "REF4"
        """
        cmd = f":MEASure:ADVanced:P{position}:SOURce1 C{source}"
        logger.debug(f"Measuring source {source} on channel {position} -> {cmd}")
        return self.write(cmd)

    def measure_on_off(self, position, state=True):
        """
        Enable or disable a specific measurement on the oscilloscope.
        position: 1, 2, 3, 4, or 5 (corresponding to the measurement slots on the oscilloscope)
        state: True to enable, False to disable
        """
        cmd = f":MEASure:ADVanced:P{position} {'ON' if state else 'OFF'}"
        logger.debug(f"Setting measurement {position} to {'ON' if state else 'OFF'} -> {cmd}")
        self.write(cmd)

    # ---------------------------
    # API Functions
    # ---------------------------

    def set_measurement(
        self,
        position: int,
        channel: int,
        measurement_type: str,
    ):

        """
        Adds a measurement to the screen.

        Args:
            place: Measurement slot.
            channel: Channel number (1, 2, 3, or 4)
            measurement_type:
                OFF
                VMAX
                VMIN
                VPP
                VRMS
                FREQ
                PERIOD
                DUTY
                ...
        """

        if measurement_type == "OFF":
            self.measure_on_off(
                position=position,
                state=False
            )
            
            self.measure_statistics_on_off(
                state=False
            )
            
        else:

            self.measure_on_off(
                position=position,
                state=True
            )
            
            self.measure_statistics_on_off(
                state=True
            )

            self.measure_source1(
                position=position,
                source=channel
            )
            
            self.measure_item(
                position=position,
                parameter=measurement_type
            )
            
    def reset(self):
        """
        Clears persistence,
        statistics and measurements.
        """
        for i in range(1,5):
            self.set_channel_enable(i, False)
        
        for i in range(1,6):
            self.set_measurement(i, 1, "OFF")

        self.measure_statistics_on_off(False)

        self.measure_statistics_reset()
        self.display_clear()

        time.sleep(2)

    def set_persistence(
        self,
        duration: float,
    ):
        """
        Enables display persistence.

        Args:
            time: Persistence duration in seconds.
        """

        if duration == 0:
            self.display_persistance(
                duration="OFF"
            )

        else:
            self.display_persistance(
                duration=duration
            )

    def set_channel(
        self,
        channel: int,
        enable: bool,
        attenuation: float,
        unit: str,
        label: str,
        coupling: str,
        bandwidth_limit: str,
        volts_per_div: float,
        position: float,
    ):
        """
        Configures a channel.

        Args:
            channel: Channel number.
            enable: Show or hide channel.
            attenuation: Probe attenuation (1x, 10x, 100x ...).
            unit: V, A, W, ...
            label: Channel label.
            coupling: DC, AC, GND.
            bandwidth_limit: Enable bandwidth limit.
            scale: Vertical scale per division.
            position: Vertical position.
        """

        if enable is False:
            self.set_channel_enable(
                channel=channel,
                state=False
            )
            return
        else:
            self.set_channel_enable(
                channel=channel,
                state=True
            )
        
        if not label:
            self.set_channel_label_on_off(
                state=False
            )
        
        else:
            self.set_channel_label_on_off(
                channel=channel,
                state=True
            )

            self.set_channel_label_text(
                channel=channel,
                text=label
            )

        self.set_channel_attenuation(
            channel=channel,
            attenuation=attenuation
        )

        self.set_channel_unit(
            channel=channel,
            unit=unit
        )

        self.set_channel_coupling(
            channel=channel,
            coupling=coupling
        )

        self.set_channel_bwlimit(
            channel=channel,
            bw=bandwidth_limit
        )

        self.set_channel_vertical_scale(
            channel=channel,
            volts_per_div=volts_per_div
        )

        self.set_channel_offset(
            channel=channel,
            offset=position
        )

    def set_trigger(
        self,
        channel: int,
        mode: str,
        level: float,
    ):
        """
        Configures edge trigger.

        Args:
            channel: Trigger source.
            mode: Trigger mode.
            level: Trigger level.
        """

        self.set_trigger_edge_source(
            channel=channel
        )

        self.set_trigger_edge(
            level=level
        )


    def get_count(
        self,
        position: int,
    ) -> float:

        cmd = (
            f":MEASure:ADVanced:P{position}:STATistics? COUNt"
        )

        logger.debug(
            f"Get count from statistics "
            f"at position {position} -> {cmd}"
        )

        return float(self.query(cmd))
