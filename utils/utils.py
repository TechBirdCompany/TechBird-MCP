import math
import os
import matplotlib.pyplot as plt
from loguru import logger



def round_125(value):
    '''
    Rounds a value to the nearest "nice" number to adjust for scope settings.
    '''

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
    '''
    Calculates the scale for a given value, rounding it to the nearest "nice" number.
    '''
    
    raw = abs(value) / 4
    return round_125(raw)

def get_folder(folder=None):
    '''
    Returns the path to the named folder, creating it if it doesn't exist.
    '''
    
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )

    if folder is None:
        folder = os.path.join(project_root, "measurements")

    return folder

def plot_voltage_data(
    datapoints_samples,
    datapoints_voltages,
    title,
    timestamp,
    folder,
    nominal_value,
    min_limit,
    max_limit
):
    '''
    Plots the voltage data with the specified parameters and saves the plot to a file.

    <data_samples>      List of time values corresponding to the voltage measurements
    <data_voltages>     List of voltage measurements
    <title>             Title of the plot
    <timestamp>         Timestamp to include in the filename for unification
    <folder>            Folder to save the plot in
    <nominal_value>     Nominal voltage value for reference
    <min_limit>         Minimum specification limit for the voltage
    <max_limit>         Maximum specification limit for the voltage
    '''

    if not datapoints_voltages:
        logger.debug("No data to plot!")
        return None

    v_min = min(datapoints_voltages)
    v_max = max(datapoints_voltages)
    v_avg = sum(datapoints_voltages) / len(datapoints_voltages)

    min_idx = datapoints_voltages.index(v_min)
    max_idx = datapoints_voltages.index(v_max)

    logger.debug(
        f"Plot stats → Min: {v_min:.4f}, Max: {v_max:.4f}, Avg: {v_avg:.4f}"
    )

    spec_half_span = (max_limit - min_limit) / 2

    measurement_span = max(
        abs(v_min - nominal_value),
        abs(v_max - nominal_value)
    )

    max_span = max(spec_half_span, measurement_span)

    display_span = max_span * 1.5

    y_lower = nominal_value - display_span
    y_upper = nominal_value + display_span

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.axhspan(
        y_lower,
        min_limit,
        color="red",
        alpha=0.15,
        zorder=0
    )

    ax.axhspan(
        min_limit,
        max_limit,
        color="green",
        alpha=0.10,
        zorder=0
    )

    ax.axhspan(
        max_limit,
        y_upper,
        color="red",
        alpha=0.15,
        zorder=0
    )

    ax.scatter(
        datapoints_samples,
        datapoints_voltages,
        color="darkorange",
        marker="x",
        s=20,
        label=f"Samples ({len(datapoints_voltages)})",
        zorder=3
    )
    ax.axhline(
        min_limit,
        color="green",
        linestyle="--",
        linewidth=2,
        label=f"Spec Min: {min_limit:.4f} V"
    )

    ax.axhline(
        max_limit,
        color="green",
        linestyle="--",
        linewidth=2,
        label=f"Spec Max: {max_limit:.4f} V"
    )

    ax.axhline(
        nominal_value,
        color="blue",
        linewidth=2.5,
        label=f"Nominal: {nominal_value:.4f} V"
    )

    ax.axhline(
        v_avg,
        color="darkorange",
        linestyle=":",
        linewidth=2,
        label=f"Avg: {v_avg:.4f} V"
    )

    ax.scatter(
        datapoints_samples[min_idx],
        v_min,
        color="black",
        marker="v",
        s=120,
        zorder=5,
        label=f"Measured Min: {v_min:.4f} V"
    )

    ax.scatter(
        datapoints_samples[max_idx],
        v_max,
        color="black",
        marker="^",
        s=120,
        zorder=5,
        label=f"Measured Max: {v_max:.4f} V"
    )

    # Werte beschriften
    ax.annotate(
        f"{v_min:.4f} V",
        (datapoints_samples[min_idx], v_min),
        xytext=(0, -20),
        textcoords="offset points",
        ha="center"
    )

    ax.annotate(
        f"{v_max:.4f} V",
        (datapoints_samples[max_idx], v_max),
        xytext=(0, 10),
        textcoords="offset points",
        ha="center"
    )

    ax.set_ylim(y_lower, y_upper)

    ax.ticklabel_format(
        useOffset=False,
        style="plain",
        axis="y"
    )

    ax.set_xlabel("Samples")
    ax.set_ylabel("Voltage (V)")
    ax.set_title(title)

    ax.grid(True, linestyle=":", linewidth=0.5)
    ax.legend(loc="best")

    plt.tight_layout()

    safe_title = title.replace(" ", "_")
    filename = f"{timestamp}_{safe_title}_DMM.png"
    path = os.path.join(folder, filename)

    logger.info(f"Saving plot to: {path}")

    plt.savefig(path, dpi=150)
    plt.close()

    return path