import sys
from loguru import logger

from config.testcases import load_test


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
