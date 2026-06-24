import time
import datetime

from devices.scope.siglent_sds2000xplus import *
from devices.electronic_load.easttester_et54 import ET54


# connect to the load
el = ET54("ASRL4::INSTR")

# set ranges
el.ch1.Vrange = "high"
el.ch1.Crange = "high"

# set protections
el.ch1.OVP = 24.5
el.ch1.OCP = 4
el.ch1.OPP = 85

# start in constant current mode (3.1A)
el.ch1.CC_mode(0.5)
el.ch1.on()

# switch to CCCV mode
el.ch1.CCCV_mode(2.5, 13.5)
# and change the current on the way
el.ch1.CCCV_current = 1

# monitor voltage, current, power and resistance for a minute
print("timestamp, V, I, P, R")
for i in range(60):
    print(", ".join([str(x) for x in [
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        el.ch1.read_voltage(),
        el.ch1.read_current(),
        el.ch1.read_power(),
        el.ch1.read_resistance(),
    ]]))
    time.sleep(1)

# turn off the load channel
el.ch1.off()




scope = SiglentSDS("TCPIP0::10.10.10.90::INSTR")

scope.set

'''
print(scope.get_id())

scope.set_channel_enable(1, True)
scope.set_channel_enable(2, True)
scope.set_channel_enable(3, False)
scope.set_channel_enable(4, False)
scope.display_hide_menu()
scope.set_10bit_mode(True)

scope.set_channel_dc_coupling(1, False)
scope.set_channel_dc_coupling(2, False)

scope.set_channel_attenuation(1, 10)
scope.set_channel_attenuation(2, 1)

scope.set_channel_label_on_off(1, True)
scope.set_channel_label_on_off(2, True)

scope.set_channel_label_text(1, "VCC_1V0 Voltage")
scope.set_channel_label_text(2, "VCC_1V0 Current")

scope.set_channel_20MHzbwlimit(1, True)
scope.set_channel_20MHzbwlimit(2, True)

scope.set_channel_unit_volt(1, True)
scope.set_channel_unit_volt(2, False)

scope.set_channel_vertical_scale(1, 0.2)
scope.set_channel_vertical_scale(2, 0.1)

scope.set_channel_offset(1, 0.2*2*-1)
scope.set_channel_offset(2, 0.1*3*-1)

scope.set_timebase(1/1000)

scope.set_trigger_edge_source(1)
scope.set_trigger_edge(0)



scope.set_channel_dc_coupling(1, False)
scope.set_channel_offset(1, 0)
scope.set_channel_vertical_scale(1, 0.05)
'''
