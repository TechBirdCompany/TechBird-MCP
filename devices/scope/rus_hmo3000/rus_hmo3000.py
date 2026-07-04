import pyvisa
import datetime
import os
import time
from loguru import logger

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
        return self.inst.query(cmd).strip()

    def close(self):
        cmd = "CLOSE"
        try:
            self.inst.close()
            logger.info(f"Closing connection to oscilloscope -> {cmd}")
        except:
            logger.warning(f"Failure with command -> {cmd}")


    # ---------------------------
    # Persistence Control
    # ---------------------------
    def display_persistance_state(self, state="OFF"):
        '''
        Defines whether the waveform persists on the screen or whether 
        the screen is refreshed continuously.

        <state> ON|OFF 
        '''

        cmd = f"DISPlay:PERSistence:STATe {state}"
        logger.info(f"Settintg persistence state")
        return self.write(cmd)
    


    def display_persistance_time(self, time):
        '''
        Persistence time if persistence is active (please refer to DISPlay:PERSistence:STATe). 
        Each newdata point in the diagram area remains on the screen for the duration defined here. 
        To set infinitepersistence, use DISPlay:PERSistence:INFinite.

        <time> time in seconds
        '''

        cmd = "DISPlay:PERSistence:TIME {time}"
        logger.info(f"Setting time for persistance mode")
        return self.write(cmd)
    


    def display_persistnace_infinity(self, state="OFF"):
        '''
        Sets the persistence time to infinite if DISPlay:PERSistence:STATe is ON. 
        Each new data point remains on the screen infinitely until this setting is 
        changed or the persistence is cleared.

        <state> ON|OFF 
        '''

        cmd = f"DISPlay:PERSistence:INFinite {state}"
        logger.info(f"Setting persistance mode to infinity")
        return self.write(cmd)
    


    def display_persistance_clear(self):
        '''
        Removes the displayed persistent waveform from the screen.
        '''

        cmd = "DISPlay:PERSistence:CLEar"
        logger.info(f"Clear persistance trace")
        return self.write(cmd)



    # ---------------------------
    # Channel Control
    # ---------------------------

    def channel_state(self, channel, state):
        '''
        Switches the channel signal on or off.
        
        <channel>   1|2|3|4
        <state>     ON|OFF
        '''

        cmd = f"CHANnel{channel}:STATe {state}"
        logger.info(f"Switch {channel} {state}")
        return self.write(cmd)
    


    def channel_coupling(self, channel, coupling):
        '''
        Selects the connection of the indicated channel signal.

        <channel>   1|2|3|4
        <coupling>  DC|DCLimit|AC|ACLimit|GND
        '''

        cmd = f"CHANnel{channel}:COUPling {coupling}"
        logger.info(f"Set channel {channel} to {coupling} coupling")
        return self.write(cmd)
    


    def channel_scale(self, channel, scale):
        '''
        Sets the vertical scale for the indicated channel.
        
        <channel>   1|2|3|4
        <scale>     1E-3 to 10 V/div
        '''

        if 1e-3 < scale > 10:
            logger.warning(f"Scale out of limits")
            return
        else:
            logger.info(f"Set channel {channel} to {scale} V/div")
            cmd = f"CHANnel{channel}:SCALe {scale}"
            return self.write(cmd)



    def channel_position(self, channel, position):
        '''
        Sets the vertical position of the indicated channel and its 
        horizontal axis in the window.

        <channel>   1|2|3|4
        <position>  -5 to 5
        '''

        if -5 < position > 5:
            logger.warning(f"Position out of limits")
            return
        else:
            logger.info(f"Set channel {channel} to position {position} div")
            cmd = f"CHANnel{channel}:POSition {position}"
            return self.write(cmd)



    def channel_bandwidth(self, channel, bandwidth):
        '''
        Selects the bandwidth limit for the indicated channel.
        
        <channel>   1|2|3|4
        <bandwidth>  FULL|B20
        '''

        logger.info(f"Set channel {channel} to bandwidth {bandwidth}")
        cmd = f"CHANnel{channel}:BANDwidth {bandwidth}"
        return self.write(cmd)

    def channel_label(self, channel, label):
        '''
        Set the label for the input channel.

        <channel>   1|2|3|4
        <label>     String value “xxxxxxxx“ with maximum 8 ASCII characters.
        '''

        logger.info(f"Set label of channel {channel} to {label}")
        cmd = f"CHANnel{channel}:LABel {label}"
        return self.write(cmd)
    
    def channel_label_state(self, channel, state):
        '''
        Switches the label of the channel on or off
        <channel>   1|2|3|4
        <state>     ON|OFF
        '''

        logger.info(f"Enable label for channel {channel}")
        cmd = f"CHANnel{channel}:LABel:STATe {state}"
        return self.write(cmd)
    


    # ---------------------------
    # Probe Control
    # ---------------------------

    def probe_unit(self, channel, unit="V"):
        '''
        Selects the unit that the probe can measure.

        <channel>   1|2|3|4
        <unit>      V|A
        '''

        logger.info(f"Set unit of channel {channel} to {unit}")
        cmd = f"PROBe{channel}:SETup:ATTenuation:UNIT {unit}"
        return self.write(cmd)
    


    def probe_attenuation(self, channel, attenuation=10):
        '''
        Sets the attenuation or gain of the probe if the probe was not detected by the instrument.

        <channel>   1|2|3|4
        <unit>      0.001 to 1000
        '''

        if 0.001 <= attenuation <= 1000:
            logger.warning(f"Attenuation out of limits")
            return
        else:
            logger.info(f"Set channel {channel} to attenuation 1:{attenuation}")
            cmd = f"PROBe{channel}:SETup:ATTenuation:MANual {attenuation}"
            return self.write(cmd)

    

    # ---------------------------
    # Trigger Control
    # ---------------------------

    def trigger_mode(self, mode):
        '''
        Sets the trigger mode. The trigger mode determines the behaviour of 
        the instrument if no trigger occurs.

        <mode>  AUTO|NORMal
        '''

        logger.info(f"Set trigger mode to {mode}")
        cmd = f"TRIGger:A:MODE {mode}"
        return self.write(cmd)



    # ---------------------------
    # Device Control
    # ---------------------------
    def get_id(self):
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

    def set_bits(self, bit="8Bits"):
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
        cmd = f":MEASure:ADVanced:P{position}:SOURce1 {source}"
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