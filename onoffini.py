from argparse import ArgumentParser, RawTextHelpFormatter
from typing import Literal

from loguru import logger

from devices.powersupply.powersupply_protocol import powersupply
from devices.powersupply.peaktech_1885.peaktech_1885 import PEAKTECH_1885


def onoffini(
    ps: powersupply,
    voltage: float,
    current: float,
    state: Literal["ON", "OFF"],
) -> None:
    """
    Control the power supply output.

    If state is ON:
        - Set voltage and current
        - Enable output

    If state is OFF:
        - Disable output

    Args:
        ps: Power supply instance.
        voltage: Output voltage in volts.
        current: Current limit in amperes.
        state: Desired output state ("ON" or "OFF").
    """

    logger.info(
        f"Requested settings: Voltage={voltage} V, Current={current} A, State={state}"
    )

    if state == "OFF":
        logger.info("Turning power supply output OFF")
        ps.power_on_off("OFF")
        return

    logger.info(f"Setting voltage to {voltage} V")
    logger.info(f"Setting current limit to {current} A")

    ps.set_values(
        voltage=voltage,
        current=current,
    )

    logger.info("Turning power supply output ON")
    ps.power_on_off("ON")


def main() -> None:

    parser = ArgumentParser(
        prog="onoffini",
        description="Control a PeakTech 1885 power supply from the command line.",
        epilog=(
            "Examples:\n"
            "  python onoffini.py --voltage 24 --current 5 --state ON\n"
            "  python onoffini.py --voltage 24 --current 5 --state OFF"
        ),
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument(
        "--voltage",
        type=float,
        required=True,
        help="Output voltage in volts.",
    )

    parser.add_argument(
        "--current",
        type=float,
        required=True,
        help="Current limit in amperes.",
    )

    parser.add_argument(
        "--state",
        choices=["ON", "OFF"],
        required=True,
        help="Output state of the power supply.",
    )

    args = parser.parse_args()

    try:
        logger.info("Connecting to PeakTech 1885 power supply...")

        ps = PEAKTECH_1885.auto_connect()

        logger.success("Connection established")

        onoffini(
            ps=ps,
            voltage=args.voltage,
            current=args.current,
            state=args.state,
        )

        logger.success("Command executed successfully")

    except Exception as exc:
        logger.exception(f"Operation failed: {exc}")


if __name__ == "__main__":
    main()