"""OWON XDM1041 Digital Multimeter measurement functions."""

import time
from typing import Tuple, List, Optional

from xdm1000 import XDM1000
from loguru import logger


# =========================================
# Measurement Functions
# =========================================


def measure_voltage(
    duration_s: float,
    sample_interval_s: float = 0.1,
    mode: str = "VDC",
    rate: str = "FAST",
) -> Tuple[List[float], List[float]]:
    """Measure voltage over specified duration.
    
    Continuously samples voltage from XDM1041 DMM and records time/voltage pairs.
    Automatically closes connection when measurement completes.
    
    Args:
        duration_s: Measurement duration in seconds
        sample_interval_s: Delay between samples in seconds (default 0.1s = 10Hz)
        mode: Measurement mode (default "VDC" for DC voltage)
        rate: Measurement rate (default "FAST")
        
    Returns:
        Tuple of (times_list, voltages_list) where:
            - times_list: List of elapsed time values [seconds]
            - voltages_list: List of voltage measurements [volts]
            
    Raises:
        Exception: If DMM connection fails during initialization
    """
    dmm = XDM1000()

    dmm.set_mode(mode)
    dmm.set_rate(rate)
    
    logger.info(
        f"Starting voltage measurement: duration={duration_s}s, "
        f"interval={sample_interval_s}s, mode={mode}, rate={rate}"
    )

    times: List[float] = []
    voltages: List[float] = []

    start = time.perf_counter()

    try:
        while (time.perf_counter() - start) < duration_s:
            try:
                elapsed_time = time.perf_counter() - start
                voltage = dmm.measure()

                times.append(elapsed_time)
                voltages.append(voltage)
                
                logger.debug(f"Sample {len(voltages)}: {voltage:.4f}V at {elapsed_time:.2f}s")

            except Exception as e:
                logger.warning(f"Sample error: {e}")
                continue

            time.sleep(sample_interval_s)
            
    finally:
        dmm.close()
        logger.info(
            f"Measurement complete: collected {len(voltages)} samples"
        )

    return times, voltages

