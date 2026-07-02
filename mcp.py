from loguru import logger

#from config.testcases import load_test

from devices.dmm.rigol_dmm800.rigol_dmm800 import DMM800


def main():

    resource = "TCPIP0::192.168.1.38::INSTR"

    dmm = DMM800(resource)

    try:

        plot_path = dmm.measure_and_plot_voltage(
            voltage=0.5,
            voltage_nom=0,
            voltage_min=-0.5,
            voltage_max=0.5,
            min_samples=250,
            mode="FAST",
            folder="measurements",
            filename="GND",
        )

        print(f"Plot saved: {plot_path}")

    finally:
        dmm.close()


if __name__ == "__main__":
    main()
