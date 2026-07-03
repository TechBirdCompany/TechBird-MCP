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



def plot_voltage_data(
    datapoints_samples: List[float],
    datapoints_voltages: List[float],
    title: str,
    timestamp: str,
    folder: str,
    nominal_value: float,
    min_limit: float,
    max_limit: float,
) -> Optional[str]:
    """Plot voltage data with specification limits and save to file.
    
    Creates a scatter plot of voltage measurements with specification bands,
    nominal value line, and statistics. Saves plot as PNG file.
    
    Args:
        datapoints_samples: List of time/sample values for x-axis
        datapoints_voltages: List of voltage measurements for y-axis
        title: Plot title
        timestamp: Timestamp string for filename (e.g., "20240115_120530")
        folder: Folder path to save plot file
        nominal_value: Reference nominal voltage value
        min_limit: Specification minimum limit
        max_limit: Specification maximum limit
        
    Returns:
        Path to saved PNG file, or None if no data to plot
    """
    if not datapoints_voltages:
        logger.warning("No data to plot")
        return None

    # Calculate statistics
    v_min = min(datapoints_voltages)
    v_max = max(datapoints_voltages)
    v_avg = sum(datapoints_voltages) / len(datapoints_voltages)

    min_idx = datapoints_voltages.index(v_min)
    max_idx = datapoints_voltages.index(v_max)

    logger.debug(
        f"Plot stats → Min: {v_min:.4f}V, Max: {v_max:.4f}V, Avg: {v_avg:.4f}V"
    )

    # Calculate display range
    spec_half_span = (max_limit - min_limit) / 2
    measurement_span = max(
        abs(v_min - nominal_value),
        abs(v_max - nominal_value),
    )

    max_span = max(spec_half_span, measurement_span)
    display_span = max_span * 1.5

    y_lower = nominal_value - display_span
    y_upper = nominal_value + display_span

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))

    # Specification bands
    ax.axhspan(
        y_lower,
        min_limit,
        color="red",
        alpha=0.15,
        zorder=0,
        label="Out of spec (low)",
    )

    ax.axhspan(
        min_limit,
        max_limit,
        color="green",
        alpha=0.10,
        zorder=0,
        label="Specification range",
    )

    ax.axhspan(
        max_limit,
        y_upper,
        color="red",
        alpha=0.15,
        zorder=0,
        label="Out of spec (high)",
    )

    # Plot data points
    ax.scatter(
        datapoints_samples,
        datapoints_voltages,
        color="darkorange",
        marker="x",
        s=20,
        label=f"Samples ({len(datapoints_voltages)})",
        zorder=3,
    )

    # Reference lines
    ax.axhline(
        min_limit,
        color="green",
        linestyle="--",
        linewidth=2,
        label=f"Spec Min: {min_limit:.4f}V",
    )

    ax.axhline(
        max_limit,
        color="green",
        linestyle="--",
        linewidth=2,
        label=f"Spec Max: {max_limit:.4f}V",
    )

    ax.axhline(
        nominal_value,
        color="blue",
        linewidth=2.5,
        label=f"Nominal: {nominal_value:.4f}V",
    )

    ax.axhline(
        v_avg,
        color="darkorange",
        linestyle=":",
        linewidth=2,
        label=f"Avg: {v_avg:.4f}V",
    )

    # Min/Max markers
    ax.scatter(
        datapoints_samples[min_idx],
        v_min,
        color="black",
        marker="v",
        s=120,
        zorder=5,
        label=f"Measured Min: {v_min:.4f}V",
    )

    ax.scatter(
        datapoints_samples[max_idx],
        v_max,
        color="black",
        marker="^",
        s=120,
        zorder=5,
        label=f"Measured Max: {v_max:.4f}V",
    )

    # Annotations
    ax.annotate(
        f"{v_min:.4f}V",
        (datapoints_samples[min_idx], v_min),
        xytext=(0, -20),
        textcoords="offset points",
        ha="center",
    )

    ax.annotate(
        f"{v_max:.4f}V",
        (datapoints_samples[max_idx], v_max),
        xytext=(0, 10),
        textcoords="offset points",
        ha="center",
    )

    # Formatting
    ax.set_ylim(y_lower, y_upper)
    ax.ticklabel_format(useOffset=False, style="plain", axis="y")

    ax.set_xlabel("Samples")
    ax.set_ylabel("Voltage (V)")
    ax.set_title(title)

    ax.grid(True, linestyle=":", linewidth=0.5)
    ax.legend(loc="best")

    plt.tight_layout()

    # Save file
    safe_title = title.replace(" ", "_")
    filename = f"{timestamp}_{safe_title}_DMM.png"
    path = os.path.join(folder, filename)

    logger.info(f"Saving plot to: {path}")
    plt.savefig(path, dpi=150)
    plt.close()

    return path