import math
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from loguru import logger

def round_125(value):
    exponent = math.floor(math.log10(value))
    base = value / (10 ** exponent)

    if base <= 1:
        nice = 1
    elif base <= 2:
        nice = 2
    elif base <= 5:
        nice = 5
    else:
        nice = 10

    return nice * (10 ** exponent)

def calc_scale(value):
    raw = abs(value) / 4
    return round_125(raw)

def get_folder(folder=None):
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )

    if folder is None:
        folder = os.path.join(project_root, "measurements")

    return folder

def plot_voltage_data(times, voltages, title, timestamp, folder):

    if not voltages:
        logger.debug("No data to plot!")
        return None

    v_min = min(voltages)
    v_max = max(voltages)
    v_avg = sum(voltages) / len(voltages)

    logger.debug(f"Plot stats → Min: {v_min:.4f}, Max: {v_max:.4f}, Avg: {v_avg:.4f}")

    plt.figure()


    plt.scatter(
        times,
        voltages,
        color="darkorange",
        s=10,
        marker="x",
        label=f"Voltage ({len(voltages)} samples)"
    )


    plt.axhline(v_min, color="black", linestyle="--", label=f"Min: {v_min:.4f} V")
    plt.axhline(v_max, color="black", linestyle="--", label=f"Max: {v_max:.4f} V")

    #  Average
    plt.axhline(v_avg, color="blue", linestyle="-", label=f"Avg: {v_avg:.4f} V")

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