from devices.powersupply.peaktech_1885.peaktech_1885 import PEAKTECH_1885

def main():

    ps = PEAKTECH_1885.autoconnect()

    try:
        print("\n=== Connected ===")

        voltage, current = ps.get_value()

        print(
            f"Actual Values: "
            f"{voltage:.2f} V / "
            f"{current:.3f} A"
        )

        ps.lock(True)

        ps.set_values(
            voltage=10.0,
            current=2.0
        )

        ps.power_on_off("ON")

        voltage, current = ps.get_value()

        print(
            f"Output Values: "
            f"{voltage:.2f} V / "
            f"{current:.3f} A"
        )

        input(
            "\nPress ENTER to disable output..."
        )

        ps.power_on_off("OFF")

    finally:

        try:
            ps.lock(False)
        except Exception:
            pass

        ps.close()

        print("\nDisconnected")


if __name__ == "__main__":
    main()