import time
from devices.electronic_load.peaktech_2275.peaktech_2275 import PeakTech2275
from devices.electronic_load.easttester_et54.easttester_et54 import EastTesterET54

load = 2
if load == 1:
    load = EastTesterET54.auto_connect()
else:
    load = PeakTech2275.auto_connect()

try:
    
    load.set_mode("CC", channel=1)

    time.sleep(0.5)

    load.set_current(0.5, channel=1)

    time.sleep(0.5)

    load.load_on()

    time.sleep(1)

    measurements = load.fetch(channel=1)
    print(f"Measurements: Voltage={measurements[0]}V, Current={measurements[1]}A")

    time.sleep(10)

    load.load_off()

    time.sleep(1)

finally:
    load.close()
