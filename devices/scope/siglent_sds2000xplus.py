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

    def set_10bit_mode(self, state=False):
        self.write(f":ACQuire:RESolution {'10Bits' if state else '8Bits'}")


    # ---------------------------
    # CHANNEL SETTINGS
    # ---------------------------
    def set_channel_20MHzbwlimit(self, channel, state=True):
        self.write(f":CHANnel{channel}:BWLimit {'20M' if state else 'FULL'}")

    def set_channel_vertical_scale(self, channel, volts_per_div):
        self.write(f":CHANnel{channel}:SCALe {volts_per_div}")

    def set_channel_offset(self, channel, offset):
        self.write(f":CHANnel{channel}:OFFset {offset}")

    def set_channel_enable(self, channel, state=True):
        self.write(f":CHANnel{channel}:SWITch {'ON' if state else 'OFF'}")

    def set_channel_dc_coupling(self, channel, DC=True):
        self.write(f":CHANnel{channel}:COUPling {'DC' if DC else 'AC'}")

    def set_channel_label_on_off(self, channel, state=False):
        self.write(f":CHANnel{channel}:LABel {'ON' if state else 'OFF'}")

    def set_channel_label_text(self, channel, text):
        self.write(f':CHANnel{channel}:LABel:TEXT "{text}"')

    def set_channel_unit_volt(self, channel, volt=True):
        self.write(f"CHANnel{channel}:UNIT {'V' if volt else 'A'}")

    def set_channel_attenuation(self, channel, attenuation):
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
