from typing import Optional, Literal
from loguru import logger
from datetime import datetime
import time

from devices.dmm.dmm_protocol import dmm
from devices.scope.scope_protocol import scope

def get_screenshot_scope(
        device:scope,
        filename: str = "TEMP",
        label_ch1: Optional[str] = None,
        label_ch2: Optional[str] = None,
        label_ch3: Optional[str] = None,
        label_ch4: Optional[str] = None
) -> None:
    """
    Gets screenshot of the given scope

    Args:
        <device>         Scope device
        
        <filename>      Filename

        <label_ch1>     Optional label for CH1

        <label_ch2>     Optional label for CH2

        <label_ch3>     Optional label for CH3

        <label_ch4>     Optional label for CH4
    """
    
    labels = [label_ch1, label_ch2, label_ch3, label_ch4]

    for i in range(len(labels)):
        device.set_label(
            channel = i+1,
            label = labels[i]
        )

    device.save_screenshot(
        filename=f"{filename}_{datetime.now().strftime("%Y%m%d_%H%M%S")}"
    )

def get_screenshot_dmm(
       device:dmm,
       filename: str = "TEMP"
) -> None:
    """
    Gets screenshot of dmm, if supported

    Args:
        <device>    DMM device

        <filename>  Filename   
    """

    logger.warning(f"Function not implemented")

def get_plot_dmm(
        device:dmm,
        filename: str = "TEMP",
        samples: int = 200,
        title: str = "",
        y_label: str = "",
        nominal_value: float = 0.0,
        min_limit: float = 0.0,
        max_limit: float = 0.0,
) -> None:
    """
    Get plot of DMM for the desired samples, if supported

    Args:
        <device>            DMM device

        <filename>          Filename 

        <samples>           Samples which need to be captured

        <title>             Title of the plot

        <y_label>           y label...

        <nominal_value>     Nominal value, will be displayed as center line

        <min_limit>         Minimal limit

        <max_limit>         Maximal limit
    """

    device.get_plot(
        filename=f"{filename}_{datetime.now().strftime("%Y%m%d_%H%M%S")}",
        title=title,
        y_label=y_label,
        nominal_value=nominal_value,
        min_limit=min_limit,
        max_limit=max_limit,
        limit=samples
    )