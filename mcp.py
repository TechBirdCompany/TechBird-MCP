import sys
from loguru import logger

from config.testcases import load_test

from dmm800 import DMM800


def main():

    resource = "TCPIP0::192.168.1.100::INSTR"
    # oder:
    # resource = "USB0::0xF4EC::0xEE38::XXXXXXXX::INSTR"

    dmm = DMM800(resource)

    try:

        print("Creating statistics screenshot...")

        dmm.measure_with_statistics_and_screenshot(
            voltage=10,
            min_samples=100,
            mode="MEDIUM",
            folder="screenshots",
            filename="10V_Reference"
        )

        print("Creating voltage plot...")

        plot_path = dmm.measure_and_plot_voltage(
            voltage=10,
            min_samples=100,
            mode="MEDIUM",
            folder="plots",
            filename="10V_Reference"
        )

        print(f"Plot saved: {plot_path}")

    finally:
        dmm.close()


if __name__ == "__main__":
    main()

'''
def setup_logging():
    """
    Einheitliches Logging für Konsole
    """

    logger.remove()

    logger.add(
        sys.stdout,
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}"
    )


def main():

    setup_logging()

    logger.info("=== START TEST RUN ===")

    # Test parameters
    load_test(
        label="VCC_5V0",
        voltage=5.0,
        current=0.5,
        timebaseDC=0.01,
        timebaseAC=0.001,
        single=False
    )

    logger.info("=== TEST RUN FINISHED ===")


if __name__ == "__main__":
    main()
'''