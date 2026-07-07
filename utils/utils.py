"""Utility functions for measurement processing and plotting."""

import math
import os
from typing import Optional, List
import re
import matplotlib.pyplot as plt
from loguru import logger


def to_float(value: str) -> float:
    """Extract and convert numeric value from string.
    
    Searches for the first numeric pattern (integer or float) in the input
    string and converts it to float.
    
    Args:
        value: String containing a numeric value (e.g., "3.14V", "-5.5")
        
    Returns:
        Extracted number as float
        
    Raises:
        IndexError: If no numeric pattern found in string
        ValueError: If extracted value cannot be converted to float
    """
    number = re.findall(r"[-+]?\d*\.?\d+", value)[0]
    return float(number)


def round_125(value: float) -> float:
    """Round value to nearest "nice" number (1, 2, 5, 10, etc).
    
    Useful for setting oscilloscope or load scales to human-friendly values.
    
    Args:
        value: Numeric value to round
        
    Returns:
        Rounded value using 1-2-5 algorithm
    """
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


def calc_scale(value: float) -> float:
    """Calculate display scale for a measurement value.
    
    Computes the appropriate scale for displaying a value using 1-2-5
    rounding algorithm. Typically used for setting voltage/current ranges.
    
    Args:
        value: Measurement value to scale
        
    Returns:
        Calculated scale value
    """
    raw = abs(value) / 4
    return round_125(raw)


def get_folder(folder: Optional[str] = None) -> str:
    """Get or create measurements folder path.
    
    Returns the specified folder path, or defaults to project/measurements
    if none provided.
    
    Args:
        folder: Optional folder path. If None, uses default measurements folder.
        
    Returns:
        Absolute path to folder (directory is created if needed)
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    if folder is None:
        folder = os.path.join(project_root, "measurements")

    return folder



def plot_data(
    x_data,
    y_data,
    title: str,
    y_label: str,
    suffix: str = "",
    unit: str = "",
    nominal_value: float = 0.0,
    min_limit: float = 0.0,
    max_limit: float = 0.0,
):
    """
    Plot measurement data with specification limits and save to file.

    Args:
        x_data: X-axis values (usually sample numbers)
        y_data: Measured values
        title: Plot title
        y_label: Y-axis label
        suffix: Optional filename prefix/suffix
        unit: Measurement unit (V, A, W, Ω, ...)
        nominal_value: Target value
        min_limit: Lower specification limit
        max_limit: Upper specification limit

    Returns:
        Path to saved PNG file or None
    """

    if not y_data:
        logger.warning("No data to plot")
        return None

    value_min = min(y_data)
    value_max = max(y_data)
    value_avg = sum(y_data) / len(y_data)

    min_idx = y_data.index(value_min)
    max_idx = y_data.index(value_max)

    logger.debug(
        f"Plot stats → "
        f"Min: {value_min:.4f}{unit}, "
        f"Max: {value_max:.4f}{unit}, "
        f"Avg: {value_avg:.4f}{unit}"
    )

    spec_half_span = abs(max_limit - min_limit) / 2

    measurement_span = max(
        abs(value_min - nominal_value),
        abs(value_max - nominal_value),
    )

    max_span = max(spec_half_span, measurement_span)

    if max_span == 0:
        max_span = 1

    display_span = max_span * 1.5

    y_lower = nominal_value - display_span
    y_upper = nominal_value + display_span

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.axhspan(
        y_lower,
        min_limit,
        facecolor="red",
        alpha=0.08,
        hatch="xx",
        edgecolor="red",
        zorder=0,
    )

    ax.axhspan(
        min_limit,
        max_limit,
        color="green",
        alpha=0.10,
        zorder=0,
    )

    ax.axhspan(
        max_limit,
        y_upper,
        facecolor="red",
        alpha=0.08,
        hatch="xx",
        edgecolor="red",
        zorder=0,
    )

    ax.scatter(
        x_data,
        y_data,
        color="darkorange",
        marker="x",
        s=20,
        label=f"Samples ({len(y_data)})",
        zorder=3,
    )

    ax.axhline(
        min_limit,
        color="green",
        linestyle="--",
        linewidth=2,
        label=f"Spec Min: {min_limit:.4f}{unit}",
    )

    ax.axhline(
        max_limit,
        color="green",
        linestyle="--",
        linewidth=2,
        label=f"Spec Max: {max_limit:.4f}{unit}",
    )

    ax.axhline(
        nominal_value,
        color="blue",
        linewidth=2.5,
        label=f"Nominal: {nominal_value:.4f}{unit}",
    )

    ax.axhline(
        value_avg,
        color="darkorange",
        linestyle=":",
        linewidth=2,
        label=f"Avg: {value_avg:.4f}{unit}",
    )

    ax.scatter(
        x_data[min_idx],
        value_min,
        color="black",
        marker="v",
        s=120,
        zorder=5,
        label=f"Measured Min: {value_min:.4f}{unit}",
    )

    ax.scatter(
        x_data[max_idx],
        value_max,
        color="black",
        marker="^",
        s=120,
        zorder=5,
        label=f"Measured Max: {value_max:.4f}{unit}",
    )

    ax.annotate(
        f"{value_min:.4f}{unit}",
        (x_data[min_idx], value_min),
        xytext=(0, -20),
        textcoords="offset points",
        ha="center",
    )

    ax.annotate(
        f"{value_max:.4f}{unit}",
        (x_data[max_idx], value_max),
        xytext=(0, 10),
        textcoords="offset points",
        ha="center",
    )

    ax.set_ylim(y_lower, y_upper)

    ax.ticklabel_format(
        useOffset=False,
        style="plain",
        axis="y",
    )

    ax.set_xlabel("Samples")

    if unit:
        ax.set_ylabel(f"{y_label} ({unit})")
    else:
        ax.set_ylabel(y_label)

    ax.set_title(title)

    ax.grid(
        True,
        linestyle=":",
        linewidth=0.5,
    )

    ax.legend(loc="best")

    plt.tight_layout()

    output_dir = get_folder()
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{title}_{suffix}".strip("_")
    filename = filename.replace(" ", "_")

    path = os.path.join(
        output_dir,
        f"{filename}.png",
    )

    logger.info(f"Saving plot to: {path}")

    plt.savefig(
        path,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close(fig)

    return path