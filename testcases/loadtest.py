import time
from loguru import logger
from utils.utils import *

from devices.dmm.dmm_protocol import dmm
from devices.scope.scope_protocol import scope
from devices.electronic_load.eload_protocol import eload

def load_test(
    scope: scope,
    dmm: dmm,
    eload: eload,
    voltage: float,
    max_voltage: float,
    min_voltage: float,
    domain: str,
    current: float,
    single: bool = False
):
    """
    Measures the domain in idle and with mid and high load
    """

    logger.info(
        f"Starting load test: "
        f"{voltage}V @ {current}A"
    )

    if single:
        test_points = [
            ("FULL", current),
        ]
    else:
        test_points = [
            ("IDLE", 0),
            ("HALF", current / 2),
            ("FULL", current),
        ]

    for test_current_label, test_current in test_points:


        current_label = f"{test_current:.2f}A"

        logger.info(
            f"Starting test point "
            f"{test_current_label} "
            f"({current_label})"
        )

        # ---------------------------
        # DC Measurment
        # ---------------------------
        
        eload.load_off()    # Disable eload

        eload.set_mode("CC")    # Set eload to CC

        dmm.setup(  # Setup DMM
            mode="V",
            range=max_voltage,
            speed="HIGH",
        )

        scope.stop()    # Stop scope

        scope.reset()   # Reset measurments and display of scope    

        scope.set_persistence(0) # Remove persistance mode

        scope.set_resolution(   # Set resolution to 10 Bit for 20 MHz
            bit="10Bits"
        )

        scope.set_channel(  # Set channel 1 of scope
            channel=1,
            enable=True,
            attenuation=10,
            unit="V",
            label=f"{domain} @ {test_current}A",
            coupling="DC",
            bandwidth_limit="20MHz",
            volts_per_div=calc_scale(voltage),
            position=calc_scale(voltage)*-2,
        )

        scope.set_channel(  # Set channel 2 of scope
            channel=2,
            enable=True,
            attenuation=10,
            unit="A",
            label=f"{domain} @ {test_current}A",
            coupling="DC",
            bandwidth_limit="20MHz",
            volts_per_div=calc_scale(current),
            position=calc_scale(current)*-3,
        )

        scope.set_trigger(  # Set trigger mode
            channel=1,
            mode="",
            level=voltage / 2,
        )

        scope.set_timebase( # Set Timebase
            sec_per_div=1e-3,
        )

        scope.set_measurement(  # Set measurment 1 for channel 1 to max
            position=1,
            channel=1,
            measurement_type="MAX",
        )

        scope.set_measurement(  # Set measurment 2 for channel 1 to min
            position=2,
            channel=1,
            measurement_type="MIN",
        )

        scope.set_measurement(  # Set measurment 3 for channel 1 to RMS
            position=3,
            channel=1,
            measurement_type="RMS",
        )

        scope.set_measurement(  # Set measurment 4 for channel 2 to RMS
            position=4,
            channel=2,
            measurement_type="RMS",
        )

        eload.set_current(test_current)  # Set eload to current

        eload.load_on() # Enable eload

        scope.run() # Set scope in run mode

        while True:
            count = scope.get_count(
                position=1
            )

            logger.info(f"Scope Counter at: {count}")

            if count >= 250:
                break

        scope.stop() # Set scope in stop mode

        scope.save_screenshot(  # Get screenshot of scope
            filename=f"{domain}_DC",
            suffix=f"{voltage}_{test_current_label}",
        )

        dmm.get_plot(   # Get Plot of voltage during load //BSC: needs to be paralized with time
            title=f"{domain} DC Output @ {test_current}A",
            y_label=domain,
            suffix=f"{domain} @ {current_label}",
            nominal_value=voltage,
            min_limit=min_voltage,
            max_limit=max_voltage,
            limit=250,
        )

        # ---------------------------
        # AC Measurment
        # ---------------------------

        scope.reset()   # Reset measurments and display of scope

        scope.set_channel(  # Prepare channel 1 to ripple measurment
            channel=1,
            enable=True,
            attenuation=10,
            unit="V",
            label=f"{domain} @ {test_current}A",
            coupling="AC",
            bandwidth_limit="20MHz",
            volts_per_div=calc_scale(voltage*0.075),
            position=0,
        )

        scope.set_channel(  # Set channel 2 of scope
            channel=2,
            enable=True,
            attenuation=10,
            unit="A",
            label=f"{domain} @ {test_current}A",
            coupling="DC",
            bandwidth_limit="20MHz",
            volts_per_div=calc_scale(current),
            position=calc_scale(current)*-3,
        )

        scope.set_measurement(  # Set measurment 1 for channel 1 to max
            position=1,
            channel=1,
            measurement_type="MAX",
        )

        scope.set_measurement(  # Set measurment 2 for channel 1 to min
            position=2,
            channel=1,
            measurement_type="MIN",
        )

        scope.set_measurement(  # Set measurment 3 for channel 1 to RMS
            position=3,
            channel=1,
            measurement_type="PKPK",
        )

        scope.set_measurement(  # Set measurment 4 for channel 2 to RMS
            position=4,
            channel=2,
            measurement_type="RMS",
        )

        scope.set_timebase( # Set timebase
            sec_per_div=0.1e-3,
        )

        scope.set_persistence(  # Set peristance mode
            duration=10,
        )

        scope.run() # Set Scope to run mode

        while True:
            count = scope.get_count(
                position=1
            )

            logger.info(f"Scope Counter at: {count}")

            if count >= 250:
                break

        scope.save_screenshot(  # Create screenshot
            filename=f"{domain}_RIPPLE",
            suffix=f"{voltage}V_{test_current}A",
        )

        eload.load_off() # Disable eload

        if single == True:
            break

    logger.info("Load test completed")