import time
from loguru import logger
from utils.utils import *
import sys
from datetime import datetime

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
    single: bool = False,
    current_probe_attenuation: float = 10,
    dc_sec_per_div: float = 1e-3,
    ac_sec_per_div: float = 0.1e-3,
    ac_voltage_percentage: float = 0.075,
    advanced: bool = False,
    advanced_dc_sec_per_div: float = 1e-3,
    advanced_ac_sec_per_div: float = 0.1e-3,
    advanced_ac_volts_per_div: float = 0.05,
    use_current_probe: bool = True,
) -> str:
    """
    Measures the domain in idle and with mid and high load

    Args:
        <scope>                         Scope

        <dmm>                           DMM

        <eload>                         E Load

        <voltage>                       Voltage value which is expected

        <max_voltage>                   Max voltage of <voltage>

        <min_voltage>                   Min voltage of <voltage>

        <domain>                        Domain name of <voltage>

        <current>                       Maximum current which should be available
                                        If <single> is true, it will measure only this current

        <samples>                       Number of samples which should be captured

        <single>                        Single measurment or with idle, half and full current

        <current_probe_attenuation>     Attenuation of the current probe

        <dc_sec_per_div>                Timebase of the DC measurment

        <ac_sec_per_div>                Timebase of the AC measurment

        <ac_voltage_percentage>         Percentage factor of voltage used to derive AC scale in normal test

        <advanced>                      Advanced measurment with custom scope settings,
                                        always executed as single measurment

        <advanced_dc_sec_per_div>       Timebase of the DC measurment in advanced mode

        <advanced_ac_sec_per_div>       Timebase of the AC measurment in advanced mode

        <advanced_ac_volts_per_div>     Volts per division of the AC measurment in advanced mode

        <use_current_probe>             Whether to enable current probe measurement on channel 2
    """

    created_files = []

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    if advanced:   # Advanced measurments are always single measurments
        single = True
        file_tag = "ADVANCED_"
        use_dc_sec_per_div = advanced_dc_sec_per_div
        use_ac_sec_per_div = advanced_ac_sec_per_div
        ac_scale = advanced_ac_volts_per_div
    else:
        file_tag = ""
        use_dc_sec_per_div = dc_sec_per_div
        use_ac_sec_per_div = ac_sec_per_div
        ac_scale = calc_scale(voltage * ac_voltage_percentage)

    logger.info(
        f"Starting {'advanced ' if advanced else ''}load test: "
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
            label=f"{domain}@{test_current}A",
            coupling="DC",
            bandwidth_limit="20MHz",
            volts_per_div=calc_scale(voltage),
            position=calc_scale(voltage)*-2,
        )

        if use_current_probe:
            scope.set_channel(  # Set channel 2 of scope
                channel=2,
                enable="ON",
                attenuation=current_probe_attenuation,
                unit="A",
                label=f"{domain}@{test_current}A",
                coupling="DC",
                bandwidth_limit="20MHz",
                volts_per_div=calc_scale(current),
                position=calc_scale(current)*-3,
            )
        else:
            scope.set_channel(  # Disable channel 2
                channel=2,
                enable="OFF",
            )

        scope.set_trigger(  # Set trigger mode
            channel=1,
            mode="",
            level=voltage / 2,
        )

        scope.set_timebase( # Set Timebase
            sec_per_div=use_dc_sec_per_div,
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

        if use_current_probe:
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

            if count != last_count: # Print only when sample increases
                sys.stdout.write(
                    f"\rMeasurement count: {count}/{samples}"
                )
                sys.stdout.flush()
                last_count = count

            if count >= samples:
                print()
                break

            time.sleep(0.1)

        scope.stop() # Set scope in stop mode

        file = scope.save_screenshot(  # Get screenshot of scope
            filename=f"{domain}@{str(test_current)}A_{file_tag}DC_SCOPE_{timestamp}",
        )

        created_files.append(file)

        file = dmm.get_plot(
            title=f"{domain} DC Output @ {test_current}A",
            y_label=domain,
            filename=f"{domain}@{str(test_current)}A_{file_tag}DC_DMM_{timestamp}",
            nominal_value=voltage,
            min_limit=min_voltage,
            max_limit=max_voltage,
            limit=samples,
        )

        created_files.append(file)

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
            volts_per_div=ac_scale,
            position=0,
        )

        if use_current_probe:
            scope.set_channel(  # Set channel 2 of scope
                channel=2,
                enable="ON",
                attenuation=current_probe_attenuation,
                unit="A",
                label=f"{domain} @ {test_current}A",
                coupling="DC",
                bandwidth_limit="20MHz",
                volts_per_div=calc_scale(current),
                position=calc_scale(current)*-3,
            )
        else:
            scope.set_channel(  # Disable channel 2
                channel=2,
                enable="OFF",
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

        if use_current_probe:
            scope.set_measurement(  # Set measurment 4 for channel 2 to RMS
                position=4,
                channel=2,
                measurement_type="RMS",
            )

        scope.set_timebase( # Set timebase
            sec_per_div=use_ac_sec_per_div,
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

            if count != last_count: # Print only when count increases
                sys.stdout.write(
                    f"\rMeasurement count: {count}/{samples}"
                )
                sys.stdout.flush()
                last_count = count

            if count >= samples:
                print()
                break

            time.sleep(0.1)

        file = scope.save_screenshot(  # Create screenshot
            filename=f"{domain}@{str(test_current)}A_{file_tag}AC_SCOPE_{timestamp}",
        )

        created_files.append(file)

        eload.load_off() # Disable eload

        if single == True:
            break

    eload.close()

    logger.info("Load test completed")

    return created_files