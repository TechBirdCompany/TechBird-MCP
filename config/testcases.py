import time
import datetime
import threading
import os

from loguru import logger

from xdm1000 import XDM1000
from devices.scope.siglent_sds2000xplus import SiglentSDS
from devices.electronic_load.easttester_et54.et54 import ET54
from utils.utils import *

# Existing plotting function (plot only)
from devices.dmm.owon_xdm1041.owon_xdm_1041 import plot_voltage_data

def reset_devices(scope, eload):
    '''
    Reset all devices to a usable state
    '''

    # Disable all scope channels
    scope.set_channel_enable(1, False)
    scope.set_channel_enable(2, False)
    scope.set_channel_enable(3, False)
    scope.set_channel_enable(4, False)

    # Remove all measurments on scope
    for i in range(1, 6):
        scope.measure_on_off(i, False)

    # Unlock electronic load and turn channel of off
    eload.unlock()
    eload.off()

def measure_voltage(duration_s):
    '''
    Measure voltage for a given duration
    '''

    # Variables
    times = []
    voltages = []

    # Connect to DMM
    dmm = XDM1000()

    # Set DMM to VDC Mode
    dmm.set_mode("VDC")

    # Enable fast aquesition
    dmm.set_rate("FAST")

    # Starttime
    start = time.perf_counter()

    # Loop
    while (time.perf_counter() - start) < duration_s:
        try:
            t = time.perf_counter() - start
            v = dmm.measure()

            times.append(t)
            voltages.append(v)

        except Exception as e:
            logger.debug(f"DMM error: {e}")
            continue

        # Sleep for 50 ms
        time.sleep(0.05)

    # Close connection
    dmm.close()

    return times, voltages


# ============================================
# MAIN TEST
# ============================================

def load_test(label, voltage, current, timebaseDC, timebaseAC, single=False):

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    logger.info(f"Starting Load Test: {label}")

    scope = SiglentSDS("TCPIP0::10.10.10.90::INSTR")
    eload = ET54.auto_connect()

    currents = [current] if single else [0, current / 2, current]

    reset_devices(scope, eload)

    # Scaling vorbereiten
    C_POS = -3
    c_scale = calc_scale(current)
    logger.info(f"c_scale: {c_scale}")
    c_offset = C_POS * c_scale
    logger.info(f"c_offset: {c_offset}")


    V_POS = -2
    v_scale = calc_scale(voltage)
    logger.info(f"v_scale: {v_scale}")
    v_offset = V_POS * v_scale
    logger.info(f"v_offset: {v_offset}")

    ripple = voltage * 0.07
    r_scale = calc_scale(ripple)

    # Channels
    scope.set_channel_enable(1, True)
    scope.set_channel_enable(3, True)

    scope.set_channel_unit(1, "V")
    scope.set_channel_unit(3, "A")

    scope.set_channel_vertical_scale(3, c_scale)
    scope.set_channel_offset(3, c_offset)

    scope.set_bits("10Bits")
    scope.measure_statistics_on_off(True)

    # Voltage MAX
    scope.measure_on_off(1, True)
    scope.measure_source1(1, "C1")
    scope.measure_item(1, "MAX")

    # Voltage MIN
    scope.measure_on_off(2, True)
    scope.measure_source1(2, "C1")
    scope.measure_item(2, "MIN")

    # Voltage RMS
    scope.measure_on_off(4, True)
    scope.measure_source1(4, "C1")
    scope.measure_item(4, "RMS")

    # Current RMS
    scope.measure_on_off(5, True)
    scope.measure_source1(5, "C3")
    scope.measure_item(5, "RMS")


    for test_current in currents:

        current_label = "IDLE" if test_current == 0 else f"{test_current}A"

        logger.info(f"Running step: {current_label}")

        eload.ch1.CC_mode(test_current)

        scope.set_channel_vertical_scale(1, v_scale)
        scope.set_channel_offset(1, v_offset)       

        scope.set_channel_label_text(1, f"{label} @ {current_label}")
        scope.set_channel_label_text(3, f"{label}")

        scope.set_channel_coupling(1, "DC")
        scope.set_timebase(timebaseDC)

        scope.measure_statistics_reset()

        # ====================================
        # DMM thread (measurement only)
        # ====================================
        dmm_data = {}

        def run_dmm():
            t, v = measure_voltage(10)
            dmm_data["times"] = t
            dmm_data["voltages"] = v

        dmm_thread = threading.Thread(target=run_dmm)
        dmm_thread.start()

        time.sleep(0.1)
        eload.on()

        time.sleep(10)

        # Scope screenshot
        scope.save_screenshot(
            f"{label}_{current_label}",
            folder=get_folder(),
            timestamp=timestamp
        )

        # warten auf DMM
        dmm_thread.join()

        # ====================================
        # Plot (main thread)
        # ====================================
        plot_voltage_data(
            times=dmm_data["times"],
            voltages=dmm_data["voltages"],
            title=f"{label}_{current_label}_DMM",
            timestamp=timestamp,
            folder=get_folder()
        )

        # ====================================
        # RIPPLE
        # ====================================

        scope.set_channel_coupling(1, "AC")
        scope.set_channel_vertical_scale(1, r_scale)
        scope.set_channel_offset(1, 0)

        scope.measure_on_off(4, False)


        scope.set_timebase(timebaseAC)

        scope.display_persistance("INFinite")
        scope.display_clear()

        scope.measure_statistics_reset()

        eload.on()
        time.sleep(10)

        scope.save_screenshot(
            f"{label}_{current_label}_ripple",
            folder=get_folder(),
            timestamp=timestamp
        )

        scope.display_persistance("OFF")

    scope.close()
    eload.close()

    logger.info("Load test completed")