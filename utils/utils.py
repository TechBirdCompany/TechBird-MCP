import math
import os
import matplotlib.pyplot as plt
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

def plot_voltage_data(
    times,
    voltages,
    title,
    timestamp,
    folder,
    nominal_value,
    min_limit,
    max_limit
):

    if not voltages:
        logger.debug("No data to plot!")
        return None

    v_min = min(voltages)
    v_max = max(voltages)
    v_avg = sum(voltages) / len(voltages)

    min_idx = voltages.index(v_min)
    max_idx = voltages.index(v_max)

    logger.debug(
        f"Plot stats → Min: {v_min:.4f}, Max: {v_max:.4f}, Avg: {v_avg:.4f}"
    )


    spec_half_span = (max_limit - min_limit) / 2

    measurement_span = max(
        abs(v_min - nominal_value),
        abs(v_max - nominal_value)
    )

    # größere der beiden Spannweiten verwenden
    max_span = max(spec_half_span, measurement_span)

    # 50% Luft ober- und unterhalb der Spezifikation
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
        times,
        voltages,
        color="darkorange",
        marker="x",
        s=20,
        label=f"Samples ({len(voltages)})",
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

    # Nennwert
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
        times[min_idx],
        v_min,
        color="black",
        marker="v",
        s=120,
        zorder=5,
        label=f"Measured Min: {v_min:.4f} V"
    )

    ax.scatter(
        times[max_idx],
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
        (times[min_idx], v_min),
        xytext=(0, -20),
        textcoords="offset points",
        ha="center"
    )

    ax.annotate(
        f"{v_max:.4f} V",
        (times[max_idx], v_max),
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

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage (V)")
    ax.set_title(title)

    ax.grid(True, linestyle=":", linewidth=0.5)
    ax.legend(loc="best")

    plt.tight_layout()

    safe_title = title.replace(" ", "_")
    filename = f"{timestamp}_{safe_title}_DMM.png"
    path = os.path.join(folder, filename)

    logger.debug(f"Saving plot to: {path}")

    plt.savefig(path, dpi=150)
    plt.close()

    return path