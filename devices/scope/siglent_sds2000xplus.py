import pyvisa
import time

class SiglentSDS:
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
        self.inst.close()

    # ---------------------------
    # BASIC FUNCTIONS
    # ---------------------------
    def display_hide_menu(self):
        self.write(f":DISPlay:HIDemenu")

    # ---------------------------
    # IDENTIFICATION
    # ---------------------------
    def get_id(self):
        return self.query("*IDN?")

    # ---------------------------
    # ACQUIRE CONTROL
    # ---------------------------
    def run(self):
        self.write(":TRIGger:RUN")

    def stop(self):
        self.write(":TRIGger:STOP")

    def set_bits(self, bit="8Bits"):
        """
        Set the acquisition resolution to 10-bit or 8-bit.
        bit: "10bits" or "8bits"
        """
        self.write(f":ACQuire:RESolution {bit}")


    # ---------------------------
    # CHANNEL SETTINGS
    # ---------------------------
    def set_channel_bwlimit(self, channel, bw="FULL"):
        """
        Set the bandwidth limit for a specific channel.
        channel: 1, 2, 3, or 4 
        bw: "FULL" or "20MHz"
        """
        self.write(f":CHANnel{channel}:BWLimit {bw}")

    def set_channel_vertical_scale(self, channel, volts_per_div):
        """
        Set the vertical scale (volts per division) for a specific channel.
        channel: 1, 2, 3, or 4
        volts_per_div: float value representing volts per division
        """
        self.write(f":CHANnel{channel}:SCALe {volts_per_div}")

    def set_channel_offset(self, channel, offset):
        """
        Set the vertical offset for a specific channel.
        channel: 1, 2, 3, or 4
        offset: float value representing the offset
        """
        self.write(f":CHANnel{channel}:OFFset {offset}")

    def set_channel_enable(self, channel, state=True):
        self.write(f":CHANnel{channel}:SWITch {'ON' if state else 'OFF'}")

    def set_channel_coupling(self, channel, coupling="DC"):
        """
        Set the coupling mode for a specific channel.
        channel: 1, 2, 3, or 4
        coupling: "DC" or "AC"
        """
        self.write(f":CHANnel{channel}:COUPling {coupling}")

    def set_channel_label_on_off(self, channel, state=False):
        self.write(f":CHANnel{channel}:LABel {'ON' if state else 'OFF'}")

    def set_channel_label_text(self, channel, text):
        """
        Set the label text for a specific channel.
        channel: 1, 2, 3, or 4
        text: string value representing the label text 
        """
        self.write(f':CHANnel{channel}:LABel:TEXT "{text}"')

    def set_channel_unit_volt(self, channel, unit="V"):
        """
        Set the unit for a specific channel.
        channel: 1, 2, 3, or 4
        unit: "V" or "A"
        """
        self.write(f"CHANnel{channel}:UNIT {unit}")

    def set_channel_attenuation(self, channel, attenuation):
        """
        Set the attenuation for a specific channel.
        channel: 1, 2, 3, or 4
        attenuation: float value representing the attenuation
        """
        self.write(f":CHANnel{channel}:PROBe {attenuation}")


    # ---------------------------
    # TIMEBASE
    # ---------------------------
    def set_timebase(self, sec_per_div):
        self.write(f":TIMebase:SCALe {sec_per_div}")

    # ---------------------------
    # TRIGGER
    # ---------------------------
    def set_trigger_edge(self, level=0.0):
        self.write(f":TRIGger:EDGE:LEVel {level}")

    def set_trigger_edge_source(self, channel):
        """
        Siglent SDS 2000xplus: Needs to activate the desired channel first, otherwise Ext Trigger will be selected
        """
        self.write(f":TRIGger:EDGE:SOURce C{channel}")
