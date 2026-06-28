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

        time.sleep(0.01)

    dmm.close()
    return times, voltages


# ============================================
# Plot (main thread)
# ============================================

def plot_voltage_data(times, voltages, title, timestamp, folder):

    if not voltages:
        logger.debug("No data to plot!")
        return None

    v_min = min(voltages)
    v_max = max(voltages)
    v_avg = sum(voltages) / len(voltages)

    logger.debug(f"Plot stats → Min: {v_min:.6f}, Max: {v_max:.6f}, Avg: {v_avg:.6f}")

    plt.figure()


    plt.scatter(
        times,
        voltages,
        color="darkorange",
        s=10,
        marker="x",
        label=f"Voltage ({len(voltages)} samples)"
    )


    plt.axhline(v_min, color="black", linestyle="--", label=f"Min: {v_min:.5f} V")
    plt.axhline(v_max, color="black", linestyle="--", label=f"Max: {v_max:.5f} V")

    #  Average
    plt.axhline(v_avg, color="blue", linestyle="-", label=f"Avg: {v_avg:.5f} V")

    plt.ticklabel_format(useOffset=False, style='plain', axis='y')

    span = v_max - v_min
    margin = span * 0.3 if span > 0 else 0.01

    plt.ylim(
        v_avg - (span / 2 + margin),
        v_avg + (span / 2 + margin)
    )

    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.title(title)

    plt.legend()
    plt.grid(True, linestyle=":", linewidth=0.5)
    plt.tight_layout()


    safe_title = title.replace(" ", "_")
    filename = f"{timestamp}_{safe_title}_DMM.png"
    path = os.path.join(folder, filename)

    logger.debug(f"Saving plot to: {path}")

    plt.savefig(path)
    plt.close()

    return path