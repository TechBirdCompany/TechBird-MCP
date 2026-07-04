from typing import Protocol

class scope(Protocol):

    def identify(self) -> str:
        """
        Identifies the device.

        Returns:
            Result of *IDN?
        """
        ...

    def set_resolution(
        self,
        bit: str = "8Bits",
    ) -> None:
        """
        Configure acquisition resolution.
        """
        ...

    def set_channel(
        self,
        channel: int,
        enable: bool,
        attenuation: float,
        unit: str,
        label: str,
        coupling: str,
        bandwidth_limit: str,
        volts_per_div: float,
        position: float,
    ) -> None:
        """
        Configure a channel.
        """
        ...

    def set_trigger(
        self,
        channel: int,
        mode: str,
        level: float,
    ) -> None:
        """
        Configure trigger settings.
        """
        ...

    def set_timebase(
        self,
        sec_per_div: float,
    ) -> None:
        """
        Configure horizontal scale.
        """
        ...

    def set_persistence(
        self,
        duration: float,
    ) -> None:
        """
        Configure display persistence.
        """
        ...

    def reset(self) -> None:
        """
        Clears persistence,
        statistics and measurements.
        """
        ...

    def set_measurement(
        self,
        position: int,
        channel: int,
        measurement_type: str,
    ) -> None:
        """
        Configure measurement slot.
        """
        ...

    def save_screenshot(
        self,
        filename: str,
        suffix: str,
    ) -> str:
        """
        Save screenshot and return path.
        """
        ...

    def run(self) -> None:
        """
        Starts acquisition.
        """
        ...

    def stop(self) -> None:
        """
        Stops acquisition.
        """
        ...

    def close(self) -> None:
        """
        Close connection.
        """
        ...

    def get_count(
            self,
            position: int
    ):
        """
        Returns the count of said position
        """