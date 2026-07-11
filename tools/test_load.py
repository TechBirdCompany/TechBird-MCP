import time
from loguru import logger
from utils.utils import *
import sys

from devices.dmm.dmm_protocol import dmm
from devices.scope.scope_protocol import scope
from devices.electronic_load.eload_protocol import eload

def test_load(
    scope: scope,
    dmm: dmm,
    eload: eload,
    voltage: float,
    max_voltage: float,
    min_voltage: float,
    domain: str,
    current: float,
    samples: int = 200,
    single: bool = False
):
    """
    Measures the domain in idle and with mid and high load

    Args:
        <scope>             Scope

        <dmm>               DMM

        <eload>             E Load

        <voltage>           Voltage value which is expected

        <max_voltage>       Max voltage of <voltage>

        <min_voltage>       Min voltage of <voltage>

        <domain>            Domain name of <voltage>

        <current>           Maximum current which should be available
                            If <single> is true, it will measure only this current

        <samples>           Number of samples which should be captured

        <single>            Single measurment or with idle, half and full current
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
            speed="FAST",
        )

        scope.stop()    # Stop scope

        scope.reset()   # Reset measurments and display of scope    

        scope.set_persistence(0) # Remove persistance mode

        scope.set_resolution(   # Set resolution to 10 Bit for 20 MHz
            bit="10Bits"
        )

        scope.set_channel(  # Set channel 1 of scope
            channel=1,
            enable="ON",
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
            enable="ON",
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

        last_count = None

        while True:
            count = scope.get_count(position=1)

            if count != last_count:
                sys.stdout.write(
                    f"\rMeasurement count: {count}/{samples}"
                )
                sys.stdout.flush()
                last_count = count

            if count >= 250:
                print()  # Zeilenumbruch
                break

            time.sleep(0.1)

        scope.stop() # Set scope in stop mode

        scope.save_screenshot(  # Get screenshot of scope
            filename=f"{domain}_DC",
        )

        dmm.get_plot(   # Get Plot of voltage during load //BSC: needs to be paralized with time
            title=f"{domain} DC Output @ {test_current}A",
            y_label=domain,
            filename=f"{domain} @ {current_label}",
            nominal_value=voltage,
            min_limit=min_voltage,
            max_limit=max_voltage,
            limit=samples,
        )

        # ---------------------------
        # AC Measurment
        # ---------------------------

        scope.reset()   # Reset measurments and display of scope

        scope.set_channel(  # Prepare channel 1 to ripple measurment
            channel=1,
            enable="ON",
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
            enable="ON",
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
            duration=-1,
        )

        time.sleep(5)

        scope.persistence_clear() # Clear persistance traces

        scope.run() # Set Scope to run mode

        last_count = None

        while True:
            count = scope.get_count(position=1)

            if count != last_count:
                sys.stdout.write(
                    f"\rMeasurement count: {count}/{samples}"
                )
                sys.stdout.flush()
                last_count = count

            if count >= 250:
                print()  # Zeilenumbruch
                break

            time.sleep(0.1)

        scope.save_screenshot(  # Create screenshot
            filename=f"{domain}_RIPPLE",
        )

        eload.load_off() # Disable eload

        if single == True:
            break

    logger.info("Load test completed")