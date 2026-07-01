import time
import os
import matplotlib.pyplot as plt

from xdm1000 import XDM1000
from loguru import logger


# ============================================
#  DMM MESSUNG (THREAD)
# ============================================

def measure_voltage(duration_s):
    dmm = XDM1000()

    dmm.set_mode("VDC")
    dmm.set_rate("FAST")

    times = []
    voltages = []

    start = time.perf_counter()

    while (time.perf_counter() - start) < duration_s:
        try:
            t = time.perf_counter() - start
            v = dmm.measure()

            times.append(t)
            voltages.append(v)

        except Exception as e:
            logger.debug(f"DMM error: {e}")
            continue

        time.sleep(0.1)

    dmm.close()
    return times, voltages


